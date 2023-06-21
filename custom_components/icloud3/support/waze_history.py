from ..global_variables     import GlobalVariables as Gb
from ..const                import (EVLOG_NOTICE, EVLOG_ALERT, CRLF_DOT, CRLF, RARROW2, DATETIME_ZERO,
                                    CONF_TRACK_FROM_ZONES
                                    )
from ..helpers.messaging    import (broadcast_info_msg,
                                    post_event, post_internal_error, post_monitor_msg,
                                    log_info_msg, log_error_msg, log_exception,
                                    _trace, _traceha, )
from ..helpers.time_util    import (datetime_now, secs_to_time_str, mins_to_time_str, )
from ..helpers.dist_util    import (mi_to_km, calc_distance_km, format_dist_km,)
from ..support.waze_route_calc_ic3 import WRCError

import homeassistant.util.dt as dt_util

import traceback
import time
import sqlite3
from sqlite3 import Error


#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   ZONES TABLE
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
ZON_ID   = 0
ZON_ZONE = 1
ZON_ENTITY_ID = 2
ZON_LAT  = 3
ZON_LONG = 4
ZON_STATUS = 5          # 0-Useable, 1=Moved and needs Recalc Done
ZON_UPDATED = 6
ZON_RECALC_RECD = 7     # Last recd recalculated for restart (0-beginning)

# Create the zones table
CREATE_ZONES_TABLE = '''
    CREATE TABLE IF NOT EXISTS zones (
        zone_id         integer PRIMARY KEY,
        zone            text NOT NULL,
        entity_id       text,
        latitude        real,
        longitude       real,
        status          integer default (0),
        updated         text default ('00/00/00 00:00:00'),
        recalc_recd     integer default (0)
    );'''

# Add zone record - [zone, latitude, longitude]
ADD_ZONE_RECORD = '''
    INSERT INTO zones(
        zone, entity_id, latitude, longitude, status, updated, recalc_recd)
    VALUES(?,?,?,?,?,?,?)
    '''

# Update zones table, zone_data - [zone, latitude, longitude, status, updated, recald_recd, id]
UPDATE_ZONES_TABLE_ZONE_NAME = '''
    UPDATE zones
        SET zone = ?
        WHERE zone_id = ?
    '''

UPDATE_ZONES_TABLE = '''
    UPDATE zones
        SET latitude = ?,
            longitude = ?,
            status = ?,
            updated = ?,
            recalc_recd = ?
        WHERE zone_id = ?
    '''

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   LOCATIONS TABLE
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
LOC_ID           = 0
LOC_ZONE_ID      = 1
LOC_LAT_LONG_KEY = 2
LOC_LAT          = 3
LOC_LONG         = 4
LOC_TIME         = 5
LOC_DIST         = 6
LOC_ADDED        = 7
LOC_LAST_USED    = 8
LOC_USAGE_CNT    = 9

# Create the locations table
CREATE_LOCATIONS_TABLE = '''
    CREATE TABLE IF NOT EXISTS locations (
        loc_id       INTEGER PRIMARY KEY,
        zone_id      INTEGER DEFAULT (0),
        lat_long_key TEXT    NOT NULL
                             DEFAULT ('0:0'),
        latitude     DECIMAL (8, 4) DEFAULT (0.0),
        longitude    DECIMAL (8, 4) DEFAULT (0.0),
        time         DECIMAL (6, 2) DEFAULT (0),
        distance     DECIMAL (8, 2) DEFAULT (0),
        added        TEXT,
        last_used    TEXT,
        usage_cnt    INTEGER DEFAULT (1)
    );'''

GET_LOCATIONS_TABLE_RECD_COUNT = '''
    SELECT count(*) FROM locations;
    '''

# Add location record - [zone_id, lat_long_key, distance, travel_time, added,
#                        last_used, usage_cnt]
ADD_LOCATION_RECORD = '''
    INSERT INTO locations(
        zone_id, lat_long_key, latitude, longitude,
        time, distance, added, last_used, usage_cnt)
    VALUES(?,?,?,?,?,?,?,?,?)
    '''

# Update locations table, location_data [last_used, usage_cnt, id]
UPDATE_LOCATION_USED = '''
    UPDATE locations
        SET last_used = ? ,
            usage_cnt = ?
        WHERE loc_id = ?
    '''

# DB Maintenance - Update locations table time & distance
UPDATE_LOCATION_TIME_DISTANCE = '''
    UPDATE locations
        SET time = ? ,
            distance = ?
        WHERE loc_id = ?
    '''

# DB Maintenance - Select duplicate zone_id and lat_long_key records
DUPLICATE_LOCATION_RECDS_SELECT = '''
    SELECT * FROM locations
        WHERE EXISTS (
            SELECT 1 FROM locations loc2
                WHERE locations.zone_id = loc2.zone_id
                    AND locations.lat_long_key = loc2.lat_long_key
                    AND locations.rowid > loc2.rowid
        );
    '''

# DB Maintenance - Delete duplicate zone_id and lat_long_key records
DUPLICATE_LOCATION_RECDS_DELETE = '''
    DELETE FROM locations
        WHERE EXISTS (
            SELECT 1 FROM locations loc2
                WHERE locations.zone_id = loc2.zone_id
                    AND locations.lat_long_key = loc2.lat_long_key
                    AND locations.rowid > loc2.rowid
        );
    '''

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class WazeRouteHistory(object):
    def __init__(self, wazehist_used, max_distance, track_direction):

        # Flags to control db maintenance
        self.wazehist_recalculate_time_dist_abort_flag = False
        self.wazehist_recalculate_time_dist_running_flag = False

        self.use_wazehist_flag = wazehist_used
        self.max_distance = mi_to_km(max_distance)
        self.track_direction_north_south_flag = \
                track_direction in ['north-south', 'north_south']
        self.track_latitude  = 0      # used to update the icloud3_wazeist_track_gps sensor
        self.track_longitude = 0

        self.last_lat_long_key = ''   # Last lat:long key read
        self.last_location_recds    = []   # List of the last recds retrieved for the lat:long

        self.connection = None
        self.cursor     = None
        wazehist_database = Gb.wazehist_database_filename
        post_event(Gb.devicename, f"Waze History Database > {wazehist_database}")

        if self.use_wazehist_flag and self.connection is None:
            self.open_waze_history_database(wazehist_database)

#--------------------------------------------------------------------
    @property
    def is_historydb_USED(self):
        return self.use_wazehist_flag

#--------------------------------------------------------------------
    def open_waze_history_database(self, wazehist_database):
        """
        Create a database connection to the SQLite database
            specified by db_file

        wazehist_database: The filename of the waze history sqlite3 database

        Note: This sets the sql connection and cursor fields if the database
                opened successfully
        """

        try:
            self.connection = sqlite3.connect(wazehist_database, check_same_thread=False)
            self.cursor     = self.connection.cursor()

            self._sql(CREATE_ZONES_TABLE)
            self._sql(CREATE_LOCATIONS_TABLE)

            self.compress_wazehist_database()

        except:
            post_internal_error(traceback.format_exc)
            self.connection = None
            self.cursor = None

        return

#--------------------------------------------------------------------
    def close_waze_history_database(self):
        '''
        Close the Waze History Database
        '''
        if self.connection is None:
            return

        try:
            self.connection.commit()
            self.connection.close()

        except:
            pass

        self.connection = None
        self.cursor = None

#--------------------------------------------------------------------
    def _sql(self, sql):
        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except:
            post_internal_error(traceback.format_exc)

#--------------------------------------------------------------------
    def _sql_data(self, sql, data):
        self.cursor.execute(sql, data)
        self.connection.commit()

#--------------------------------------------------------------------
    def _add_record(self, sql, data):
        '''
        General function that adds a record to a table
        :param      sql     - sql statement that will add the data
                    data    - list containing the data to be added that matches the sql stmt
        :return     rowid   - id of the added row
        '''
        try:
            self.cursor.execute(sql, data)
            self.connection.commit()

            return self.cursor.lastrowid

        except Exception as err:
            log_exception(err)
            post_internal_error(traceback.format_exc)

#--------------------------------------------------------------------
    def _update_record(self, sql, data):
        '''
        Update a record in a table
        :param      sql     - sql statement that will update the data
                    data    - list containing the data to be added that matches the sql stmt
        '''
        try:
            self.cursor.execute(sql, data)
            self.connection.commit()
            return True

        except:
            error_msg = f"Error updating Waze History Database, {sql}, {data}"
            log_error_msg(error_msg)
            # post_internal_error(traceback.format_exc)
            return False
#--------------------------------------------------------------------
    def _delete_record(self, table, criteria=''):
        '''
        Select a record from a table
        :param      sql     - sql statement that will select the record
                    criteria- sql select stmt WHERE clause
        '''
        sql = (f"DELETE FROM {table}")
        if criteria:
            sql += (f" WHERE {criteria}")

        self.cursor.execute(sql)
        self.connection.commit()

#--------------------------------------------------------------------
    def _get_record(self, table, criteria=''):
        '''
        Select a record from a table
        :param      sql     - sql statement that will select the record
                    criteria- sql select stmt WHERE clause
                                ("lat_long_key='27.3023:-80.9738'", "location_id=342")
        '''
        try:

            sql = (f"SELECT * FROM {table}")
            if criteria:
                sql += (f" WHERE {criteria}")


            self.cursor.execute(sql)
            record = self.cursor.fetchone()

            try:
                if table == 'locations':
                    monitor_msg = ( f"Zone-{record[LOC_ZONE_ID]}, "
                                    f"Time-{record[LOC_TIME]}, "
                                    f"Dist-{record[LOC_DIST]}")
                elif table == 'zones':
                    monitor_msg = ( f"Zone-{record[ZON_ID]} "
                                    f"({record[ZON_ZONE]})")
            except:
                monitor_msg = 'NoRecord'

            if self.wazehist_recalculate_time_dist_running_flag is False:
                post_monitor_msg(   Gb.devicename,
                                    f"WazeHistDB > Get Record, "
                                    f"Table-{table}, "
                                    f"Criteria-{criteria}, "
                                    f"{monitor_msg}")
            return record

        except:
            post_internal_error(traceback.format_exc)
            return []

#--------------------------------------------------------------------
    def _get_all_records(self, table, criteria='', orderby=''):
        '''
        Select a record from a table
        :param      sql     - sql statement that will select the record
                    criteria- sql select stmt WHERE clause
                                ("lat_long_key='27.3023:-80.9738'", "location_id=342")
        '''
        try:

            sql = (f"SELECT * FROM {table} ")
            if criteria:
                sql += (f"WHERE {criteria} ")
            if orderby:
                sql += (f"ORDER BY {orderby} ")

            self.cursor.execute(sql)
            records = self.cursor.fetchall()

            post_monitor_msg(   Gb.devicename,
                                f"WazeHistDB > Get All Records, "
                                f"Table-{table}, "
                                f"Criteria-{criteria}, "
                                f"RecdCnt-{len(records)}")

            return records

        except:
            post_internal_error(traceback.format_exc)
            return []

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def get_location_time_dist(self, from_zone, latitude, longitude):
        '''
        Get the waze time & distance from the wacehist data base.

        Return: time        Waze route time
                distance    Waze route distance
                location_id 0 ==>   No history for this lat/long, get from Waze and add it
                            > 0 ==> The id of the recd used to update the last_used date & count
                            -1 ==>  This zone's base location is different than the base location
                                    in the zones table and the zone time/dist values need to be
                                    recalculated. Get the info from Waze and do not update the db.
        '''
        if self.connection is None:
            return

        try:
            zone_id = Gb.wazehist_zone_id.get(from_zone, 0)
            if (Gb.waze_history_database_used is False
                    or zone_id == 0
                    or Gb.waze_history_max_distance == 0):
                return (0, 0, 0)

            lat_long_key = (f"{latitude:.04f}:{longitude:.04f}")
            if self.last_lat_long_key != lat_long_key:
                criteria     = (f" lat_long_key='{lat_long_key}'")
                orderby      = 'zone_id, usage_cnt DESC'
                self.last_location_recds = self._get_all_records('locations', criteria=criteria, orderby=orderby)

            if self.last_location_recds == []:
                self.last_lat_long_key = ''
                return (0, 0, 0)

            self.last_lat_long_key = lat_long_key
            for record in self.last_location_recds:
                if record[LOC_ZONE_ID] == zone_id:
                    return (record[LOC_TIME], record[LOC_DIST], record[LOC_ID])

            return (0, 0, 0)

        except:
            post_internal_error(traceback.format_exc)
            return (0, 0, 0)

#--------------------------------------------------------------------
    def add_location_record(self, zone_id, latitude, longitude, time, distance):

        if self.connection is None:
            return

        try:
            if zone_id < 1:
                return

            lat_long_key = (f"{latitude:.04f}:{longitude:.04f}")
            latitude     = round(latitude, 6)
            longitude    = round(longitude, 6)
            datetime     = datetime_now()

            location_data = [zone_id, lat_long_key, latitude, longitude,
                             time, distance, datetime, datetime, 1]

            location_id = self._add_record(ADD_LOCATION_RECORD, location_data)

            self._update_sensor_ic3_wazehist_track(latitude, longitude)

            return location_id

        except:
            post_internal_error(traceback.format_exc)
            return -1

#--------------------------------------------------------------------
    def update_usage_cnt(self, location_id):
        '''
        Update the location record's last_used date & update the usage counter
        '''

        if self.connection is None:
            return

        try:
            if location_id < 1:
                return

            sql = (f"SELECT * FROM locations WHERE loc_id={location_id}")

            self.cursor.execute(sql)
            record = self.cursor.fetchone()

            cnt = record[LOC_USAGE_CNT] + 1
            usage_data = [datetime_now(), cnt, location_id]

            self._update_record(UPDATE_LOCATION_USED, usage_data)

            self.cursor.execute(sql)
            record = self.cursor.fetchone()

            if self.wazehist_recalculate_time_dist_running_flag is False:
                post_monitor_msg(   Gb.devicename,
                                    f"WazeHistDB > Update Usage Cnt, "
                                    f"recdId={location_id}, "
                                    f"Zone-{record[LOC_ZONE_ID]}, "
                                    f"Time-{record[LOC_TIME]}, "
                                    f"Dist-{record[LOC_DIST]}, "
                                    f"Cnt-{cnt}")

        except:
            post_internal_error(traceback.format_exc)

#--------------------------------------------------------------------
    def compress_wazehist_database(self):
        """ Compress the WazeHist Database """

        if self.connection is None:
            return

        self.cursor.execute(DUPLICATE_LOCATION_RECDS_SELECT)
        records = self.cursor.fetchall()

        if records != []:
            post_event(f"Waze History Database > Deleted Duplicate Recds, Count-{len(records)}")
            self.cursor.execute(DUPLICATE_LOCATION_RECDS_DELETE)
            self.connection.commit()

        self._sql("VACUUM;")

        self.cursor.execute(GET_LOCATIONS_TABLE_RECD_COUNT)
        recd_cnt = self.cursor.fetchone()[0]

        post_event(f"Waze History Database > Compressed, Record Count-{recd_cnt}")

#--------------------------------------------------------------------
    def __repr__(self):
        return (f"<WazeHistory>")

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   Waze History Database MAINTENANCE SETUP
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def load_track_from_zone_table(self):
        '''
        Cycle through the tracked from zones and see if the zone and it's location is in the
        zones table. Save the zone_id that will be used to access the data in locations table.
        - If not, add it.
        - If it is there, check the location to see if it is different than the one used to
            get the waze route distances & times.
        - If it has been changed, the zone's locations need to be updated with new distances
            & times or deleted.
        '''

        if self.connection is None:
            return

        try:
            # Check to see if all tracked from zones are in the zones table
            Gb.wazehist_zone_id = {}

            # for from_zone, Zone in Gb.TrackedZones_by_zone.items():
            for from_zone, Zone in Gb.TrackedZones_by_zone.items():
                # criteria = (f"zone='{from_zone}'")
                criteria = (f"entity_id='{Zone.entity_id}'")
                wazehist_zone_recd = self._get_record('zones', criteria)

                if wazehist_zone_recd:
                    # Fix the zone name if it different than the HA entity registry file. It was probably changed
                    # by the user and needs to be corrected since the zone name is used to determine the tracked
                    # from zone
                    if from_zone != wazehist_zone_recd[ZON_ZONE]:
                        zone_data = [from_zone, wazehist_zone_recd[ZON_ID]]

                        self._update_record(UPDATE_ZONES_TABLE_ZONE_NAME, zone_data)

                    Gb.wazehist_zone_id[from_zone] = wazehist_zone_recd[ZON_ID]

                    # If the zone location was changed by more than 5m, all waze distances/times
                    # need to be updated to the new location during the midnight maintenance check
                    wazehist_zone_recd_gps = (wazehist_zone_recd[ZON_LAT], wazehist_zone_recd[ZON_LONG])
                    zone_distance_check = calc_distance_km(Zone.gps, wazehist_zone_recd_gps)
                    if zone_distance_check > .005:
                        Gb.wazehist_zone_id[from_zone] = wazehist_zone_recd[ZON_ID] * -1

                        event_msg =(f"{EVLOG_ALERT}Waze History Database Zone Location Change ({Zone.display_as}) > "
                                    f"This zone`s location is {format_dist_km(zone_distance_check)} from it`s "
                                    f"last location (>5m). The Waze History will not be used for this zone "
                                    f"until the time/distance data has been recalculated. "
                                    f"{CRLF_DOT}To Do this, select `Event Log > Action > WazeHistory-"
                                    f"Recalculate Route Time/Dist` or,"
                                    f"{CRLF_DOT}This will be done automatically tonight "
                                    f"at midnight.")
                        post_event(event_msg)

                else:
                    zone_data = [from_zone, Zone.entity_id, Zone.latitude, Zone.longitude, 0, datetime_now(), 0]
                    zone_id   = self._add_record(ADD_ZONE_RECORD, zone_data)
                    Gb.wazehist_zone_id[from_zone] = zone_id

                    post_monitor_msg(   f"WazeHistDB > Added zone, "
                                        f"{from_zone}, "
                                        f"zoneId-{zone_id}")

                self._update_sensor_ic3_wazehist_track(Zone.latitude5, Zone.longitude5)

        except:
            post_internal_error(traceback.format_exc)

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   Waze History Database MAINTENANCE - UPDATE TIME/DISTANCE VALUES, COMPRESS DATABASE
#   NOTE: RUNS EACH NIGHT AT MIDNIGHT
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def wazehist_recalculate_time_dist_all_zones(self):
        if self.connection is None:
            return

        self.wazehist_recalculate_time_dist(all_zones_flag=True)

    def wazehist_recalculate_time_dist(self, all_zones_flag=False):
        '''
        Various maintenance functions:
            1.  Recalculate the one time/distance values based on the current zone location for
                zones that have been moved since they were added.
        '''
        if self.connection is None:
            return

        # Cycle through the zones. If the location change flag is set, cycle through the
        # Waze History Database for those zones and recalculate the time & distance.
        try:
            Device = Gb.Devices[0]
            records = self._get_all_records('locations')
            total_recds_cnt = len(records)

            if self.connection is None:
                event_msg = (f"{EVLOG_NOTICE}Waze History Database > Warning, Waze Time/Distance "
                            "is disabled in the iCloud3 configuration")
                post_event(event_msg)

            # Set the Abort Flag which is picked up in the update routine that is running
            # in another thread or as an asyncio task
            if self.wazehist_recalculate_time_dist_running_flag:
                self.wazehist_recalculate_time_dist_abort_flag = True
                Device.display_info_msg("Waze History > Update stopped")
                return

            total_recd_cnt    = 0
            total_update_cnt  = 0
            total_deleted_cnt = 0
            total_recds_cnt   = 0

            self.wazehist_recalculate_time_dist_running_flag = True
            start_time = time.perf_counter()
            for zone, zone_id in Gb.wazehist_zone_id.items():
                if self.wazehist_recalculate_time_dist_abort_flag:
                    break
                elif all_zones_flag:
                    pass
                elif zone_id > 0:       # zone_id whose location changed will be negative
                    continue

                Zone            = Gb.Zones_by_zone[zone]
                zone_display_as = Zone.display_as
                zone_from_loc   = f"{Zone.latitude},{Zone.longitude}"
                zone_id         = abs(zone_id)


                recd_cnt, recds_cnt, update_cnt, deleted_cnt = \
                        self._cycle_through_wazehist_records(zone_id, zone_display_as, zone_from_loc)

                total_recd_cnt    += recd_cnt
                total_update_cnt  += update_cnt
                total_deleted_cnt += deleted_cnt
                total_recds_cnt   += recds_cnt
                restart_cnt        = 0 if recd_cnt == recds_cnt else recd_cnt

                zone_data = [Zone.latitude5, Zone.longitude5, 0, datetime_now(), restart_cnt, zone_id]

                self._update_record(UPDATE_ZONES_TABLE, zone_data)


                if self.wazehist_recalculate_time_dist_abort_flag:
                    break

        except:
            post_internal_error(traceback.format_exc)

        self.compress_wazehist_database()

        running_time = time.perf_counter() - start_time
        event_msg = (f"Waze History Completed > Total Time-{secs_to_time_str(running_time)}")
        post_event(event_msg)

        self.wazehist_recalculate_time_dist_running_flag = False
        self.wazehist_recalculate_time_dist_abort_flag   = False

#--------------------------------------------------------------------
    def _cycle_through_wazehist_records(self, zone_id, zone_display_as, zone_from_loc):
        '''

        '''
        Device = Gb.Devices[0]
        criteria = (f"zone_id={abs(zone_id)}")
        orderby  = "lat_long_key"
        records  = self._get_all_records('locations', criteria=criteria, orderby=orderby)

        total_recds_cnt = len(records)
        event_msg =(f"{EVLOG_NOTICE}Waze History > Recalculate Time/Distance Started, "
                    f"TrackFmZone-{zone_display_as}, "
                    f"Records-{total_recds_cnt}")
        post_event(event_msg)

        recd_cnt   = 0
        update_cnt = 0
        deleted_cnt = 0
        last_recd_lat_long_key = ''
        last_recd_loc_id       = 0
        start_time = time.perf_counter()

        for record in records:
            if self.wazehist_recalculate_time_dist_abort_flag:
                break

            recd_cnt += 1

            try:
                # If this record's location key is the same as the last one,
                # increase the usage count of the last recd and delete this recd
                if record[LOC_LAT_LONG_KEY] == last_recd_lat_long_key:
                    self.update_usage_cnt(last_recd_loc_id)
                    criteria = (f"loc_id={record[LOC_ID]};")
                    self._delete_record('locations', criteria)
                    log_msg = (f"Waze History > updated, (#{recd_cnt}), "
                                f"deleted duplicate record, "
                                f"LocationKey-{record[LOC_LAT_LONG_KEY]}, "
                                f"id-{record[LOC_ID]}")
                    log_info_msg(log_msg)
                    deleted_cnt += 1
                    update_cnt += 1

                # Get new waze time & distance and update the location record
                else:
                    last_recd_lat_long_key = record[LOC_LAT_LONG_KEY]
                    last_recd_loc_id       = record[LOC_ID]

                    update_time_flag, update_dist_flag, new_time, new_dist = \
                                self._update_wazehist_record(
                                                        recd_cnt,
                                                        zone_from_loc,
                                                        record[LOC_LAT_LONG_KEY],
                                                        record[LOC_ID],
                                                        record[LOC_TIME],
                                                        record[LOC_DIST])

                    # There was an error getting the new Waze time/dist info
                    if new_time <= 0 or new_dist <= 0:
                        continue

                    if update_time_flag or update_dist_flag:
                        update_cnt += 1
                        update_msg = f"✓.."
                    else:
                        update_msg = f"⊗.."

                info_msg = (f"Recalc Time/Dist > {zone_display_as[:6]}, "
                            f"{recd_cnt} of {total_recds_cnt}, ChgCnt-{update_cnt}, "
                            f"{update_msg}"
                            f"Time-({record[LOC_TIME]:0.1f}{RARROW2}{new_time:0.1f}min), "
                            f"Dist-({record[LOC_DIST]:0.1f}{RARROW2}{new_dist:0.1f}km) "
                            "ToCancel-Select `EventLog > Action > Recalculate Route Time/Dist` again")
                Device.display_info_msg(info_msg)

                if (recd_cnt % 100) == 0:
                    running_time = time.perf_counter() - start_time
                    log_msg = (f"Waze History > Recalculate Route Time/Dist > "
                                f"Zone-{zone_display_as}, "
                                f"Checked-{recd_cnt} of {total_recds_cnt}, "
                                f"Updated-{update_cnt}, "
                                f"ElapsedTime-{secs_to_time_str(running_time)}")
                    post_event(log_msg)

            except:
                post_internal_error(traceback.format_exc)

            if self.wazehist_recalculate_time_dist_abort_flag:
                break

            try:
                #** 5/15/2022 Delete all records with invalid times or distances
                self._delete_record('locations', 'time < 0 or distance < 0')

            except:
                post_internal_error(traceback.format_exc)

        running_time = time.perf_counter() - start_time
        log_msg = (f"{EVLOG_NOTICE}Waze History Completed > Recalculate Route Time/Dist > "
                    f"Zone-{zone_display_as}, "
                    f"Checked-{recd_cnt} of {total_recds_cnt}, "
                    f"Updated-{update_cnt}, "
                    f"Time-{secs_to_time_str(running_time)}")
        post_event(log_msg)

        return recd_cnt, total_recds_cnt, update_cnt, deleted_cnt
#--------------------------------------------------------------------
    def _update_wazehist_record(self, recd_cnt, zone_from_loc, wazehist_to_loc,
                                            loc_id, current_time, current_dist):
        '''
        Get the waze time & distance and update the wazehist db if:
            - time difference > +- 15-sec
            - distance difference > 50m
        '''
        if self.wazehist_recalculate_time_dist_abort_flag:
            return False, False, 0, 0

        wazehist_to_loc  = wazehist_to_loc.replace(':', ',')

        new_time  = current_time
        new_dist  = current_dist
        retry_cnt = 0
        while retry_cnt < 3:
            try:
                # Gb.Waze.WazeRouteTimeDistObj.__init__(zone_from_loc, wazehist_to_loc, Gb.Waze.waze_region)
                # new_time, new_dist = Gb.Waze.WazeRouteTimeDistObj.calc_route_info(Gb.Waze.waze_realtime)

                from_lat, from_long = zone_from_loc.split(',')
                to_lat  , to_long   = wazehist_to_loc.split(',')

                new_time, new_dist = \
                            Gb.Waze.WazeRouteCalc.calc_route_info   (from_lat, from_long,
                                                                    to_lat, to_long,
                                                                    log_results_flag=False)
                break

            except WRCError as err:
                retry_cnt += 1
            except Exception as err:
                log_exception(err)
                # post_internal_error('Update WazeHist Recd', traceback.format_exc)

        #** 5/15/2022 Make sure values are above 0
        if (new_time < 0
                or new_dist < 0):
            return False, False, 0, 0

        update_time_flag = (abs(new_time - current_time) > .25)
        update_dist_flag = (abs(new_dist - current_dist) > .05)

        if (update_time_flag is False
                and update_dist_flag is False):
            return update_time_flag, update_dist_flag, new_time, new_dist

        new_time = round(new_time, 2)
        new_dist = round(new_dist, 3)

        route_data = [new_time, new_dist, loc_id]

        self._update_record(UPDATE_LOCATION_TIME_DISTANCE, route_data)

        # log_msg = (f"Waze History > updated (#{recd_cnt}), "
        #             f"Time({current_time:0.1f}{RARROW}{new_time:0.1f}min), "
        #             f"Dist({current_dist:0.1f}{RARROW}{new_dist:0.1f}km), "
        #             f"id={loc_id}")
        # log_info_msg(log_msg)

        return update_time_flag, update_dist_flag, new_time, new_dist

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   WAZE HISTORY TRACK SENSOR UPDATE, RUNS EACH NIGHT AT MIDNIGHT
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def wazehist_delete_invalid_rcords(self):

        if self.connection is None:
            return

        # Delete invalid zones
        zone_ids = str([v for v in Gb.wazehist_zone_id.values()]).replace('[', '').replace(']', '')
        criteria = (f" zone_id NOT IN ({zone_ids})")
        records  = self._get_all_records('locations', criteria=criteria)

        if records:
            post_event(f"Waze History > Deleted Locations with Invalid Zones, Cnt-{len(records)}")
            self._delete_record('locations', criteria=criteria)

    #------------------------------------------------------------------------------
    def wazehist_update_track_sensor(self):
        '''
        Cycle through all recds in the locations table and fill in the latitude/longitude
        of the sensor.icloud3_wazehist_track entity. This lets you see all the locations
        in the wazehist database on a lovelace map.
        '''

        if self.connection is None:
            return

        Device = Gb.Devices[0]

        if self.track_direction_north_south_flag:
            orderby = 'latitude, longitude'
            orderby_text = "North-South"
        else:
            orderby = 'longitude, latitude'
            orderby_text = "East-West"

        records = self._get_all_records('locations', orderby=orderby)
        total_recds_cnt = len(records)

        if self.connection is None:
            event_msg = (f"{EVLOG_NOTICE}Waze History Database is disabled in the "
                        "iCloud3 configuration.")
            post_event(event_msg)

        event_msg = (f"Waze History > Refreshing locations that can be displayed "
                        f"in a HA Map using `sensor.icloud3_wazehist_track`, "
                        f"RecordCnt-{total_recds_cnt}, "
                        f"OrderedBy-{orderby_text}")
        post_event(event_msg)

        try:
            self._update_sensor_ic3_wazehist_track(Gb.HomeZone.latitude, Gb.HomeZone.longitude)

            recd_cnt = 0
            for record in records:
                recd_cnt += 1
                info_msg = (f"Waze History > "
                            f"Records-{recd_cnt}/{total_recds_cnt}, "
                            f"GPS-{record[LOC_LAT_LONG_KEY]}")
                Device.display_info_msg(info_msg)

                self._update_sensor_ic3_wazehist_track(record[LOC_LAT], record[LOC_LONG])

            self._update_sensor_ic3_wazehist_track(Gb.HomeZone.latitude, Gb.HomeZone.longitude)

            Device.display_info_msg(Device.format_info_msg)

        except Exception as err:
            log_exception(err)

#--------------------------------------------------------------------
    def _update_sensor_ic3_wazehist_track(self, latitude, longitude):
        '''
        Update the sensor with the latitude/longitude locations
        '''
        if Gb.WazeHist and Gb.WazeHistTrackSensor:
            self.track_latitude = latitude
            self.track_longitude = longitude
            Gb.WazeHistTrackSensor.async_update_sensor()
