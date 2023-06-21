#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   This module handles all tracking activities for a device. It contains
#   the following modules:
#       TrackFromZones - iCloud3 creates an object for each device/zone
#           with the tracking data fields.
#
#   The primary methods are:
#       determine_interval - Determines the polling interval, update times,
#           location data, etc for the device based on the distance from
#           the zone.
#       determine_interval_after_error - Determines the interval when the
#           location data is to be discarded due to poor GPS, it is old or
#           some other error occurs.
#
#
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


from ..global_variables     import GlobalVariables as Gb
from ..const                import (HOME, NOT_HOME, AWAY, NOT_SET, HIGH_INTEGER, CHECK_MARK, CIRCLE_X, LTE, LT,
                                    STATIONARY, STATIONARY_FNAME, WATCH, IOSAPP_FNAME,
                                    AWAY_FROM, TOWARDS, PAUSED, INZONE, NEAR, NEAR_HOME,
                                    ERROR,
                                    VALID_DATA,
                                    WAZE,
                                    NEAR_DEVICE_DISTANCE,
                                    WAZE_USED, WAZE_NOT_USED, WAZE_PAUSED, WAZE_OUT_OF_RANGE, WAZE_NO_DATA,
                                    OLD_LOC_POOR_GPS_CNT, AUTH_ERROR_CNT, RETRY_INTERVAL_RANGE_1, IOSAPP_REQUEST_LOC_CNT,
                                    RETRY_INTERVAL_RANGE_2,
                                    EVLOG_TIME_RECD, EVLOG_ALERT,
                                    RARROW, NEARBY_DEVICE_USEABLE_SYM,
                                    EXIT_ZONE,
                                    ZONE, ZONE_INFO, INTERVAL,
                                    DISTANCE, ZONE_DISTANCE, ZONE_DISTANCE_M, ZONE_DISTANCE_M_EDGE,
                                    MAX_DISTANCE, CALC_DISTANCE, WAZE_DISTANCE, WAZE_METHOD,
                                    TRAVEL_TIME, TRAVEL_TIME_MIN, DIR_OF_TRAVEL, MOVED_DISTANCE,
                                    LAST_LOCATED, LAST_LOCATED_TIME, LAST_LOCATED_DATETIME,
                                    LAST_UPDATE, LAST_UPDATE_TIME, LAST_UPDATE_DATETIME,
                                    NEXT_UPDATE, NEXT_UPDATE_TIME, NEXT_UPDATE_DATETIME,
                                    LAST_LOCATED,
                                    )

from ..support              import iosapp_interface
from ..helpers.common       import (instr, round_to_zero, is_zone, is_statzone, isnot_zone,
                                    zone_display_as, )
from ..helpers.messaging    import (post_event, post_error_msg,
                                    post_internal_error, post_monitor_msg, log_debug_msg, log_rawdata,
                                    log_info_msg, log_error_msg, log_exception, _trace, _traceha, )
from ..helpers.time_util    import (secs_to_time, secs_to_time_str, secs_to_time_age_str, waze_mins_to_time_str,
                                    secs_since, time_to_12hrtime, secs_to_datetime, secs_to, secs_to_age_str,
                                    datetime_now, time_now, time_now_secs, )
from ..helpers.dist_util    import (km_to_mi, km_to_mi_str, format_dist_km,  format_dist_m, format_km_to_mi, )


import homeassistant.util.dt as dt_util
import traceback

# location_data fields
LD_STATUS      = 0
LD_ZONE_DIST   = 1
LD_ZONE_DIST_M = 2
LD_WAZE_DIST   = 3
LD_CALC_DIST   = 4
LD_WAZE_TIME   = 5
LD_MOVED       = 6
LD_DIRECTION   = 7

#waze_from_zone fields
WAZ_STATUS   = 0
WAZ_TIME     = 1
WAZ_DISTANCE = 2
WAZ_MOVED    = 3

#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
def determine_interval(Device, DeviceFmZone):
    '''
    Calculate new interval. Return location based attributes.
    The durrent location:   Device.loc_data_latitude/longitude.
    The last location:      Device.sensors[LATITUDE]/[LONGITUDE]
    '''

    devicename = Device.devicename

    battery10_flag       = (0 > Device.dev_data_battery_level >= 10)
    battery5_flag        = (0 > Device.dev_data_battery_level >= 5)

    inzone_flag          = (Device.loc_data_zone != NOT_HOME)
    not_inzone_flag      = (Device.loc_data_zone == NOT_HOME)
    was_inzone_flag      = (Device.sensors[ZONE] not in [NOT_HOME, AWAY, NOT_SET])

    inzone_home_flag     = (Device.loc_data_zone == HOME)
    was_inzone_home_flag = (Device.sensor_zone == HOME)

    Device.DeviceFmZoneBeingUpdated = DeviceFmZone

    if DeviceFmZone.from_zone == Device.loc_data_zone:
        Device.DeviceFmZoneLast = DeviceFmZone

    if Device.offline_secs > 0:
        event_msg =(f"{EVLOG_ALERT}Device back Online > "
                    f"WentOfflineAt-{secs_to_time_age_str(Device.offline_secs)}, "
                    f"DeviceStatus-{Device.device_status}")
        post_event(devicename, event_msg)
        Device.offline_secs = 0

    #--------------------------------------------------------------------------------
    Device.write_ha_sensor_state(LAST_LOCATED, Device.loc_data_time)

    if used_nearby_device_results(Device, DeviceFmZone):
        return DeviceFmZone.sensors

    Device.NearDeviceUsed = None

    #--------------------------------------------------------------------------------
    location_data = _get_distance_data(Device, DeviceFmZone)

    # If an error occurred, the [1] entry contains an attribute that can be passed to
    # display_info_code to display an error message
    if (location_data[LD_STATUS] == ERROR):
        return location_data[LD_ZONE_DIST]

    dist_from_zone_km       = location_data[LD_ZONE_DIST]
    dist_from_zone_m        = location_data[LD_ZONE_DIST_M]
    waze_dist_from_zone_km  = location_data[LD_WAZE_DIST]
    calc_dist_from_zone_km  = location_data[LD_CALC_DIST]
    waze_time_from_zone     = location_data[LD_WAZE_TIME]
    dist_moved_km           = location_data[LD_MOVED]
    dir_of_travel           = location_data[LD_DIRECTION]

    log_msg = ( f"DistFmZome-{dist_from_zone_km}, Moved-{dist_moved_km}, "
                f"Waze-{waze_dist_from_zone_km}, Calc-{calc_dist_from_zone_km}, "
                f"TravTime-{waze_time_from_zone}, Dir-{dir_of_travel}")
    log_debug_msg(devicename, log_msg)


    #--------------------------------------------------------------------------------
    # The following checks the distance from home and assigns a
    # polling interval in minutes.  It assumes a varying speed and
    # is generally set so it will poll one or twice for each distance
    # group. When it gets real close to home, it switches to once
    # each 15 seconds so the distance from home will be calculated
    # more often and can then be used for triggering automations
    # when you are real close to home. When home is reached,
    # the distance will be 0.

    Device.display_info_msg( f"Determine Interval-{DeviceFmZone.info_status_msg}")

    # Reset got zone exit trigger since now in a zone for next
    # exit distance check. Also reset Stat Zone timer and dist moved.
    if inzone_flag:
        Device.got_exit_trigger_flag = False
        Device.statzone_clear_timer

    waze_time_msg = '0 min'
    calc_interval = round(km_to_mi(dist_from_zone_km) / 1.5) * 60
    if Gb.Waze.is_status_USED:
        waze_interval = round(waze_time_from_zone * 60 * Gb.travel_time_factor , 0)
    else:
        waze_interval = 0

    #--------------------------------------------------------------------------------
    #if more than 3km(1.8mi) then assume driving
    last_went_3km = Device.went_3km
    if DeviceFmZone is Device.DeviceFmZoneLast:
        if dist_from_zone_km > 3:
            oldway_went_3km = True
        elif dist_from_zone_km < .03:    # back in the zone, reset flag
           oldway_went_3km = False

    #--------------------------------------------------------------------------------
    #if more than 3km(1.8mi) then assume driving
    if DeviceFmZone is Device.DeviceFmZoneHome:     #Device.DeviceFmZoneLast:
        if dist_from_zone_km > 3:
            Device.went_3km = True
        elif dist_from_zone_km < .03:    # back in the zone, reset flag
            Device.went_3km = False

    # if last_went_3km != Device.went_3km:
    #         _trace(devicename, f"New went_3k {DeviceFmZone=} {Device.DeviceFmZoneHome=} {dist_from_zone_km=} {Device.went_3km=} {oldway_went_3km=}")

    #--------------------------------------------------------------------------------
    interval        = 15
    interval_str    = ''
    interval_method = ''
    interval_multiplier = 1

    if Device.state_change_flag:
        if inzone_flag:
            #inzone & old location
            if Device.is_location_old_or_gps_poor and battery10_flag is False:
                interval_method = '1.OldLocPoorGPS'
                interval        = _get_interval_for_error_retry_cnt(Device, OLD_LOC_POOR_GPS_CNT)

            elif Device.isnot_in_statzone:
                interval_method = "1.EnterZone"
                interval        = Device.inzone_interval_secs

        #battery < 5% and near zone
        elif battery5_flag and dist_from_zone_km <= 1:
            interval_method = "2.Battery5%"
            interval        = 15

        #battery < 10%
        elif battery10_flag:
            interval_method = "2.Battery10%"
            interval        = Device.statzone_inzone_interval_secs

        #exited zone, set to short interval if other devices are in same zone
        elif not_inzone_flag and was_inzone_flag:
            interval_method = "2.ExitZone"
            interval        = Gb.exit_zone_interval_secs

            if Device.loc_data_zone == HOME:
                DeviceFmZone.max_dist_km = 0
        else:
            interval_method = "2.ZoneChanged"
            interval        = 240

    # Exit_Zone trigger & away & exited less than 1 min ago
    elif (instr(Device.trigger, EXIT_ZONE)
            and not_inzone_flag
            and secs_since(Device.iosapp_zone_exit_secs) < 60):
        interval_method = '3.ExitTrigger'
        interval        = Gb.exit_zone_interval_secs

    #inzone & poor gps & check gps accuracy when inzone
    elif (Device.is_gps_poor
            and inzone_flag
            and Gb.discard_poor_gps_inzone_flag is False):
        interval_method = '3.PoorGPSinZone'
        interval = _get_interval_for_error_retry_cnt(Device, OLD_LOC_POOR_GPS_CNT)

    elif Device.is_gps_poor:
        interval_method = '3.PoorGPS'
        interval        = _get_interval_for_error_retry_cnt(Device, OLD_LOC_POOR_GPS_CNT)

    elif Device.is_location_old_or_gps_poor:
        interval_method = '3.OldLocPoorGPS'
        interval        = _get_interval_for_error_retry_cnt(Device, OLD_LOC_POOR_GPS_CNT)

    # elif Device.is_in_statzone:
    #    interval_method = "3.StatZone"
    #    interval        = Device.statzone_inzone_interval_secs

    elif battery10_flag and dist_from_zone_km > 1:
        interval_method = "3.Battery10%"
        interval        = Device.statzone_inzone_interval_secs

    elif inzone_home_flag or (dist_from_zone_km < .05 and dir_of_travel == TOWARDS):
        interval_method = '3.InHomeZone'
        interval        = Device.inzone_interval_secs

    #in another zone and inzone time > travel time
    elif inzone_flag and Device.inzone_interval_secs > waze_interval:
        interval_method = '3.InZone'
        interval = Device.inzone_interval_secs

    elif dir_of_travel ==  NOT_SET:
        interval_method = '3.NeedInfo'
        interval = 150

    elif dist_from_zone_km < 2 and dir_of_travel == AWAY_FROM:
        interval_method = '<2km.Away'
        interval        = Device.old_loc_threshold_secs  #1.5 mi & going Away

    elif dist_from_zone_km < 2 and Device.went_3km:
        interval_method = '<2km'
        interval        = 15          #1.5 mi = real close and driving

    elif dist_from_zone_km < 2:       #1.5 mi=1 min
        interval_method = '<3km'
        interval        = 60

    elif dist_from_zone_km < 3.5:      #2 mi=1.5 min
        interval_method = '<3.5km'
        interval        = 90

    elif waze_time_from_zone > 5 and waze_interval > 0:
        interval_method = '3.WazeTime'
        interval        = waze_interval

    elif dist_from_zone_km < 5:        #3 mi=2 min
        interval_method = '<5km'
        interval        = 120

    elif dist_from_zone_km < 8:        #5 mi=3 min
        interval_method = '<8km'
        interval        = 180

    elif dist_from_zone_km < 12:       #7.5 mi=5 min
        interval_method = '<12km'
        interval        = 300

    elif dist_from_zone_km < 20:       #12 mi=10 min
        interval_method = '<20km'
        interval        = 600

    elif dist_from_zone_km < 40:       #25 mi=15 min
        interval_method = '<40km'
        interval        = 900

    elif dist_from_zone_km > 150:      #90 mi=1 hr
        interval_method = '>150km'
        interval        = 3600

    else:
        interval_method = '3.Calculated'
        interval        = calc_interval

    if (dir_of_travel in ('', ' ', '___', AWAY_FROM)
            and interval < 180
            and interval > 30):
        interval_method += '+6.Away(<3min)'
        interval = 180

    elif dir_of_travel == AWAY_FROM and not Gb.Waze.distance_method_waze_flag:
        interval_method += '+6.Away(Calc)'
        interval_multiplier = 2    #calc-increase timer

    elif (dir_of_travel == NOT_SET
            and interval > 180):
        interval_method += '+>180s'
        interval = 180

    #15-sec interval (close to zone) and may be going into a stationary zone,
    #increase the interval
    # elif interval == 15 and Gb.this_update_secs >= Device.statzone_timer+45:
    #     interval_method += '+6.StatTimer+45'
    #     interval = 30

    #Turn off waze close to zone flag to use waze after leaving zone or getting more than 1km from it
    if Gb.Waze.waze_close_to_zone_pause_flag:
        if inzone_flag or calc_dist_from_zone_km >= 1:
            Gb.Waze.waze_close_to_zone_pause_flag = False

    #if triggered by ios app (Zone Enter/Exit, Manual, Fetch, etc.)
    if (Device.iosapp_update_flag
            and interval < 180
            and interval > 30):
        interval_method += '+7.iosAppTrigger'
        interval   = 180

    #if changed zones on this poll reset multiplier
    if Device.state_change_flag:
        interval_multiplier = 1

    #Check accuracy again to make sure nothing changed, update counter
    if Device.is_gps_poor:
        interval_multiplier = 1

    try:
        #Real close, final check to make sure interval is not adjusted
        if (interval <= 60
                or ((0 > Device.dev_data_battery_level >= 33) and interval >= 120)):
            interval_multiplier = 1

        interval     = interval * interval_multiplier
        interval, x  = divmod(interval, 5)
        interval     = interval * 5

        #check for max interval, override in zone times
        #_trace(f"{Device.devicename} {interval=} {interval_method=} {Gb.max_interval_secs=} {Device.statzone_inzone_interval_secs} {Device.inzone_interval_secs=}")
        if interval > Gb.max_interval_secs:
            if Device.is_in_statzone:
                interval = Device.in_statzone_interval_secs
                interval_method = f"7.inZoneMax"
            elif inzone_flag:
                pass
                # interval = Gb.max_interval_secs / 2
                # interval_method = f"7.inZoneMax"
            else:
                interval = Gb.max_interval_secs
                interval_method = f"7.Max"

        #  Use interval if > StatZone interval unless the StatZone interval is the device's
        # inzone interval
        elif (Device.is_in_statzone
                and Device.statzone_inzone_interval_secs >= interval):
            interval_method = "7.StatZone"
            interval        = Device.in_statzone_interval_secs
        #_trace(f"{Device.devicename} {interval=} {interval_method=} ")

        interval_str = secs_to_time_str(interval)

        if interval_multiplier > 1:
            interval_method += (f"x{interval_multiplier}")

        #check if next update is past midnight (next day), if so, adjust it
        next_update_secs = round((Gb.this_update_secs + interval)/5, 0) * 5

        # If the device is monitored, the get the smallest next_update_secs for the tracked devices.
        # Override the results of this device with the next one to be updated.
        try:
            if Device.is_monitored:
                for _Device in Gb.Devices_by_devicename_tracked.values():
                    if (_Device.DeviceFmZoneClosest
                            and _Device.near_device_distance <= NEAR_DEVICE_DISTANCE
                            and next_update_secs < _Device.DeviceFmZoneClosest.next_update_secs):
                        next_update_secs = _Device.DeviceFmZoneClosest.next_update_secs
                        interval         = _Device.DeviceFmZoneClosest.interval_secs
                        interval_str     = _Device.DeviceFmZoneClosest.interval_str
                        interval_method  = f"{_Device.fname}"
        except:
            error_msg = f"User Monitor Results error > {_Device.devicename}, Zone-{_Device.DeviceFmZoneClosest.from_zone}"
            post_error_msg(error_msg)
            pass

        # Update all dates and other fields
        DeviceFmZone.interval_secs    = interval
        DeviceFmZone.interval_str     = interval_str
        DeviceFmZone.next_update_secs = next_update_secs
        DeviceFmZone.next_update_time = secs_to_time(next_update_secs)
        DeviceFmZone.last_update_secs = Gb.this_update_secs
        DeviceFmZone.last_update_time = time_to_12hrtime(Gb.this_update_time)

        DeviceFmZone.interval_method  = interval_method
        DeviceFmZone.dir_of_travel    = dir_of_travel

    except Exception as err:
        sensor_msg = post_internal_error('Update DeviceFmZone Times', traceback.format_exc)


    #--------------------------------------------------------------------------------
    # if poor gps and moved less than 1km, redisplay last distances
    if (Device.state_change_flag is False
            and Device.is_gps_poor
            and dist_moved_km < 1):
        dist_from_zone_km      = DeviceFmZone.zone_dist
        dist_from_zone_m       = DeviceFmZone.zone_dist_m
        waze_dist_from_zone_km = DeviceFmZone.waze_dist
        p_from_zone_km = DeviceFmZone.calc_dist
        waze_time_from_zone    = DeviceFmZone.waze_time

    else:
        #save for next poll if poor gps
        DeviceFmZone.zone_dist   = dist_from_zone_km
        DeviceFmZone.zone_dist_m = dist_from_zone_m
        DeviceFmZone.waze_dist   = waze_dist_from_zone_km
        DeviceFmZone.waze_time   = waze_time_from_zone
        DeviceFmZone.calc_dist   = calc_dist_from_zone_km

    waze_time_msg = Gb.Waze.waze_mins_to_time_str(waze_time_from_zone)

    if (Device.is_location_gps_good
            and interval > 60
            and waze_dist_from_zone_km > DeviceFmZone.max_dist_km):
        DeviceFmZone.max_dist_km = waze_dist_from_zone_km

    #--------------------------------------------------------------------------------
    #Make sure the new 'last state' value is the internal value for
    #the state (e.g., Away-->not_home) to reduce state change triggers later.
    sensors                       = {}
    sensors[LAST_LOCATED_DATETIME]= Device.loc_data_datetime
    sensors[LAST_LOCATED_TIME]    = Device.loc_data_time
    sensors[LAST_LOCATED]         = Device.loc_data_time

    sensors.update(_update_next_update_fields_and_sensors(None, interval))

    sensors[TRAVEL_TIME]          = waze_mins_to_time_str(waze_time_from_zone)
    sensors[TRAVEL_TIME_MIN]      = f"{waze_time_from_zone:.0f} min"
    sensors[DIR_OF_TRAVEL]        = dir_of_travel

    sensors[DISTANCE]             = km_to_mi(dist_from_zone_km)
    sensors[MAX_DISTANCE]         = km_to_mi(DeviceFmZone.max_dist_km)
    sensors[ZONE_DISTANCE]        = km_to_mi(dist_from_zone_km)
    sensors[ZONE_DISTANCE_M]      = dist_from_zone_m
    sensors[ZONE_DISTANCE_M_EDGE] = abs(dist_from_zone_m - DeviceFmZone.from_zone_radius_m)
    sensors[WAZE_DISTANCE]        = km_to_mi(waze_dist_from_zone_km)
    sensors[WAZE_METHOD]          = Gb.Waze.waze_status_fname
    sensors[CALC_DISTANCE]        = km_to_mi(calc_dist_from_zone_km)
    sensors[MOVED_DISTANCE]       = km_to_mi(dist_moved_km)

    if Device.is_inzone:
        sensors[ZONE_INFO] = f"@{Device.loc_data_zone_fname}"
    else:
        sensors[ZONE_INFO] = km_to_mi_str(dist_from_zone_km)

    #save for event log
    if type(waze_time_msg) != str: waze_time_msg = ''
    DeviceFmZone.last_tavel_time   = waze_time_msg
    DeviceFmZone.last_distance_km  = dist_from_zone_km
    DeviceFmZone.last_distance_str = (f"{format_km_to_mi(dist_from_zone_km)}")

    if Device.is_location_gps_good:
        Device.old_loc_poor_gps_cnt = 0

    Device.display_info_msg(Device.format_info_msg, new_base_msg=True)
    post_results_message_to_event_log(Device, DeviceFmZone)
    post_zone_time_dist_event_msg(Device, DeviceFmZone)
    DeviceFmZone.sensors.update(sensors)

    return sensors

#--------------------------------------------------------------------------------
def post_results_message_to_event_log(Device, DeviceFmZone):
    '''
    Post the final tracking results to the Event Log and HA log file
    '''
    Device.last_update_msg_secs = time_now()
    event_msg = (f"Results: From-{DeviceFmZone.from_zone_display_as} > ")

    if Device.is_tracked:
        event_msg += (  f"NextUpdate-{DeviceFmZone.next_update_time}, "
                        f"Interval-{DeviceFmZone.interval_str}, ")
    if DeviceFmZone.zone_dist > 0:
        event_msg += (  f"TravTime-{DeviceFmZone.last_tavel_time}, "
                        f"Distance-{format_km_to_mi(DeviceFmZone.zone_dist)}, ")
    if DeviceFmZone.dir_of_travel not in [INZONE, '_', '___', ' ', '']:
        event_msg +=    f"Direction-{DeviceFmZone.dir_of_travel}, "
    if Device.is_statzone_timer_set and Device.is_tracked and Gb.is_statzone_used:
        event_msg +=    f"IntoStatZone-{secs_to_time(Device.statzone_timer)}, "
    if Device.statzone_dist_moved_km > 0:
        event_msg +=    f"Moved-{format_dist_km(Device.statzone_dist_moved_km)}, "
    if Device.dev_data_battery_level > 0:
        event_msg +=    f"Battery-{Device.dev_data_battery_level}%, "
    if Gb.log_debug_flag and DeviceFmZone.interval_method and Device.is_tracked:
        event_msg +=    (f"Method-{DeviceFmZone.interval_method}, "
                        f"{'Went3km, ' if Device.went_3km else ''}")
    post_event(Device.devicename, event_msg[:-2])

    if Device.is_tracked:
        log_msg = ( f"RESULTS: From-{DeviceFmZone.from_zone_display_as} > "
                    f"iOSAppZone-{Device.iosapp_data_state}, "
                    f"iC3Zone-{Device.loc_data_zone}, "
                    f"Interval-{DeviceFmZone.interval_str}, "
                    f"TravTime-{DeviceFmZone.last_tavel_time}, "
                    f"Dist-{format_km_to_mi(DeviceFmZone.zone_dist)}, "
                    f"NextUpdt-{DeviceFmZone.next_update_time}, "
                    f"MaxDist-{format_km_to_mi(DeviceFmZone.max_dist_km)}, "
                    f"Dir-{DeviceFmZone.dir_of_travel}, "
                    f"Moved-{format_dist_km(Device.statzone_dist_moved_km)}, "
                    f"Battery-{Device.dev_data_battery_level}%, "
                    f"LastDataUpdate-{secs_to_time(Device.last_data_update_secs)}, "
                    f"GPSAccuracy-{Device.loc_data_gps_accuracy}m, "
                    f"LocAge-{secs_to_age_str(Device.loc_data_secs)}, "
                    f"OldThreshold-{secs_to_time_str(Device.old_loc_threshold_secs)}, "
                    f"LastEvLogMsg-{secs_to_time(Device.last_evlog_msg_secs)}, "
                    f"Method-{DeviceFmZone.interval_method}")
        log_info_msg(Device.devicename, log_msg)

#--------------------------------------------------------------------------------
def post_zone_time_dist_event_msg(Device, DeviceFmZone):
    '''
    Post the iosapp state, ic3 zone, interval, travel time, distance msg to the
    Event Log
    '''

    if Device.iosapp_monitor_flag:
        iosapp_state = zone_display_as(Device.iosapp_data_state)
        if iosapp_state == NOT_SET:
            iosapp_state = '──'
    else:
        iosapp_state = '──'

    ic3_zone = zone_display_as(Device.loc_data_zone)

    if Device.loc_data_zone == NOT_SET:
        interval = travel_time = distance = '──'
    else:
        interval     = DeviceFmZone.interval_str.split("(")[0] if Device.is_tracked else '──'
        travel_time  = DeviceFmZone.last_tavel_time
        travel_time  = 'inZone' if travel_time == '0 sec' else travel_time
        distance     = DeviceFmZone.zone_distance_str

    event_msg =(f"{EVLOG_TIME_RECD}{iosapp_state},{ic3_zone},{interval},{travel_time},{distance}")
    post_event(Device.devicename, event_msg)

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   iCloud FmF or FamShr authentication returned an error or no location
#   data is available. Update counter and device attributes and set
#   retry intervals based on current retry count.
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def determine_interval_after_error(Device, counter=OLD_LOC_POOR_GPS_CNT):
    '''
    Handle errors where the device can not be or should not be updated with
    the current data. The update will be retried 4 times on a 15 sec interval.
    If the error continues, the interval will increased based on the retry
    count using the following cycles:
        1-4   - 15 sec
        5-8   - 1 min
        9-12  - 5min
        13-16 - 15min
        >16   - 30min

    The following errors use this routine:
        - iCloud Authentication errors
        - FmF location data not available
        - Old location
        - Poor GPS Acuracy
    '''
    devicename = Device.devicename

    try:
        interval, error_cnt, max_error_cnt = get_error_retry_interval(Device, counter)

        # Pause tracking when the max count is exceeded, send paused msg when the cnt is reached
        if error_cnt >= max_error_cnt:
            Device.pause_tracking()

            if error_cnt == max_error_cnt:
                message = {
                    "title": "iCloud3 Tracking Exception",
                    "message": (f"Old Location or Poor GPS Accuracy Error "
                                f"Count exceeded (#{error_cnt}). Event Log > Actions > "
                                f"Resume to restart tracking."),
                    "data": {"subtitle": "Tracking has been Paused"}}
                iosapp_interface.send_message_to_device(Device, message)

        if (Device.is_offline and Device.offline_secs == 0):
            Device.offline_secs = Gb.this_update_secs

        # Often, iCloud does not actually locate the device but just returns the last
        # location it has. A second call is needed after a 5-sec delay. This also
        # happens after a reauthentication. If so, do not display an error on the
        # first retry.

        next_update_secs = Gb.this_update_secs + interval
        Device.update_sensors_error_msg = Device.update_sensors_error_msg or Device.old_loc_poor_gps_msg

        update_all_device_fm_zone_sensors_interval(Device, interval)

        Device.display_info_msg(Device.update_sensors_error_msg)
        event_msg = ''

        if (Device.is_data_source_FAMSHR and Device.is_offline):
            event_msg =(f"{EVLOG_ALERT}Device is Offline > "
                        f"WentOfflineAt-{secs_to_time_age_str(Device.offline_secs)}, "
                        f"RetryAt-{secs_to_time(next_update_secs)}, "
                        f"DeviceStatus-{Device.device_status}")

        elif ((Device.old_loc_poor_gps_cnt > 0
                    and secs_since(Device.DeviceFmZoneHome.next_update_secs) < \
                        (Device.DeviceFmZoneHome.interval_secs + 5))
                or Device.outside_no_exit_trigger_flag):
            pass

        elif counter == AUTH_ERROR_CNT:
            event_msg =(f"Results > RetryCounter-{Gb.icloud_acct_error_cnt}, "
                        f"RetryAt {secs_to_time(next_update_secs)} "
                        f"({Device.DeviceFmZoneHome.interval_str})")

        if event_msg == '' and Device.update_sensors_error_msg != '':
            event_msg =(f"{Device.update_sensors_error_msg}, "
                        f"RetryAt-{secs_to_time(next_update_secs)} "
                        f"({Device.DeviceFmZoneHome.interval_str})")
            Device.icloud_update_reason = "Newer Data is Available"

        if event_msg:
            post_event(devicename, event_msg)
            log_info_msg(Device.devicename, f"Old Location/Other Error-{event_msg}")
            # log_rawdata(f"{Device_devicename} - {from_zone}", DeviceFmZone.sensors)

    except Exception as err:
        log_exception(err)

#----------------------------------------------------------------------------
def get_error_retry_interval(Device, counter=OLD_LOC_POOR_GPS_CNT):
    '''
    Determine the interval value based on the error counter and current retry_count

    Return:
        interval value

    Called from:
        determine interval after error
        Device.post_location_data_accepted_rejected_msg

    '''
    try:
        if Device.is_offline:
            if Device.sensor_zone == NOT_SET:
                return 120, 0, 20
            else:
                return Gb.offline_interval_secs, 0, 20

        interval = 0

        if counter == OLD_LOC_POOR_GPS_CNT:
            error_cnt = Device.old_loc_poor_gps_cnt
            range_tbl = RETRY_INTERVAL_RANGE_1

        elif counter == AUTH_ERROR_CNT:
            error_cnt = Gb.icloud_acct_error_cnt
            range_tbl = RETRY_INTERVAL_RANGE_1

        elif counter == IOSAPP_REQUEST_LOC_CNT:
            error_cnt = Device.iosapp_request_loc_retry_cnt
            range_tbl = RETRY_INTERVAL_RANGE_2
        else:
            error_cnt = Device.old_loc_poor_gps_cnt
            range_tbl = RETRY_INTERVAL_RANGE_1
            interval = 60

        max_error_cnt = int(list(range_tbl.keys())[-1])
        if max_error_cnt < 20: max_error_cnt = 20

        # Retry in 10-secs if this is the first time retried
        if error_cnt <= 1:
            interval = 5

        else:
            interval_list = [cnt_time for cnt, cnt_time in range_tbl.items() if cnt <= error_cnt]
            interval = interval_list[-1]
            interval = interval * 60

    except Exception as err:
        log_exception(err)

    return interval, error_cnt, max_error_cnt

#----------------------------------------------------------------------------
def update_all_device_fm_zone_sensors_interval(Device, interval, DeviceFmZone=None):
    '''
    Update the Device and DeviceFmZone sensors with a new interval

    Parameters:
        Device - Device to be updated
        interval - New polling interval that determins the next_update_time
        DeviceFmZone - Update all DeviceFmZones or only this DeviceFmZone
    '''

    # if next_update_secs < Device.next_update_secs:
    if DeviceFmZone:
        Device.DeviceFmZoneNextToUpdate = DeviceFmZone

    _update_next_update_fields_and_sensors(Device, interval)

    # Set all track from zone intervals. This prevents one zone from triggering an update
    # when the location data was poor.
    for _DeviceFmZone in Device.DeviceFmZones_by_zone.values():
        _update_next_update_fields_and_sensors(_DeviceFmZone, interval)

        # Move Stationary Zone timer if it is set and expired so it does not trigger an update
        if Device.statzone_timer_reached and Gb.is_statzone_used:
            Device.statzone_timer = Device.next_update_secs

#----------------------------------------------------------------------------
def _update_next_update_fields_and_sensors(Device_DfZ, interval):
    '''
    Update all of the internal and sensor fields for an interval value.

    Parameters:
        Device   - The Device or DeviceFmZone to update
                   None: Update a sensors dictionary to be merged with Device.sensors later
        interval - The new interval (secs)

    Return:
        sensors  - Dictionary of updated sensors that can be merged with the Device's
                    sensors.
    '''
    next_update_secs = Gb.this_update_secs + interval
    next_update_time = secs_to_time(next_update_secs)

    sensors = {}

    if Device_DfZ:
        Device = Device_DfZ if Device_DfZ in Gb.Devices else Device_DfZ.Device
        data_source_ICLOUD = Device.is_data_source_ICLOUD
    else:
        data_source_ICLOUD = Gb.primary_data_source_ICLOUD

    sensors[INTERVAL]             = secs_to_time_str(interval)
    sensors[NEXT_UPDATE_DATETIME] = secs_to_datetime(next_update_secs)
    sensors[NEXT_UPDATE_TIME]     = next_update_time
    sensors[NEXT_UPDATE]          = next_update_time

    sensors[LAST_UPDATE_DATETIME] = datetime_now()
    sensors[LAST_UPDATE_TIME]     = time_now()
    sensors[LAST_UPDATE]          = time_now()

    if Device_DfZ is None:
        return sensors

    Device_DfZ.interval_secs    = interval
    Device_DfZ.interval_str     = secs_to_time_str(interval)
    Device_DfZ.next_update_secs = next_update_secs
    Device_DfZ.next_update_time = next_update_time
    Device_DfZ.last_update_secs = Gb.this_update_secs
    Device_DfZ.last_update_time = time_to_12hrtime(Gb.this_update_time)

    Device_DfZ.sensors.update(sensors)

    return sensors

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   UPDATE DEVICE LOCATION & INFORMATION ATTRIBUTE FUNCTIONS
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def _get_distance_data(Device, DeviceFmZone):
    """
    Determine the location of the device.
        Returns:
            - zone (current zone from lat & long)
                set to HOME if distance < home zone radius
            - dist_from_zone_km (mi or km)
            - dist_traveled (since last poll)
            - dir_of_travel (towards, away_from, stationary, in_zone,
                left_zone, near_home)
    """

    Device.display_info_msg(f"GetDistancesFrom-{DeviceFmZone.from_zone_display_as}")

    if Device.no_location_data:
        event_msg = "No location data available, will retry"
        post_event(Device.devicename, event_msg)
        return (ERROR, {})


    calc_dist_from_zone_km = dist_from_zone_km   = DeviceFmZone.distance_km
    dist_from_zone_m       = dist_from_zone_km * 1000
    waze_dist_moved_km     = dist_moved_km       = Device.loc_data_dist_moved_km
    waze_dist_from_zone_km = calc_dist_from_zone_km
    waze_time_from_zone    = 0
    last_dir_of_travel     = DeviceFmZone.dir_of_travel
    from_zone              = DeviceFmZone.from_zone

    # Device is in the from_zone so nothing to do
    if Device.loc_data_zone == from_zone:
        Device.statzone_reset_timer
        Gb.Waze.waze_status = WAZE_PAUSED
        Gb.Waze.waze_close_to_zone_pause_flag = True
        distance_data = [VALID_DATA,
                        0,                          # dist_from_zone_km,
                        dist_from_zone_m,           # # dist_from_zone_m,
                        0,                          # waze_dist_from_zone_km,
                        calc_dist_from_zone_km,     # calc_dist_from_zone_km,
                        dist_moved_km,
                        0,                          # waze_time_from_zone,
                        INZONE]

        return  distance_data

    #--------------------------------------------------------------------------------
    Gb.Waze.waze_status = WAZE_USED if Gb.Waze.distance_method_waze_flag else WAZE_NOT_USED
    waze_source_msg = ''
    if Gb.Waze.is_status_USED:
        # See if this location hasn't changed or is in the history db
        if Gb.WazeHist.is_historydb_USED and calc_dist_from_zone_km < Gb.WazeHist.max_distance:
            waze_status, waze_time_from_zone, waze_dist_from_zone_km, dist_moved_km, \
                hist_db_location_id, waze_source_msg = \
                Gb.Waze.get_history_time_distance(Device, DeviceFmZone, check_hist_db=True)
        else:
            hist_db_location_id = 0

        # Not in history db or history db is not used
        if hist_db_location_id == 0:
            waze_dist_from_zone_km = calc_dist_from_zone_km
            waze_time_from_zone    = 0

        if hist_db_location_id > 0:
            pass

        # Pause waze and set close to zone pause flag if nearing a track from zone
        elif (calc_dist_from_zone_km < 1
                and Device.loc_data_zone == from_zone
                and DeviceFmZone.is_going_towards):
            Gb.Waze.waze_status = WAZE_PAUSED
            Gb.Waze.waze_close_to_zone_pause_flag = True
            dist_from_zone_km = calc_dist_from_zone_km

        #Determine if Waze should be used based on calculated distance
        elif (calc_dist_from_zone_km > Gb.Waze.waze_max_distance
                or calc_dist_from_zone_km < Gb.Waze.waze_min_distance):
            Gb.Waze.waze_status = WAZE_OUT_OF_RANGE
            dist_from_zone_km = calc_dist_from_zone_km
            if calc_dist_from_zone_km > 1:
                waze_source_msg = f"Out of Range, Dist-{format_dist_km(calc_dist_from_zone_km)} "
                if calc_dist_from_zone_km > Gb.Waze.waze_max_distance:
                    waze_source_msg += f"(> {format_dist_km(Gb.Waze.waze_max_distance)})"
                else:
                    waze_source_msg += f"(< {format_dist_km(Gb.Waze.waze_min_distance)})"

    dist_from_zone_m = dist_from_zone_km * 1000

    # Get Waze travel_time & distance
    if Gb.Waze.is_status_USED:
        if hist_db_location_id == 0:
            waze_status, waze_time_from_zone, waze_dist_from_zone_km, waze_dist_moved_km \
                    = Gb.Waze.get_route_time_distance(Device, DeviceFmZone, check_hist_db=False)

            Gb.Waze.waze_status = waze_status

        # Don't reset data if poor gps, use the best we have
        dist_from_zone_m = dist_from_zone_km * 1000
        Device.display_info_msg( f"Finalizing-{DeviceFmZone.info_status_msg}")
        if Device.loc_data_zone == from_zone:
            dist_from_zone_km = 0
            dist_moved_km     = 0

        elif Gb.Waze.is_status_USED:
            dist_from_zone_km = waze_dist_from_zone_km
            dist_from_zone_m  = waze_dist_from_zone_km * 1000
            dist_moved_km     = waze_dist_moved_km
    else:
        waze_dist_from_zone_km = 0

    if waze_source_msg:
        event_msg = f"Waze Route Info > {waze_source_msg}"
        post_event(Device.devicename, event_msg)

    #--------------------------------------------------------------------------------
    dir_of_travel = '___'
    time_change = 0 if waze_time_from_zone == 0 else round(waze_time_from_zone - DeviceFmZone.waze_time, 2)
    dist_change = round(dist_from_zone_km - DeviceFmZone.zone_dist, 2)

    if Device.is_in_statzone:
        dir_of_travel = STATIONARY_FNAME

    elif Device.is_inzone:
        dir_of_travel = INZONE

    elif Device.sensors[ZONE] == NOT_SET or last_dir_of_travel == NOT_SET:
        dir_of_travel = Device.sensors[DIR_OF_TRAVEL]

    # Towards if the last zone distance > than this zone distance
    elif time_change < 0 or dist_change < 0:
        dir_of_travel = TOWARDS

    elif (Device.got_exit_trigger_flag
            or instr(Device.trigger.lower, 'exit')
            or (Device.was_inzone and isnot_zone(Device.sensor_zone))
            or time_change > 0
            or dist_change > 0):
        dir_of_travel = AWAY_FROM

    else:
        #didn't move far enough to tell current direction
        dir_of_travel = last_dir_of_travel

    if Device.loc_data_zone == NOT_HOME:
        if Gb.is_statzone_used is False:
            pass

        elif Device.statzone_timer == 0:
            Device.statzone_reset_timer

        # If moved more than stationary zone limit (~.06km(200ft)),
        # reset StatZone still timer
        # Use calc distance rather than waze for better accuracy
        elif (calc_dist_from_zone_km > Gb.statzone_min_dist_from_zone_km
                and Device.loc_data_dist_moved_km > Gb.statzone_dist_move_limit_km
                and Device.is_tracked):
            Device.statzone_reset_timer

            event_msg =(f"StatZone Timer Reset > "
                        f"MovedTooFar-{format_dist_km(Device.loc_data_dist_moved_km)}, "
                        f"Limit-{format_dist_km(Gb.statzone_dist_move_limit_km)}, "
                        f"NewTimer-{secs_to_time(Device.statzone_timer)}")
            post_event(Device.devicename, event_msg)

    dist_from_zone_km      = round_to_zero(dist_from_zone_km)
    dist_moved_km          = round_to_zero(dist_moved_km)
    waze_dist_from_zone_km = round_to_zero(waze_dist_from_zone_km)
    waze_dist_moved_km     = round_to_zero(waze_dist_moved_km)

    distance_data = [VALID_DATA,
                    dist_from_zone_km,
                    dist_from_zone_m,
                    waze_dist_from_zone_km,
                    calc_dist_from_zone_km,
                    waze_time_from_zone,
                    dist_moved_km,
                    dir_of_travel]

    return  distance_data

#--------------------------------------------------------------------------------
def _get_interval_for_error_retry_cnt(Device, counter=OLD_LOC_POOR_GPS_CNT, pause_control_flag=False):
    '''
    Get the interval time based on the retry_cnt.
    retry_cnt   =   poor_location_gps count (default)
                =   iosapp_request_loc_sent_retry_cnt
                =   retry pyicloud authorization count
    pause_control_flag = True if device will be paused (interval is negative)
                = False if just getting interfal and device will not be paused

    Returns     interval in minutes
                (interval is negative if device should be paused)

    Interval range table - key = retry_cnt, value = time in minutes
    - poor_location_gps cnt, icloud_authentication cnt (default):
        interval_range_1 = {0:.25, 4:1, 8:5,  12:30, 16:60, 20:120, 24:240}
    - request iosapp location retry cnt:
        interval_range_2 = {0:.5,  4:2, 8:30, 12:60, 16:120}

    '''
    if counter == OLD_LOC_POOR_GPS_CNT:
        retry_cnt = Device.old_loc_poor_gps_cnt
        range_tbl = RETRY_INTERVAL_RANGE_1

    elif counter == AUTH_ERROR_CNT:
        retry_cnt = Gb.icloud_acct_auth_error_cnt
        range_tbl = RETRY_INTERVAL_RANGE_1

    elif counter == IOSAPP_REQUEST_LOC_CNT:
        retry_cnt = Device.iosapp_request_loc_retry_cnt
        range_tbl = RETRY_INTERVAL_RANGE_2
    else:
        return 60

    interval = .25
    for k, v in range_tbl.items():
        if k <= retry_cnt:
            interval = v

    if pause_control_flag is False: interval = abs(interval)
    interval = interval * 60

    return interval


#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   If a NearDevice is available, Make sure that it is not a circular reference by checking
#   the NearDevice's NearDevice. It should not point back to this Device. If so, don't use it.
#   If OK, use the results of another device that is nearby. It must be
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def used_nearby_device_results(Device, DeviceFmZone):
    if (Device.NearDevice is None
            or Device.NearDevice.NearDevice is Device
            or DeviceFmZone.from_zone not in Device.NearDevice.DeviceFmZones_by_zone):
        return False

    neardevice_fname      = Device.NearDevice.fname_devtype
    neardevice_fname_chk  = f"{NEARBY_DEVICE_USEABLE_SYM}{neardevice_fname}"
    Device.dist_apart_msg = Device.dist_apart_msg.replace(NEARBY_DEVICE_USEABLE_SYM, '')
    Device.dist_apart_msg = Device.dist_apart_msg.replace(neardevice_fname, neardevice_fname_chk)

    event_msg =(f"Using Nearby Device Results > {Device.NearDevice.fname}, "
                f"Distance-{format_dist_m(Device.near_device_distance)}")
    post_event(Device.devicename, event_msg)

    copy_near_device_results(Device, DeviceFmZone)
    Device.display_info_msg(Device.format_info_msg, new_base_msg=True)
    post_results_message_to_event_log(Device, DeviceFmZone,)
    post_zone_time_dist_event_msg(Device, DeviceFmZone)

    return True

#--------------------------------------------------------------------------------
def copy_near_device_results(Device, DeviceFmZone):
    '''
    The Device is near the NearDevice for the DeviceFmZone zone results. Copy the NearDevice
    variables to Device since everything is the same.
    '''
    NearDevice       = Device.NearDevice
    from_zone        = DeviceFmZone.from_zone
    NearDeviceFmZone = Device.NearDevice.DeviceFmZones_by_zone[from_zone]

    Device.loc_data_zone           = NearDevice.loc_data_zone

    DeviceFmZone.zone_dist         = NearDeviceFmZone.zone_dist
    DeviceFmZone.waze_dist         = NearDeviceFmZone.waze_dist
    DeviceFmZone.waze_time         = NearDeviceFmZone.waze_time
    DeviceFmZone.calc_dist         = NearDeviceFmZone.calc_dist
    DeviceFmZone.interval_method   = NearDeviceFmZone.interval_method
    DeviceFmZone.last_update_secs  = NearDeviceFmZone.last_update_secs
    DeviceFmZone.last_update_time  = NearDeviceFmZone.last_update_time
    DeviceFmZone.last_tavel_time   = NearDeviceFmZone.last_tavel_time
    DeviceFmZone.last_distance_km  = NearDeviceFmZone.last_distance_km
    DeviceFmZone.last_distance_str = NearDeviceFmZone.last_distance_str
    DeviceFmZone.dir_of_travel     = NearDeviceFmZone.dir_of_travel
    Device.zone_change_secs        = NearDevice.zone_change_secs

    DeviceFmZone.sensors.update(NearDeviceFmZone.sensors)

    if Device.is_in_statzone:
        interval_secs = Device.in_statzone_interval_secs
    elif Device.is_inzone:
        interval_secs = Device.inzone_interval_secs
    else:
        interval_secs = NearDeviceFmZone.interval_secs

    _update_next_update_fields_and_sensors(DeviceFmZone, interval_secs)

    Device.StatZone                = NearDevice.StatZone
    Device.statzone_timer          = NearDevice.statzone_timer
    Device.statzone_dist_moved_km  = NearDevice.statzone_dist_moved_km
    Device.iosapp_request_loc_sent_secs = Gb.this_update_secs

    log_rawdata(f"{Device.devicename} - {from_zone}", DeviceFmZone.sensors)

    return DeviceFmZone.sensors

#--------------------------------------------------------------------------------
def update_nearby_device_info(Device):
    '''
    Cycle through the devices and see if this device is in the same location as
    another device updated earlier in this 5-sec polling loop.

    Return: The closest device

    {devicename: [dist_m, gps_accuracy_factor, display_text]}
    '''
    if (len(Gb.Devices) == 1
            or len(Device.dist_to_other_devices) == 0
            or Gb.distance_between_device_flag is False):
        return

    closest_device_distance     = HIGH_INTEGER
    Device.dist_apart_msg       = ''
    Device.NearDevice           = None
    Device.near_device_distance = 0
    Device.near_device_checked_secs = time_now_secs()

    for devicename, dist_to_other_devices in Device.dist_to_other_devices.items():
        _Device = Gb.Devices_by_devicename[devicename]

        dist_m, min_gps_accuracy, display_text = dist_to_other_devices

        # if one device is a watch and the devices are paired and the watch is close to the
        # device, the watch may use the devices location info. Don't use the watch as nearby
        # ⦾×⌘⛒♺⚯⚠︎⚮∞
        if ((Device.device_type == WATCH or _Device.device_type == WATCH)
                and Device.person_id_famshr == _Device.person_id_famshr
                and dist_m < NEAR_DEVICE_DISTANCE):
            useable_symbol = '×'
        elif dist_m > NEAR_DEVICE_DISTANCE:
            useable_symbol = '>'
        elif min_gps_accuracy > NEAR_DEVICE_DISTANCE:
            useable_symbol = '±'
        elif display_text == '0m/±0m':
            useable_symbol = '×'
        elif _Device.NearDevice is Device:
            useable_symbol = '⌘'
        elif _check_near_device_circular_loop(_Device, Device) is False:
            useable_symbol = '⌘'
        elif Device.loc_data_zone != _Device.loc_data_zone:
            useable_symbol = '🜔'
        else:
            useable_symbol = NEARBY_DEVICE_USEABLE_SYM

        Device.dist_apart_msg += (  f"{useable_symbol}{_Device.fname_devtype}-"
                                    f"{display_text}, ")

        # The nearby devices can not point to each other and other criteria
        # if (((Device.is_tracked and _Device.is_tracked) or _Device.is_monitored)
        if (Device.is_tracked
                and _Device.is_tracked
                and useable_symbol == NEARBY_DEVICE_USEABLE_SYM
                and _Device.DeviceFmZoneHome.interval_secs > 0
                and _Device.old_loc_poor_gps_cnt == 0
                and _Device.is_online):

            if dist_m < closest_device_distance:
                closest_device_distance = dist_m
                Device.NearDevice = _Device
                Device.near_device_distance = dist_m

    monitor_msg = f"Nearby Devices > ({LT}{NEAR_DEVICE_DISTANCE}m), {Device.dist_apart_msg}"
    post_monitor_msg(Device.devicename, monitor_msg)

    return

#--------------------------------------------------------------------------------
def _check_near_device_circular_loop(_Device, Device):
    '''
    Make sure the eligible nearbe device is not used by another device(s) that ends
    up referencing the Device being updated, creating a circular loop back to itself
    '''
    if _Device.NearDevice is None:
        return True

    next_Device_to_check = _Device.NearDevice
    checked_Devices = []
    near_devices_msg = f"{_Device.devicename}{RARROW}{next_Device_to_check.devicename}"
    log_debug_base_msg = f"Check Nearby Device-{_Device.devicename}"
    reason_msg = ''

    check_start_time_secs = time_now_secs()
    cnt = 0
    can_use_device = False

    while can_use_device is False:     #next_Device_to_check is not Device:
        # Make sure the loop will not hang
        cnt += 1
        if cnt > len(Gb.Devices):
            reason_msg = f"DeviceCnt-{cnt} > {len(Gb.Devices)}"
            break

        # Make sure the loop does not hang by only running 5-secs
        if secs_since(check_start_time_secs) > 5:
            reason_msg = 'Running more than 10-secs'
            break

        # If the next_NearDevice will loop back to a device that has already been checked,
        # do not use the _Device.NearDevice
        if next_Device_to_check.NearDevice in checked_Devices:
            near_devices_msg += f"{RARROW}{_Device.devicename}"
            reason_msg = 'Looped back to itself'
            break

        # If the next_NearDevice circles back to the _Device originally being checked,
        # do not use the _Device.NearDevice
        if next_Device_to_check.NearDevice is _Device:
            near_devices_msg += f"{RARROW}{_Device.devicename}"
            reason_msg = 'Looped back to start'
            break

        # If the NearDevice cycle ends, it's OK to use the current _Device
        if (next_Device_to_check is None
                or next_Device_to_check.NearDevice is None):
            near_devices_msg += f"{RARROW}None"
            can_use_device = True
            break

        near_devices_msg += f"{RARROW}{next_Device_to_check.NearDevice.devicename}"
        next_Device_to_check = next_Device_to_check.NearDevice
        checked_Devices.append(next_Device_to_check.NearDevice)
        log_msg = ( f"{log_debug_base_msg}, Checking, "
                    f"Cnt-{cnt}, "
                    f"Timer-{secs_since(check_start_time_secs)} secs, "
                    f"{near_devices_msg}")
        log_debug_msg(Device.devicename, log_msg)

    # The loop was broken out of
    can_cannot_msg = 'CanUse' if can_use_device else f"CanNotUse, {reason_msg}"
    log_msg = ( f"{log_debug_base_msg}, "
                f"{can_cannot_msg}, "
                f"Cnt-{cnt}, "
                f"Timer-{secs_since(check_start_time_secs)} secs, "
                f"{near_devices_msg}")
    log_debug_msg(Device.devicename, log_msg)
    return can_use_device
