#------------------------------------------------------------------------------
#
#   This module handles all device data
#
#------------------------------------------------------------------------------
from .global_variables  import GlobalVariables as Gb
from .const             import (DEVICE_TRACKER, DEVICE_TRACKER_DOT, CIRCLE_STAR2, LTE, GTE,
                                NOTIFY, DISTANCE_TO_DEVICES, NEAR_DEVICE_DISTANCE,
                                DISTANCE_TO_OTHER_DEVICES, DISTANCE_TO_OTHER_DEVICES_DATETIME,
                                HOME, HOME_FNAME, NOT_HOME, NOT_SET, UNKNOWN, DOT, RARROW, INFO_SEPARATOR,
                                TOWARDS, AWAY, AWAY_FROM, INZONE, STATIONARY, STATIONARY_FNAME,
                                TOWARDS_HOME, AWAY_FROM_HOME, INZONE_HOME, INZONE_STATIONARY,
                                PAUSED, PAUSED_CAPS, RESUMING,
                                DATETIME_ZERO, HHMMSS_ZERO, HIGH_INTEGER,
                                TRACKING_NORMAL, TRACKING_PAUSED, TRACKING_RESUMED,
                                LAST_CHANGED_SECS, LAST_CHANGED_TIME, STATE,
                                EVLOG_ALERT,
                                BLANK_SENSOR_FIELD,
                                ICLOUD, FMF, FAMSHR, FMF_FNAME, FAMSHR_FNAME,
                                IOSAPP, IOSAPP_FNAME,
                                DATA_SOURCE_FNAME,
                                TRACK_DEVICE, MONITOR_DEVICE, INACTIVE_DEVICE,
                                NAME, DEVICE_TYPE_FNAME,
                                ICLOUD_HORIZONTAL_ACCURACY, ICLOUD_VERTICAL_ACCURACY, ICLOUD_BATTERY_STATUS,
                                ICLOUD_BATTERY_LEVEL, ICLOUD_DEVICE_CLASS, ICLOUD_DEVICE_STATUS, ICLOUD_LOW_POWER_MODE, ID,
                                FRIENDLY_NAME, PICTURE, ICON, BADGE,
                                LATITUDE, LONGITUDE,
                                LOCATION, LOCATION_SOURCE, TRIGGER, TRACKING,
                                FROM_ZONE, INTERVAL,
                                ZONE, ZONE_DISPLAY_AS, ZONE_NAME, ZONE_FNAME, ZONE_DATETIME,
                                LAST_ZONE, LAST_ZONE_DISPLAY_AS, LAST_ZONE_NAME, LAST_ZONE_FNAME, LAST_ZONE_DATETIME,
                                BATTERY_SOURCE, BATTERY, BATTERY_LEVEL, BATTERY_STATUS, BATTERY_STATUS_FNAME, BATTERY_UPDATE_TIME,
                                ZONE_DISTANCE, ZONE_DISTANCE_M, ZONE_DISTANCE_M_EDGE, HOME_DISTANCE, MAX_DISTANCE,
                                CALC_DISTANCE, WAZE_DISTANCE, WAZE_METHOD,
                                TRAVEL_TIME, TRAVEL_TIME_MIN, DIR_OF_TRAVEL,
                                MOVED_DISTANCE, MOVED_TIME_FROM, MOVED_TIME_TO,
                                DEVICE_STATUS, LOW_POWER_MODE, RAW_MODEL, MODEL, MODEL_DISPLAY_NAME,
                                LAST_UPDATE, LAST_UPDATE_TIME, LAST_UPDATE_DATETIME,
                                NEXT_UPDATE, NEXT_UPDATE_TIME, NEXT_UPDATE_DATETIME,
                                LAST_LOCATED, LAST_LOCATED_TIME, LAST_LOCATED_DATETIME,
                                INFO, GPS_ACCURACY, GPS, VERT_ACCURACY, ALTITUDE,
                                DEVICE_STATUS_CODES, DEVICE_STATUS_OFFLINE, DEVICE_STATUS_PENDING,
                                CONF_TRACK_FROM_BASE_ZONE, CONF_TRACK_FROM_ZONES,
                                FRIENDLY_NAME, PICTURE, ICON, BADGE,
                                CONF_PICTURE, CONF_STAT_ZONE_FNAME,
                                CONF_DEVICE_TYPE, CONF_RAW_MODEL, CONF_MODEL, CONF_MODEL_DISPLAY_NAME,
                                CONF_FNAME, CONF_FAMSHR_DEVICENAME,
                                CONF_IOSAPP_DEVICE, CONF_FMF_EMAIL,
                                CONF_TRACKING_MODE, CONF_INZONE_INTERVAL, )

from .const_sensor      import (SENSOR_LIST_ZONE_NAME, SENSOR_ICONS, )
from .                  import device_fm_zone
from .support           import determine_interval as det_interval
from .support           import restore_state
from .helpers           import entity_io

from .helpers.common    import (instr, is_zone, isnot_zone, is_statzone,
                                circle_letter, format_gps, zone_display_as, round_to_zero, )
from .helpers.messaging import (post_event, post_error_msg, post_monitor_msg, log_exception, log_debug_msg,
                                post_internal_error, _trace, _traceha, )
from .helpers.time_util import ( time_now_secs, secs_to_time, secs_to_time_str, secs_since, secs_to,
                                time_to_12hrtime,
                                datetime_to_secs, secs_to_datetime, datetime_now,
                                secs_to_age_str,  secs_to_time_age_str, )
from .helpers.dist_util import (calc_distance_m, calc_distance_km, format_km_to_mi, m_to_ft_str,
                                format_dist_km, format_dist_m, km_to_mi,)

from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.util import slugify
import traceback
import copy

#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
class iCloud3_Device(TrackerEntity):

    def __init__(self, devicename, conf_device):
        self.conf_device           = conf_device
        self.devicename            = devicename
        self.dr_device_id          = ''      # ha device_registry device_id
        self.fname                 = devicename.title()

        self.StatZone              = None    # The StatZone this Device is in or None if not in a StatZone
        #self.stationary_zonename   = (f"{self.devicename}_{STATIONARY}")

        self.DeviceFmZones_by_zone = {}      # DeviceFmZones objects for the track_from_zones parameter for this Device
        self.DeviceFmZoneHome      = None    # DeviceFmZone object for the Home zone
        self.device_fm_zone_names  = []      # List of the from_zones in the DeviceFmZones_by_zone dictionary
        self.only_track_from_home  = True    # Track from only Home  (True) or also track from other zones (False)
        self.DeviceFmZoneBeingUpdated = None    # DeviceFmZone object being updated in determine_interval for EvLog TfZ info
        self.DeviceFmZoneNextToUpdate = None # Set to the DeviceFmZone when it's next_update_time is reached
        self.DeviceFmZoneClosest   = None    # DeviceFmZone object for the Closest tfz - used to set the Device's sensors
        self.DeviceFmZoneLast      = None    # DeviceFmZone object the device was last in

        self.TrackFromBaseZone     = None    # DeviceFmZone of Home or secondary tracked from zone
        self.track_from_base_zone  = HOME    # Name of secondary tracked from base zone (normally Home)
        self.NearDevice            = None    # Device in the same location as this Device
        self.NearDeviceUsed        = None
        self.DeviceTracker         = None    # Device's device_tracker entity object
        self.Sensors               = Gb.Sensors_by_devicename.get(devicename, {})
        self.Sensors_from_zone     = Gb.Sensors_by_devicename_from_zone.get(devicename, {})

        self.initialize()
        self.initialize_on_initial_load()
        self.initialize_sensors()
        self._link_device_entities_sensor_device_tracker()
        self.configure_device(conf_device)
        self.initialize_track_from_zones()

    def initialize(self):
        self.devicename_verified          = False

        # Operational variables
        self.device_type                  = 'iPhone'
        self.raw_model                    = DEVICE_TYPE_FNAME.get(self.device_type, self.device_type)      # iPhone15,2
        self.model                        = DEVICE_TYPE_FNAME.get(self.device_type, self.device_type)      # iPhone
        self.model_display_name           = DEVICE_TYPE_FNAME.get(self.device_type, self.device_type)      # iPhone 14 Pro
        self.data_source                  = None
        self.tracking_status              = TRACKING_NORMAL
        self.tracking_mode                = TRACK_DEVICE      #normal, monitor, inactive
        self.last_data_update_secs        = 0
        self.last_evlog_msg_secs          = 0
        self.last_update_msg_secs         = 0
        self.dist_from_zone_km_small_move_total = 0
        self.device_tracker_entity_ic3    = (f"{DEVICE_TRACKER}.{self.devicename}")
        self.zone_change_datetime         = DATETIME_ZERO
        self.zone_change_secs             = 0
        self.info_msg                     = ''              # results of last format_info_msg
        self.went_3km                     = False
        self.near_device_distance         = 0               # Distance to the NearDevice device
        self.near_device_checked_secs     = 0               # When the nearby devices were last updated
        self.dist_apart_msg               = ''              # Distance to all other devices msg set in icloud3_main
        self.dist_apart_msg_by_devicename = {}              # Distance to all other devices msg set in icloud3_main
        self.last_update_loc_secs         = 0               # Located secs from the device tracker entity update
        self.last_update_loc_time         = DATETIME_ZERO   # Located time from the device tracker entity update
        self.last_update_gps_accuracy     = 0
        self.passthru_zone                = ''
        self.passthru_zone_timer          = 0               # Timer (secs) when the passthru zone delay expires
        self.selected_zone_results        = []              # ZoneSelected, zone_selected, zone_selected_dist_m, zones_distance_list

        # Trigger & Update variables
        self.trigger                      = 'iCloud3'
        self.next_update_secs             = 0
        self.seen_this_device_flag        = False
        self.iosapp_zone_enter_secs       = 0
        self.iosapp_zone_enter_time       = HHMMSS_ZERO
        self.iosapp_zone_enter_zone       = ''
        self.iosapp_zone_enter_dist_m     = -1
        self.iosapp_zone_enter_trigger_info= ''
        self.iosapp_zone_exit_secs        = 0
        self.iosapp_zone_exit_time        = HHMMSS_ZERO
        self.iosapp_zone_exit_zone        = ''
        self.iosapp_zone_exit_dist_m      = -1
        self.iosapp_zone_exit_trigger_info= ''
        self.update_in_process_flag       = False
        self.device_being_updated_retry_cnt = 0
        self.got_exit_trigger_flag        = False
        self.outside_no_exit_trigger_flag = False
        self.moved_since_last_update      = 0

        # Fields used in FmF and FamShr initialization
        self.verified_flag           = False    # Indicates this is a valid and trackable Device
        self.device_id_famshr        = None     #       "
        self.device_id_fmf           = None     # iCloud device_id
        self.person_id_famshr        = None

        # StatZone fields
        self.statzone_timer          = 0
        self.statzone_dist_moved_km  = 0
        self.statzone_setup_secs     = 0     # Time the statzone was set up

        # iCloud configration fields
        self.conf_famshr_name        = None
        self.conf_famshr_devicename  = None
        self.conf_famshr_device_id   = None
        self.conf_fmf_email          = None
        self.conf_fmf_device_id      = None

        # Device source
        self.primary_data_source     = ICLOUD
        self.is_data_source_FAMSHR   = True
        self.is_data_source_FMF      = False
        self.is_data_source_ICLOUD   = True
        self.is_data_source_FAMSHR_FMF = True
        self.is_data_source_IOSAPP   = True

        # Device location & gps fields
        self.old_loc_poor_gps_cnt    = 0
        self.old_loc_poor_gps_msg    = ''
        self.old_loc_threshold_secs  = 120
        self.poor_gps_flag           = False
        self.inzone_interval_secs    = 600
        self.statzone_inzone_interval_secs = min(self.inzone_interval_secs, Gb.statzone_inzone_interval_secs)
        self.offline_secs            = 0        # Time the device went offline
        self.pending_secs            = 0        # Time the device went into a pending status (checked after authentication)
        self.dist_to_other_devices   = {}       # A dict of other devices distances
                                                # {devicename: [distance_m, gps_accuracy_factor, location_old_flag]}
        self.dist_to_other_devices_datetime = DATETIME_ZERO

        self.last_iosapp_msg         = ''
        self.last_device_monitor_msg = ''
        self.iosapp_statzone_action_msg_cnt = 0

        self.time_waze_calls         = 0.0

        # Device iOSApp message fields
        self.iosapp_request_loc_first_secs = 0    # Used for checking if alive and user request
        self.iosapp_request_loc_last_secs  = 0    # Used for checking if alive and user request
        self.iosapp_request_loc_cnt        = 0
        self.iosapp_request_loc_sent_secs  = 0    # Used for tracking in 5-sec loop when the data source is iosapp

        # iOSApp state variables
        self.iosapp_monitor_flag           = False
        self.iosapp_data_state             = NOT_SET
        self.iosapp_data_latitude          = 0.0
        self.iosapp_data_longitude         = 0.0
        self.iosapp_data_state_secs        = 0
        self.iosapp_data_state_time        = HHMMSS_ZERO
        self.iosapp_data_trigger_secs      = 0
        self.iosapp_data_trigger_time      = HHMMSS_ZERO
        self.iosapp_data_secs              = 0
        self.iosapp_data_time              = HHMMSS_ZERO
        self.iosapp_data_trigger           = NOT_SET
        self.iosapp_data_gps_accuracy      = 0
        self.iosapp_data_vertical_accuracy = 0
        self.iosapp_data_altitude          = 0.0

        # iOS App data update control variables
        self.invalid_error_cnt             = 0
        self.iosapp_data_invalid_error_cnt = 0
        self.iosapp_data_updated_flag      = False
        self.iosapp_data_change_reason     = ''         # Why a state/trigger is causing an update
        self.iosapp_data_reject_reason     = ''         # Why a state/trigger was not updated
        self.iosapp_update_flag            = False
        self.last_iosapp_trigger           = ''

        # iCloud data update control variables
        # self.icloud_update_needed_flag     = False
        self.icloud_devdata_useable_flag   = False
        self.icloud_acct_error_flag        = False      # An error occured from the iCloud account update request
        self.icloud_update_reason          = 'Trigger > Initial Locate'
        self.icloud_no_update_reason       = ''
        self.icloud_update_retry_flag      = False       # Set to True for initial locate
        self.icloud_initial_locate_done    = False

        # Final update control variables -
        self.update_sensors_flag           = False       # The data is good and tracking can be updated
        self.update_sensors_error_msg      = ''          # Reason an error message will be displayed

        # Location Data from iCloud or the iOS App
        self.dev_data_source             = NOT_SET          #icloud or iosapp data
        self.dev_data_fname              = ''
        self.dev_data_device_class       = 'iPhone'
        self.dev_data_device_status      = "Online"
        self.dev_data_device_status_code = 200
        self.dev_data_low_power_mode     = False

        self.loc_data_zone           = NOT_SET
        self.loc_data_latitude       = 0.0
        self.loc_data_longitude      = 0.0
        self.loc_data_gps_accuracy   = 0
        self.loc_data_secs           = 0
        self.loc_data_time           = HHMMSS_ZERO
        self.loc_data_datetime       = DATETIME_ZERO
        self.loc_data_altitude       = 0.0
        self.loc_data_vert_accuracy  = 0
        self.loc_data_isold          = False
        self.loc_data_ispoorgps      = False
        self.loc_data_dist_moved_km  = 0.0
        self.loc_data_time_moved_from = DATETIME_ZERO
        self.loc_data_time_moved_to   = DATETIME_ZERO
        self.last_loc_data_time_gps   = f"{HHMMSS_ZERO}/0m"

        self.sensor_prefix            = (f"sensor.{self.devicename}_")

        # Test variables used for saving the last value of a variable during debugging
        self.debug_save_number            = 0
        self.debug_save_string            = ''
        self.debug_save_list              = []
        self.debug_save_dict              = {}

    def __repr__(self):
        return (f"<Device: {self.devicename}>")

#------------------------------------------------------------------------------
    def initialize_on_initial_load(self):
        # Initialize these variables only when starting up
        # Do not initialize them on a restart

        # If self.sensors exista, this device has been initialized during the initial
        # load or when iC3 is restarted and it is not a new device.
        try:
            if self.sensor != {}:
                return
        except:
            pass

        # if Gb.initial_icloud3_loading_flag is False:
        #     return

        self.iosapp_data_battery_level    = 0
        self.iosapp_data_battery_status   = ''
        self.iosapp_data_battery_update_secs = 0

        self.dev_data_battery_source      = ''
        self.dev_data_battery_level       = 0
        self.dev_data_battery_status      = ''
        self.dev_data_battery_update_secs = 0
        self.dev_data_battery_level_last  = 0
        self.dev_data_battery_status_last = ''

#------------------------------------------------------------------------------
    def initialize_sensors(self):
        # device_tracker.[devicename] attributes for the Device

        self.attrs              = {}
        self.kwargs             = {}
        self.sensors            = {}
        # self.sensors_um         = {}
        self.sensors_icon       = {}
        self.sensor_badge_attrs = {}

        # Device related sensors
        self.sensors[NAME]               = ''
        self.sensors[PICTURE]            = ''
        self.sensors[BADGE]              = ''
        self.sensors[LOW_POWER_MODE]     = ''
        self.sensors[INFO]               = ''

        self.sensors[BATTERY]            = 0
        self.sensors[BATTERY_STATUS]     = ''
        self.sensors[BATTERY_SOURCE]     = ''
        self.sensors[BATTERY_UPDATE_TIME] = HHMMSS_ZERO

        # Location related items
        self.sensors[GPS]                = (0, 0)
        self.sensors[LATITUDE]           = 0
        self.sensors[LONGITUDE]          = 0
        self.sensors[GPS_ACCURACY]       = 0
        self.sensors[ALTITUDE]           = 0
        self.sensors[VERT_ACCURACY]      = 0
        self.sensors[LOCATION_SOURCE]    = ''             #icloud:fmf/famshr or iosapp
        self.sensors[TRIGGER]            = ''
        self.sensors[LAST_LOCATED_DATETIME] = DATETIME_ZERO
        self.sensors[LAST_LOCATED_TIME]     = HHMMSS_ZERO
        self.sensors[LAST_LOCATED]          = HHMMSS_ZERO

        self.sensors['dev_id']           = ''
        self.sensors[RAW_MODEL]          = ''
        self.sensors[MODEL]              = ''
        self.sensors[MODEL_DISPLAY_NAME] = ''
        self.sensors['host_name']        = ''
        self.sensors['source_type']      = GPS
        self.sensors[DEVICE_STATUS]      = UNKNOWN
        self.sensors[TRACKING]           = ''
        self.sensors[DISTANCE_TO_DEVICES]= ''
        self.sensors[DISTANCE_TO_OTHER_DEVICES] = {}
        self.sensors[DISTANCE_TO_OTHER_DEVICES_DATETIME] = HHMMSS_ZERO

        # Sensors overlaid with DeviceFmZone sensors for nearest zone
        self.sensors[FROM_ZONE]             = ''
        self.sensors[INTERVAL]              = ''
        self.sensors[NEXT_UPDATE_DATETIME]  = DATETIME_ZERO
        self.sensors[NEXT_UPDATE_TIME]      = HHMMSS_ZERO
        self.sensors[NEXT_UPDATE]           = HHMMSS_ZERO
        self.sensors[LAST_UPDATE_DATETIME]  = DATETIME_ZERO
        self.sensors[LAST_UPDATE_TIME]      = HHMMSS_ZERO
        self.sensors[LAST_UPDATE]           = HHMMSS_ZERO
        self.sensors[TRAVEL_TIME]           = 0
        self.sensors[TRAVEL_TIME_MIN]       = 0
        self.sensors[ZONE_DISTANCE]         = 0
        self.sensors[ZONE_DISTANCE_M]       = 0
        self.sensors[ZONE_DISTANCE_M_EDGE]  = 0
        self.sensors[HOME_DISTANCE]         = 0
        self.sensors[MAX_DISTANCE]          = 0
        self.sensors[WAZE_DISTANCE]         = 0
        self.sensors[WAZE_METHOD]           = 0
        self.sensors[CALC_DISTANCE]         = 0
        self.sensors[DIR_OF_TRAVEL]         = NOT_SET
        self.sensors[MOVED_DISTANCE]        = 0
        self.sensors[MOVED_TIME_FROM]       = DATETIME_ZERO
        self.sensors[MOVED_TIME_TO]         = DATETIME_ZERO

        # Zone related items
        self.sensors[ZONE]               = NOT_SET
        self.sensors[ZONE_DISPLAY_AS]    = NOT_SET
        self.sensors[ZONE_FNAME]         = NOT_SET
        self.sensors[ZONE_NAME]          = NOT_SET
        self.sensors[ZONE_DATETIME]      = DATETIME_ZERO
        self.sensors[LAST_ZONE]          = NOT_SET
        self.sensors[LAST_ZONE_DISPLAY_AS]=NOT_SET
        self.sensors[LAST_ZONE_FNAME]    = NOT_SET
        self.sensors[LAST_ZONE_NAME]     = NOT_SET
        self.sensors[LAST_ZONE_DATETIME] = DATETIME_ZERO


        # Initialize the Device sensors[xxx] value from the restore_state file if
        # the sensor is in the file. Otherwise, initialize to this value. This will preserve
        # non-tracking sensors across restarts
        self._restore_sensors_from_restore_state_file()

#------------------------------------------------------------------------------
    def _link_device_entities_sensor_device_tracker(self):
        # The DeviceTracker & Sensors entities are created before the Device object
        # using the configuration parameters. Cycle thru them now to set there
        # self.Device, device_id and area_id variables to this Device object.
        # This permits access to the sensors & attrs values.

        # Link the DeviceTracker-Device objects
        if self.devicename in Gb.DeviceTrackers_by_devicename:
            self.DeviceTracker = Gb.DeviceTrackers_by_devicename[self.devicename]
            self.DeviceTracker.Device = self
            try:
                self.DeviceTracker.device_id = Gb.dr_device_id_by_devicename[self.devicename]
                self.DeviceTracker.area_id   = Gb.dr_area_id_by_devicename[self.devicename]
            except:
                pass

        # Cycle through all sensors for this device.
        # Link the Sensor-Device objects to provide access the sensors dictionary
        # when they are updated.
        for Sensor in self.Sensors.values():
            Sensor.Device = self

        for sensor, Sensor in self.Sensors_from_zone.items():
            Sensor.Device = self

#------------------------------------------------------------------------------
    def configure_device(self, conf_device):

        # Configuration parameters
        self.tracking_mode        = conf_device.get(CONF_TRACKING_MODE, 'track')
        self.fname                = conf_device.get(CONF_FNAME, self.devicename.title())
        self.sensors[NAME]        = self.fname
        self.sensors['dev_id']    = self.devicename
        self.sensors['host_name'] = self.fname

        # iosapp device_tracker/sensor entity ids
        self.iosapp_entity = {
            DEVICE_TRACKER: '',
            TRIGGER: '',
            BATTERY_LEVEL: 0,
            BATTERY_STATUS: '',
            NOTIFY: '',
        }

        self.sensor_badge_attrs[FRIENDLY_NAME] = self.fname
        self.sensor_badge_attrs[ICON]          = 'mdi:account-circle-outline'

        self._initialize_data_source_fields(conf_device)

        self.device_type = conf_device.get(CONF_DEVICE_TYPE, 'iphone')
        picture          = conf_device.get(CONF_PICTURE, 'None').replace('www/', '/local/')
        if picture:
            self.sensors[PICTURE] = picture if instr(picture, '/') else (f"/local/{picture}")
            self.sensor_badge_attrs[PICTURE] = self.sensors[PICTURE]

        # Validate zone name and get Zone Object for a valid zone
        self.inzone_interval_secs = conf_device.get(CONF_INZONE_INTERVAL, 30) * 60
        self.statzone_inzone_interval_secs = min(self.inzone_interval_secs, Gb.statzone_inzone_interval_secs)

        # Get and validate track from zone config
        self.track_from_base_zone = conf_device.get(CONF_TRACK_FROM_BASE_ZONE, HOME)
        self.track_from_zones     = conf_device.get(CONF_TRACK_FROM_ZONES, HOME).copy()
        if HOME not in self.track_from_zones:
            self.track_from_zones.append(HOME)

        # Update tfz with master base zone, also remove Home zone if necessary
        if Gb.track_from_base_zone != HOME:
            self.track_from_base_zone = Gb.track_from_base_zone
            if Gb.track_from_home_zone is False:
                self.track_from_zones.remove(HOME)

        # Make sure track_from_base_zone is is in the track_from_zones list. If it is,
        # make sure it is the last entry. If not, add it as a tracked_from_aone.
        if self.track_from_base_zone in self.track_from_zones:
            if self.track_from_base_zone != self.track_from_zones[-1]:
                self.track_from_zones.remove(self.track_from_base_zone)
                self.track_from_zones.append(self.track_from_base_zone)
        else:
            self.track_from_zones.append(self.track_from_base_zone)

    def _extract_devicename(self, device_field):
        # The xxx_device field will contain a '>' if it is a valid devicename that will be used
        if instr(device_field, '>'):
            device_name = device_field.split(' >')[0].strip()
        elif device_field.startswith('Select'):
            device_name = ''
        else:
            device_name = device_field

        return device_name

#--------------------------------------------------------------------
    def _initialize_data_source_fields(self, conf_device):

        if Gb.conf_data_source_FAMSHR and conf_device.get(CONF_FAMSHR_DEVICENAME, 'None') != 'None':
            self.conf_famshr_name       = self._extract_devicename(conf_device[CONF_FAMSHR_DEVICENAME])
            self.conf_famshr_devicename = slugify(self.conf_famshr_name)

        if Gb.conf_data_source_FMF and conf_device.get(CONF_FMF_EMAIL, 'None') != 'None':
            self.conf_fmf_email = self._extract_devicename(conf_device[CONF_FMF_EMAIL])

        if Gb.conf_data_source_IOSAPP and conf_device.get(CONF_IOSAPP_DEVICE, 'None') != 'None':
            self.iosapp_entity[DEVICE_TRACKER] = conf_device[CONF_IOSAPP_DEVICE]

        self.is_data_source_FAMSHR     = Gb.conf_data_source_FAMSHR and self.conf_famshr_devicename is not None
        self.is_data_source_FMF        = Gb.conf_data_source_FMF    and self.conf_fmf_email is not None
        self.is_data_source_ICLOUD     = Gb.primary_data_source_ICLOUD and (self.is_data_source_FAMSHR or self.is_data_source_FMF)
        self.is_data_source_FAMSHR_FMF = self.is_data_source_ICLOUD
        self.is_data_source_IOSAPP     = Gb.conf_data_source_IOSAPP and self.iosapp_entity[DEVICE_TRACKER] != ''

        # Set primary data source
        if self.conf_famshr_devicename:
            self.primary_data_source = FAMSHR
        elif self.conf_fmf_email:
            self.primary_data_source = FMF
        elif self.iosapp_entity[DEVICE_TRACKER]:
            self.primary_data_source = IOSAPP
        else:
            self.primary_data_source = None

#--------------------------------------------------------------------
    def initialize_track_from_zones(self):
        '''
        Cycle through each track_from_zones zone.
            - Validate the zone name
            - Create the DeviceFmZones object
            - Set up the global variables with the DeviceFmZone objects
        '''
        try:
            try:
                old_DeviceFmZones_by_zone = self.DeviceFmZones_by_zone.copy()
            except Exception as err:
                log_exception(err)
                old_DeviceFmZones_by_zone = {}

            self.DeviceFmZones_by_zone = {}

            # Validate the zone in the config parameter. If valid, get the Zone object
            # and add to the device's DeviceFmZones_by_zone object list
            if self.track_from_zones == []:
                self.track_from_zones.append(HOME)

            # Reuse current DeviceFmZones if it exists.
            track_from_zones = self.track_from_zones.copy()
            for zone in track_from_zones:
                if zone not in Gb.Zones_by_zone:
                    self.track_from_zones.remove(zone)

                    alert_msg = (f"{EVLOG_ALERT}Alert > Invalid Track-from-Zone "
                                    f"configuration parameter > Device-{self.fname_devicename}, "
                                    f"InvalidZone-{zone} (Removed), "
                                    f"Update `Track From Zone` parameter using the "
                                    f"iCloud3 Configurator")
                    post_event(alert_msg)
                    continue

                Zone = Gb.Zones_by_zone[zone]
                if Zone.passive:
                    idx = self.track_from_zones.index(zone)
                    self.track_from_zones[idx] = f"{LTE}{zone}-Passive{GTE}"
                    continue

                if zone in old_DeviceFmZones_by_zone:
                    DeviceFmZone = old_DeviceFmZones_by_zone[zone]
                    DeviceFmZone.__init__(self, zone)
                    post_monitor_msg(f"INITIALIZED DeviceFmZone > {self.devicename}:{zone}")

                else:
                    DeviceFmZone = device_fm_zone.iCloud3_DeviceFmZone(self, zone)
                    post_monitor_msg(f"ADDED DeviceFmZone > {self.devicename}:{zone}")

                self.DeviceFmZones_by_zone[zone] = DeviceFmZone

                self._restore_sensors_from_restore_state_file(zone, DeviceFmZone)

                if zone not in Gb.TrackedZones_by_zone:
                    Gb.TrackedZones_by_zone[zone] = Gb.Zones_by_zone[zone]

                if zone == self.track_from_base_zone:
                    self.DeviceFmZoneHome    = DeviceFmZone
                    self.DeviceFmZoneLast    = DeviceFmZone
                    self.DeviceFmZoneBeingUpdated = DeviceFmZone
                    self.DeviceFmZoneNextToUpdate = DeviceFmZone
                    self.DeviceFmZoneClosest = DeviceFmZone
                    self.TrackFromBaseZone   = DeviceFmZone

            # Set a list of tracked from zone names to make it easier to get them later
            self.device_fm_zone_names = [k for k in self.DeviceFmZones_by_zone.keys()]
            self.only_track_from_home = (len(self.DeviceFmZones_by_zone) == 1)

        except Exception as err:
            log_exception(err)

#--------------------------------------------------------------------
    def _restore_sensors_from_restore_state_file(self, zone=None, DeviceFmZone=None):
        '''
        Restore the Device's sensor values and the Device's DeviceFmZone track from zone sensors
        from the restore_state configuration file
        '''
        try:
            if DeviceFmZone:
                DeviceFmZone.sensors.update(Gb.restore_state_devices[self.devicename]['from_zone'][zone])
            else:
                self.sensors.update(Gb.restore_state_devices[self.devicename]['sensors'])

        except:
            pass

#--------------------------------------------------------------------
    @property
    def fname_devicename(self):
        return (f"{self.fname}{INFO_SEPARATOR}{self.devicename}")

    @property
    def devicename_fname(self):
        return (f"{self.devicename}{INFO_SEPARATOR}{self.fname}")

    @property
    def fname_devtype(self):
        if instr(self.fname, DEVICE_TYPE_FNAME.get(self.device_type, self.device_type)):
            return self.fname

        return (f"{self.fname}{INFO_SEPARATOR}"
                f"{DEVICE_TYPE_FNAME.get(self.device_type, self.device_type)}")

    @property
    def device_id8_famshr(self):
        if self.device_id_famshr:
            return f"#{self.device_id_famshr[:8]}"
        return 'None'

    @property
    def device_id8_fmf(self):
        if self.device_id_fmf:
            return f"#{self.device_id_fmf[:8]}"
        return 'None'

    def is_statzone_name(self, zone_name):
        return zone_name in Gb.StatZones_by_zone

    @property
    def PyiCloud_RawData_famshr(self):
        if Gb.PyiCloud is None:
            return None
        else:
            return Gb.PyiCloud.RawData_by_device_id.get(self.device_id_famshr)

    @property
    def PyiCloud_RawData_fmf(self):
        if Gb.PyiCloud is None:
            return None
        else:
            return Gb.PyiCloud.RawData_by_device_id.get(self.device_id_fmf)

    def device_model(self):
        return f"{self.device_type}"

    @property
    def iosapp_device_trkr_entity_id_fname(self):
        return (f"{self.iosapp_entity[DEVICE_TRACKER].replace(DEVICE_TRACKER_DOT, '')}")

    @property
    def DeviceFmZone(self, Zone):
        return (f"{self.devicename}:{Zone.zone}")

    @property
    def state_change_flag(self):
        return (self.sensors[ZONE] != self.loc_data_zone)

    @property
    def sensor_zone(self):
        return self.sensors[ZONE]

    @property
    def loc_data_zone_fname(self):
        return zone_display_as(self.loc_data_zone)

    @property
    def loc_data_time_gps(self):
        return (f"{self.loc_data_time}/±"
                f"{self.loc_data_gps_accuracy:.0f}m")
    @property
    def iosapp_data_time_gps(self):
        return (f"{time_to_12hrtime(self.iosapp_data_time)}/±"
                f"{self.iosapp_data_gps_accuracy:.0f}m")

    @property
    def device_status(self):
        return f"{self.dev_data_device_status}/{self.dev_data_device_status_code}"

    @property
    def device_status_msg(self):
        return ( f"{DEVICE_STATUS_CODES.get(self.dev_data_device_status_code, 'Unknown')}/"
                f"{self.dev_data_device_status_code}")

    @property
    def loc_data_fgps(self):
        return format_gps(self.loc_data_latitude, self.loc_data_longitude, self.loc_data_gps_accuracy)

    @property
    def iosapp_data_fgps(self):
        return format_gps(self.iosapp_data_latitude, self.iosapp_data_longitude, self.iosapp_data_gps_accuracy)

    @property
    def loc_data_gps(self):
        return (self.loc_data_latitude, self.loc_data_longitude)

    @property
    def iosapp_data_gps(self):
        return (self.iosapp_data_latitude, self.iosapp_data_longitude)

    #--------------------------------------------------------------------
    @property
    def format_battery_level(self):
        return f"{self.dev_data_battery_level}%"

    @property
    def format_battery_status(self):
        return f"{BATTERY_STATUS_FNAME.get(self.dev_data_battery_status, self.dev_data_battery_status.title())}"

    @property
    def format_battery_status_source(self):
        return (f"{BATTERY_STATUS_FNAME.get(self.dev_data_battery_status, self.dev_data_battery_status.title())} "
                f"({self.dev_data_battery_source})")

    @property
    def format_battery_level_status_source(self):
        return f"{self.format_battery_level}, {self.format_battery_status_source}"

    @property
    def format_battery_time(self):
        return secs_to_datetime(self.dev_data_battery_update_secs)

#--------------------------------------------------------------------
    @property
    def data_source_fname(self):
        return DATA_SOURCE_FNAME.get(self.data_source, self.data_source)

    # @property
    # def is_data_source_FMF(self):
    #     return Gb.conf_data_source_FMF and self.conf_fmf_email

    # @property
    # def is_data_source_FAMSHR(self):
    #     return Gb.conf_data_source_FAMSHR and self.conf_famshr_devicename

    # @property
    # def is_data_source_FAMSHR_FMF(self):
    #     return self.is_data_source_FAMSHR or self.is_data_source_FMF

    # @property
    # def is_data_source_ICLOUD(self):
    #     return self.is_data_source_FAMSHR_FMF

    # @property
    # def is_data_source_IOSAPP(self):
    #     return Gb.conf_data_source_IOSAPP and self.iosapp_entity[DEVICE_TRACKER]

    # is_dev_data_source properties
    @property
    def is_dev_data_source_NOT_SET(self):
        return self.dev_data_source == NOT_SET

    @property
    def is_dev_data_source_FMF(self):
        return self.dev_data_source in [FMF, FMF_FNAME]

    @property
    def is_dev_data_source_FAMSHR(self):
        return self.dev_data_source in [FAMSHR, FAMSHR_FNAME]

    @property
    def is_dev_data_source_FAMSHR_FMF(self):
        return self.dev_data_source in [FAMSHR, FMF, FAMSHR_FNAME, FMF_FNAME]

    @property
    def is_dev_data_source_ICLOUD(self):
        return self.is_dev_data_source_FAMSHR_FMF

    @property
    def is_dev_data_source_IOSAPP(self):
        return self.dev_data_source in [IOSAPP, IOSAPP_FNAME]

    @property
    def no_location_data(self):
        return self.loc_data_latitude == 0 or self.loc_data_longitude == 0

    # is_xxx other properties
    @property
    def is_tracked(self):
        return self.tracking_mode == TRACK_DEVICE

    @property
    def is_monitored(self):
        return self.tracking_mode == MONITOR_DEVICE

    @property
    def is_inactive(self):
        return self.tracking_mode == INACTIVE_DEVICE

    @property
    def is_online(self):
        return not self.is_offline

    @property
    def is_offline(self):
        ''' Returns True/False if the device is offline based on the device_status '''
        if self.is_data_source_FMF:
            return False
        return (self.dev_data_device_status in DEVICE_STATUS_OFFLINE)

    @property
    def is_pending(self):
        ''' Returns True/False if the device is pending based on the device_status '''
        return (self.dev_data_device_status in DEVICE_STATUS_PENDING)

    @property
    def is_using_iosapp_data(self):
        ''' Return True/False if using IOSApp data '''
        return self.dev_data_source == IOSAPP_FNAME

    @property
    def track_from_other_zone_flag(self):
        ''' Returns True if tracking from multiple zones '''
        return (len(self.DeviceFmZones_by_zone) > 1)

    @property
    def located_secs_plus_5(self):
        ''' timestamp (secs) plus 5 secs for next cycle '''
        return (self.loc_data_secs)     # + 5)

    @property
    def is_approaching_tracked_zone(self):
        '''
        Determine if the Device is going towards a tracked zone, is within 1km of
        the zone, on a 15-sec inerval and the location is older than 15-secs.
        When this occurs, we want to refresh the location or set the old
        location threshold to 15-secs.
        '''
        if self.DeviceFmZoneClosest:
            if (secs_to(self.next_update_secs) <= 15
                    and secs_since(self.loc_data_secs > 15)
                    and self.DeviceFmZoneClosest.is_going_towards
                    and self.DeviceFmZoneClosest.zone_dist < 1
                    and self.went_3km):
                return True
        return False

    @property
    def is_tracked_from_home(self):
        return self.DeviceFmZoneClosest.from_zone == HOME

#--------------------------------------------------------------------
    def update_location_gps_accuracy_status(self):
        if self.icloud_devdata_useable_flag or self.loc_data_secs == 0:
            self.loc_data_isold = False
            self.loc_data_ispoorgps = False
        else:
            self.loc_data_isold     = (secs_since(self.loc_data_secs) > self.old_loc_threshold_secs
                                        or self.is_offline)
            self.loc_data_ispoorgps = (self.loc_data_gps_accuracy > Gb.gps_accuracy_threshold)
            self.icloud_devdata_useable_flag = self.loc_data_isold is False and self.loc_data_ispoorgps is False


    @property
    def is_iosapp_data_good(self):
        return not self.is_iosapp_data_old

    @property
    def is_iosapp_data_old(self):
        return secs_since(self.iosapp_data_secs) > self.old_loc_threshold_secs

    @property
    def is_location_old_or_gps_poor(self):
        self.update_location_gps_accuracy_status()
        return (self.loc_data_isold or self.loc_data_ispoorgps)

    @property
    def is_location_old_and_gps_poor(self):
        self.update_location_gps_accuracy_status()
        return (self.loc_data_isold and self.loc_data_ispoorgps)

    @property
    def is_location_gps_good(self):
        self.update_location_gps_accuracy_status()
        return (self.loc_data_isold is False and self.loc_data_ispoorgps is False)

    @property
    def is_location_old(self):
        self.update_location_gps_accuracy_status()
        return self.loc_data_isold

    @property
    def is_location_good(self):
        return not self.is_location_old

    @property
    def is_gps_poor(self):
        self.update_location_gps_accuracy_status()
        return self.loc_data_ispoorgps

    @property
    def is_gps_good(self):
        return not self.is_gps_poor

    @property
    def is_next_update_overdue(self):
        return (secs_since(self.next_update_secs) > 60)

#--------------------------------------------------------------------
    @property
    def is_still_at_last_location(self):
        return False
        #return (self.loc_data_latitude == self.sensors[LATITUDE]
        #            and self.loc_data_longitude == self.sensors[LONGITUDE])

    @property
    def sensor_secs(self):
        return (datetime_to_secs(self.sensors[LAST_UPDATE_DATETIME]))

    @property
    def loc_data_age(self):
        ''' timestamp(secs) --> age (secs ago)'''
        return (secs_since(self.loc_data_secs))

    @property
    def loc_data_time_age(self):
        ''' timestamp (secs) --> hh:mm:ss (secs ago)'''
        return self.loc_data_12hrtime_age

    @property
    def loc_data_time_utc(self):
        ''' timestamp (secs) --> hh:mm:ss'''
        return (secs_to_time(self.loc_data_secs))

    @property
    def loc_data_12hrtime_age(self):
        ''' location time --> 12:mm:ss (secs ago)'''
        return (f"{time_to_12hrtime(self.loc_data_time)} "
                f"({secs_to_time_str(self.loc_data_age)} ago)")

#--------------------------------------------------------------------
    @property
    def isnot_set(self):
        return (self.sensors[ZONE] == NOT_SET)

    @property
    def is_inzone(self):
        return (self.loc_data_zone not in [NOT_HOME, NOT_SET])

    @property
    def isnot_inzone(self):
        return (self.loc_data_zone in [NOT_HOME, NOT_SET])

    @property
    def is_inzone_iosapp_state(self):
        return (self.iosapp_data_state not in [NOT_HOME, NOT_SET])

    @property
    def isnot_inzone_iosapp_state(self):
        return (self.iosapp_data_state in [NOT_HOME, NOT_SET])

    @property
    def was_inzone(self):
        return (self.sensors[ZONE] not in [NOT_HOME, AWAY, AWAY_FROM, NOT_SET])

    @property
    def wasnot_inzone(self):
        return (self.sensors[ZONE] in [NOT_HOME, AWAY, AWAY_FROM])

    @property
    def is_statzone_trigger_reached(self):
        return self.icloud_update_reason.startswith('Stationary')

#--------------------------------------------------------------------
    @property
    def is_in_statzone(self):
        return self.StatZone is not None

    @property
    def isnot_in_statzone(self):
        return self.StatZone is None

    @property
    def was_in_statzone(self):
        return (is_statzone(self.sensors[ZONE]))

    @property
    def wasnot_in_statzone(self):
        return (is_statzone(self.sensors[ZONE]) is False)

    @property
    def in_statzone_interval_secs(self):
        if self.DeviceFmZoneHome.calc_dist < 180 or self.iosapp_monitor_flag is False:
            return self.statzone_inzone_interval_secs

        return Gb.max_interval_secs / 2

    # Return the seconds left before the phone should be moved into a Stationary Zone
    @property
    def statzone_timer_left(self):
        if self.is_statzone_timer_set:
            return (self.statzone_timer - time_now_secs())
        else:
            return HIGH_INTEGER

    # Return True if the timer has expired, False if not expired or not using Stat Zone
    @property
    def statzone_timer_reached(self):
        return (self.is_statzone_timer_set and Gb.this_update_secs >= self.statzone_timer)

    @property
    def statzone_move_limit_exceeded(self):
        return (self.statzone_dist_moved_km > Gb.statzone_dist_move_limit_km)

    @property
    def statzone_reset_timer(self):
        '''
        Set the Stationary Zone timer expiration time
        '''
        self.statzone_dist_moved_km = 0
        self.statzone_timer         = Gb.this_update_secs + Gb.statzone_still_time_secs

    @property
    def is_statzone_timer_set(self):
        return self.statzone_timer > 0

    @property
    def statzone_clear_timer(self):
        '''
        Clear the Stationary Zone timer
        '''
        self.statzone_dist_moved_km = 0
        self.statzone_timer         = 0

    def update_distance_moved(self, distance):
        self.statzone_dist_moved_km += distance

        if Gb.evlog_trk_monitors_flag:
            log_msg =  (f"StatZone Movement > "
                        f"TotalMoved-{format_dist_km(self.statzone_dist_moved_km)}, "
                        f"UnderMoveLimit-{self.statzone_dist_moved_km <= Gb.statzone_dist_move_limit_km}, "
                        f"Timer-{secs_to_time(self.statzone_timer)}, "
                        f"TimerLeft- {self.statzone_timer_left} secs, "
                        f"TimerExpired-{self.statzone_timer_reached}")
            post_monitor_msg(self.devicename, log_msg)

        return self.statzone_dist_moved_km

#--------------------------------------------------------------------
    def pause_tracking(self):
        '''
        Pause tracking the device
        '''
        try:
            self.tracking_status = TRACKING_PAUSED

            self.write_ha_sensor_state(NEXT_UPDATE, PAUSED)
            self.display_info_msg(PAUSED)

        except Exception as err:
            log_exception(err)
            pass

#--------------------------------------------------------------------
    @property
    def is_tracking_paused(self):
        '''
        Return:
            True    Device is paused
            False   Device not pause
        '''
        try:
            return (self.tracking_status == TRACKING_PAUSED)

        except Exception as err:
            log_exception(err)
            return False

#--------------------------------------------------------------------
    def resume_tracking(self, delay_secs=0):
        '''
        Resume tracking
        '''
        try:
            self.tracking_status             = TRACKING_RESUMED
            Gb.all_tracking_paused_flag      = False
            Gb.any_device_was_updated_reason = ''

            Gb.iCloud3.initialize_5_sec_loop_control_flags()

            if Gb.primary_data_source_ICLOUD is False or self.is_data_source_ICLOUD is False:
                self.write_ha_sensor_state(NEXT_UPDATE, '___')
                return

            for DeviceFmZone in self.DeviceFmZones_by_zone.values():
                DeviceFmZone.next_update_secs = delay_secs
                DeviceFmZone.next_update_time = HHMMSS_ZERO if delay_secs == 0 \
                                                            else secs_to_time(Gb.this_update_secs + delay_secs)

            self.DeviceFmZoneNextToUpdate     = self.DeviceFmZoneHome
            self.next_update_secs             = delay_secs

            self.old_loc_poorgps_cnt          = 0
            self.old_loc_poor_gps_msg         = ''
            self.poor_gps_flag                = False
            self.outside_no_exit_trigger_flag = False
            self.dev_data_device_status       = "Online"
            self.dev_data_device_status_code  = 200
            self.icloud_update_reason          = 'Trigger > Resume/Relocate'
            self.icloud_no_update_reason       = ''
            self.icloud_initial_locate_done    = False

            self.iosapp_request_loc_first_secs = 0
            self.iosapp_request_loc_last_secs  = 0
            self.passthru_zone_timer           = 0

            self.write_ha_sensor_state(NEXT_UPDATE, RESUMING)
            self.display_info_msg(RESUMING)

        except Exception as err:
            log_exception(err)

#--------------------------------------------------------------------
    @property
    def is_tracking_resumed(self):
        '''
        Return
            True    Device is resuming tracking
            False   Device tracking is normal
        '''
        try:
            return (self.tracking_status == TRACKING_RESUMED)

        except Exception as err:
            log_exception(err)
            return False

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   PASSTHRU (ENTER ZONE) DELAY FUNCTIONS
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    @property
    def is_passthru_timer_set(self):
        return (self.passthru_zone_timer > 0)

    @property
    def is_passthru_zone_delay_active(self):
        '''
        See if the device has just entered a non-tracked zone. If it is and
        it's timer has expired, reset the timer

        Return:
            True - Device is still waiting to see if it is ina zone
            False - It is not or the timerhas expired
        '''
        # Not used, not Active
        if Gb.is_passthru_zone_used is False or self.is_passthru_timer_set is False:
            return False

        # Active and has not expired
        if Gb.this_update_secs < self.passthru_zone_timer:
            return True

        # Expired
        self.passthru_zone_timer = 0

        return False

#--------------------------------------------------------------------
    def set_passthru_zone_delay(self, data_source, zone_entered=None, zone_entered_secs=0):
        '''
        The iOS App may have entered a non-tracked zone. If so, it might be just passing thru the zone and
        not staying in it. Check the passthru_zone_timer to see if the 1-min enter zone delay is still
        in effect or if has expired.

        Return:
            True - Set up passthru delay or it is already set up
            False - Zone was reset and should proceed with an update
        '''
        # Passthru zone is not used or already set up
        if (zone_entered == self.passthru_zone
                or zone_entered == self.loc_data_zone):
            return True

        # Entering a zone not subject to a delay
        if (zone_entered in self.DeviceFmZones_by_zone
                or is_statzone(zone_entered)
                or zone_entered is None
                or (data_source == ICLOUD and self.is_location_old_or_gps_poor)):
            return False

        # Not set and next update not reached, set it below
        elif self.is_passthru_timer_set is False and self.is_next_update_time_reached is False:
            pass

        # Time for an update, reset it
        elif self.is_next_update_time_reached:
            self.reset_passthru_zone_delay()
            return False

        # Passthru expire is set, if before enter zone time or this update time, reset it
        elif (self.is_passthru_timer_set
                and (zone_entered_secs > self.passthru_zone_timer
                        or Gb.this_update_secs >= self.passthru_zone_timer)):
            self.reset_passthru_zone_delay()
            return False

        # Activate Passthru zone
        det_interval.update_all_device_fm_zone_sensors_interval(self, Gb.passthru_zone_interval_secs)

        self.passthru_zone_timer = Gb.this_update_secs + Gb.passthru_zone_interval_secs
        self.passthru_zone = zone_entered

        event_msg =(f"Enter Zone Delayed > {zone_display_as(self.passthru_zone)}, "
                    f"DelayFor-{secs_to_time_str(Gb.passthru_zone_interval_secs)}")
        post_event(self.devicename, event_msg)

        info_msg = (f"Enter Zone Delayed - {zone_display_as(self.passthru_zone)}, "
                    f"Expires-{secs_to_time(self.passthru_zone_timer)} "
                    f"({secs_to_time_str(secs_to(self.passthru_zone_timer))})")
        self.display_info_msg(info_msg)

        return True

#--------------------------------------------------------------------
    def reset_passthru_zone_delay(self):

        if Gb.is_passthru_zone_used is False or self.is_passthru_timer_set is False:
            return

        # event_msg =(f"Enter Zone Delay Ended > {zone_display_as(self.passthru_zone)}")
        # post_event(self.devicename, event_msg)

        self.passthru_zone_timer = 0
        self.passthru_zone = ''

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   NEXT UPDATE TIME AND DISTANCE FUNCTIONS
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    @property
    def is_next_update_time_reached(self):
        '''
        Check to see if any of this Device's DeviceFmZone items will
        need to be updated within the next 5-secs

        Return:
            True    Next update time reached
            False   Next update time not reached
        '''
        if self.icloud_initial_locate_done is False or self.is_tracking_resumed:
            return True

        return Gb.this_update_secs >= self.DeviceFmZoneNextToUpdate.next_update_secs

#
#--------------------------------------------------------------------
    def _set_next_DfZ_to_update(self):
        '''
        Cycle thru the DeviceFmZones and get the lowest (next) updated secs

        Return:
            next_update_secs for the DeviceFmZone that will be updaed next
        Sets:
            DeviceFmZoneNextToUpdate to the object
        '''
        if self.only_track_from_home:
            return self.next_update_secs

        self.next_update_secs = HIGH_INTEGER
        self.DeviceFmZoneNextToUpdate = None
        for DeviceFmZone in self.DeviceFmZones_by_zone.values():
            if DeviceFmZone.next_update_secs <= self.next_update_secs:
                self.next_update_secs = DeviceFmZone.next_update_secs
                self.DeviceFmZoneNextToUpdate = DeviceFmZone

        if self.DeviceFmZoneNextToUpdate is None:
            self.DeviceFmZoneNextToUpdate = self.DeviceFmZoneHome
            self.next_update_secs = self.DeviceFmZoneHome.next_update_secs

        return self.next_update_secs

#--------------------------------------------------------------------
    def calculate_distance_moved(self):
        '''
        Calculate the distance (km) from the last updated location to
        the current location
        '''
        if self.sensor_zone == NOT_SET:
            self.loc_data_dist_moved_km = 0
        else:
            self.loc_data_dist_moved_km = calc_distance_km(self.sensors[GPS], self.loc_data_gps)
        self.loc_data_time_moved_from = self.sensors[LAST_LOCATED_DATETIME]
        self.loc_data_time_moved_to   = self.loc_data_datetime


#--------------------------------------------------------------------
    def distance_m(self, to_latitude, to_longitude):
        to_gps = (to_latitude, to_longitude)
        distance = calc_distance_m(self.loc_data_gps, to_gps)
        distance = 0 if distance < .002 else distance

        return distance

    def distance_km(self, to_latitude, to_longitude):
        to_gps = (to_latitude, to_longitude)
        distance = calc_distance_km(self.loc_data_gps, to_gps)
        distance = 0 if distance < .00002 else distance

        return distance

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   UPDATE DEVICE_TRACKER AND SENSORS FUNCTIONS
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def write_ha_device_tracker_state(self):
        ''' Update the device_tracker entity for this device '''

        if self.DeviceTracker:
            self.DeviceTracker.write_ha_device_tracker_state()

        self._update_restore_state_values()

#--------------------------------------------------------------------
    def write_ha_sensor_state(self, sensor_name, sensor_value):
        '''
        Display a value in a ic3 sensor field

        Input:
            sensor_name     Attribute field name (LOCATED_DATETIME)
            sensor_value    Value that should be displayed (self.loc_data_datetime)
        '''
        if instr(sensor_name, BATTERY) and self.sensors[BATTERY] < 1:
            return

        self.sensors[sensor_name] = sensor_value

        self.write_ha_sensors_state([sensor_name])

#--------------------------------------------------------------------
    def write_ha_sensors_state(self, sensors=None):
        ''' Update the sensors for the Device that are in the sensor_list '''

        if sensors:
            update_sensors_list = {k:v  for sensor in sensors
                                        for k, v in self.Sensors.items()
                                        if k == sensor}
        else:
            update_sensors_list = self.Sensors

        try:
            if (BATTERY in update_sensors_list
                    and BATTERY in self.sensors
                    and self.sensors[BATTERY] < 1):
                update_sensors_list.pop(BATTERY, None)
                update_sensors_list.pop(BATTERY_STATUS, None)
                update_sensors_list.pop(BATTERY_SOURCE, None)
        except:
            pass

        for sensor, Sensor in update_sensors_list.items():
            Sensor.write_ha_sensor_state()

        self._update_restore_state_values()

#--------------------------------------------------------------------
    def write_ha_device_from_zone_sensors_state(self, sensors=None):
        ''' Update the sensors for the Device that are in the sensor_list '''

        if sensors:
            update_sensors_list = {k:v  for sensor in sensors
                                        for k, v in self.Sensors_from_zone.items()
                                        if k.startswith(sensor)}
        else:
            update_sensors_list = self.Sensors_from_zone

        for sensor, Sensor in update_sensors_list.items():
            Sensor.write_ha_sensor_state()

#--------------------------------------------------------------------
    def _update_restore_state_values(self):
        """ Save the Device's updated sensors in the icloud3.restore_state file """

        if self.update_sensors_flag is False:
            return

        Gb.restore_state_devices[self.devicename] = {}
        Gb.restore_state_devices[self.devicename]['last_update'] = datetime_now()
        Gb.restore_state_devices[self.devicename]['sensors'] = copy.deepcopy(self.sensors)

        Gb.restore_state_devices[self.devicename]['from_zone'] = {}
        for from_zone, DeviceFmZone in self.DeviceFmZones_by_zone.items():
            Gb.restore_state_devices[self.devicename]['from_zone'][from_zone] = copy.deepcopy(DeviceFmZone.sensors)

        restore_state.write_storage_icloud3_restore_state_file()

#--------------------------------------------------------------------
    @property
    def badge_sensor_value(self):
        """ Determine the badge sensor state value """

        try:
            # Tracking Paused
            if self.is_tracking_paused:
                sensor_value = PAUSED_CAPS

            # Display zone name if in a zone
            elif self.loc_data_zone != NOT_HOME and self.isnot_in_statzone:
                sensor_value = self.loc_data_zone_fname

            # Display the distance to Home
            elif self.DeviceFmZoneHome:
                sensor_value = format_km_to_mi(self.DeviceFmZoneHome.zone_dist)

            else:
                sensor_value = BLANK_SENSOR_FIELD

        except Exception as err:
            log_exception(err)
            sensor_value = BLANK_SENSOR_FIELD

        return sensor_value


#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   CALCULATE THE OLD LOCATION THRESHOLD FOR THE DEVICE
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def calculate_old_location_threshold(self):
        """
        The old_loc_threshold_secs is used to determine if the Device's location is too
        old to be used. If it is too old, the Device's location will be requested again
        using an interval calculated in the determine_interval_after_error routine. The
        old_loc_threshold_secs is recalculated each time the Device's location is
        updated.
        """
        try:
            # Device is approaching a TrackFmZone (distance less than 1-km, on a 15-secs
            # interval). Set threshold to 15-secs so the location will be updated
            # immediately.
            if self.is_approaching_tracked_zone:
                self.old_loc_threshold_secs = 30 + Gb.old_location_adjustment
                return

            # Get smallest interval of all zones being tracked from
            interval = HIGH_INTEGER
            for from_zone, DeviceFmZone in self.DeviceFmZones_by_zone.items():
                if DeviceFmZone.interval_secs < interval:
                    interval = DeviceFmZone.interval_secs

            threshold_secs = 60
            if self.is_inzone:
                threshold_secs = interval * .025        # 2.5% of interval time
                if threshold_secs < 120: threshold_secs = 120

            elif self.DeviceFmZoneBeingUpdated.zone_dist > 5:
                threshold_secs = 180

            elif interval < 90:
                threshold_secs = 60
            else:
                threshold_secs = interval * .125

            if self.is_passthru_timer_set:
                threshold_secs = 15
            elif threshold_secs < 60:
                threshold_secs = 60
            elif threshold_secs > 600:
                threshold_secs = 600

            if (Gb.old_location_threshold > 0
                    and threshold_secs > Gb.old_location_threshold):
                threshold_secs = Gb.old_location_threshold

            self.old_loc_threshold_secs = threshold_secs + Gb.old_location_adjustment

        except Exception as err:
            log_exception(err)
            post_internal_error('Calc Old Threshold', traceback.format_exc)
            self.old_loc_threshold_secs = 120

#--------------------------------------------------------------------
    def is_location_data_rejected(self):
        '''
        Post an event message describing the location/gps status of the data being used
        '''
        if (self.is_location_gps_good
                or self.is_dev_data_source_NOT_SET
                #or self.old_loc_poor_gps_cnt < 2
                or self.loc_data_secs > self.last_update_loc_secs
                or self.is_offline is False):
            return False

        try:
            interval, error_cnt, max_error_cnt = det_interval.get_error_retry_interval(self)
            det_interval.update_all_device_fm_zone_sensors_interval(self, interval)

            if self.old_loc_poor_gps_cnt < 2:
                return False

            reason_msg = ''

            if self.is_tracked:
                if self.loc_data_isold:
                    reason_msg = (f"Old>{secs_to_time_str(self.old_loc_threshold_secs)}")
                elif self.loc_data_ispoorgps:
                    reason_msg = (f"PoorGPS>{Gb.gps_accuracy_threshold}m")

            event_msg =(f"Rejected #{self.old_loc_poor_gps_cnt} > "
                        f"{self.dev_data_source}-{self.loc_data_time_gps}, "
                        f"{secs_to_age_str(self.loc_data_secs)}, "
                        f"{reason_msg}, "
                        f"NextUpdate-{secs_to_time(self.next_update_secs)} "
                        f"({secs_to_time_str(interval)}), "
                        f"LastUpdate-{secs_to_age_str(self.last_update_loc_secs)}")

            post_event(self.devicename, event_msg)

        except Exception as err:
            log_exception(err)

        return True

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   UPDATE DISTANCE TO OTHER DEVICES
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def update_distance_to_other_devices(self):
        '''
        Cycle through all devices and update this device's and the other device's
        dist_to_other_device_info field

        {devicename: [distance_m, gps_accuracy_factor, display_text]}
        '''

        for _devicename, _Device in Gb.Devices_by_devicename_tracked.items():
            if _Device is self:
                continue

            if self.sensor_zone == _Device.sensor_zone and self.is_inzone:
                is_location_old = False
            else:
                is_location_old = ((secs_since(_Device.loc_data_secs) > _Device.old_loc_threshold_secs * 1.5)
                                        or (secs_since(self.loc_data_secs) > self.old_loc_threshold_secs * 1.5))

            if is_location_old:
                continue

            dist_apart_m        = _Device.distance_m(self.loc_data_latitude, self.loc_data_longitude)
            min_gps_accuracy    = (min(self.loc_data_gps_accuracy, _Device.loc_data_gps_accuracy))
            gps_accuracy_factor = round(min_gps_accuracy * dist_apart_m / NEAR_DEVICE_DISTANCE)

            if dist_apart_m > 500:
                display_text = f"{dist_apart_m/1000:.1f}km/±{min_gps_accuracy}m"
            else:
                display_text = f"{dist_apart_m:.0f}m/±{min_gps_accuracy}m"

            # distance_apart_data = [dist_apart_m, gps_accuracy_factor, display_text]
            distance_apart_data = [dist_apart_m, min_gps_accuracy, display_text]

            if (_devicename not in self.dist_to_other_devices
                    or self.devicename not in _Device.dist_to_other_devices
                    or _Device.dist_to_other_devices[self.devicename] != distance_apart_data
                    or self.dist_to_other_devices[_devicename] != distance_apart_data):
                before_s = self.dist_to_other_devices.get(_devicename)

                self.dist_to_other_devices[_devicename] = distance_apart_data
                self.dist_to_other_devices_datetime = datetime_now()
                _Device.dist_to_other_devices[self.devicename] = distance_apart_data

                Gb.dist_to_other_devices_update_sensor_list.add(self.devicename)
                Gb.dist_to_other_devices_update_sensor_list.add(_devicename)

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   UPDATE BATTERY INFORMATION
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def update_iosapp_battery_information(self):
        '''
        Update the battery info from the iOS App if the iOS App data is newer than the FamShr
        battery info. Then update the sensors if it has changed.

        sensor.gary_iphone_app_battery_level entity_attrs={'unit_of_measurement': '%', 'device_class':
            'battery', 'icon': 'mdi:battery-charging-80', 'friendly_name': 'Gary-iPhone-app Battery Level',
            'state': '82', 'last_changed_secs': 1680080444, 'last_changed_time': '5:00:44a'},
        sensor.gary_iphone_app_battery_state entity_attrs={'Low Power Mode': False,
            'icon': 'mdi:battery-charging-80', 'friendly_name': 'Gary-iPhone-app Battery State',
            'state': 'charging', 'last_changed_secs': 1680080444, 'last_changed_time': '5:00:44a'}

        Return:
            True - Data has changed
            False - Data has not changed
        '''

        try:
            if self.iosapp_entity[BATTERY_LEVEL] is None:
                return False
            if self.icloud_initial_locate_done is False:
                return

            try:
                battery_level_attrs = entity_io.get_attributes(self.iosapp_entity[BATTERY_LEVEL])

                if STATE not in battery_level_attrs: return False

                battery_level       = int(battery_level_attrs[STATE])
                battery_update_secs = battery_level_attrs[LAST_CHANGED_SECS]

            except Exception as err:
                #log_exception(err)
                return False

            if battery_update_secs > self.dev_data_battery_update_secs:
                battery_status = entity_io.get_state(self.iosapp_entity[BATTERY_STATUS])

                self.dev_data_battery_source = IOSAPP_FNAME
                self.dev_data_battery_level  = self.iosapp_data_battery_level  = battery_level
                self.dev_data_battery_status = self.iosapp_data_battery_status = battery_status if battery_status else UNKNOWN
                self.dev_data_battery_update_secs = self.iosapp_data_battery_update_secs = battery_update_secs

            # If the level and status has not changed, nothing to do
            if (self.dev_data_battery_level == self.sensors[BATTERY]
                    and self.dev_data_battery_status.lower() == self.sensors[BATTERY_STATUS].lower()):
                return False

            elif self.dev_data_battery_level < 1 or self.sensors[BATTERY] < 1:
                return False

            self.dev_data_battery_level_last = self.sensors[BATTERY]
            self.sensors[BATTERY]        = self.dev_data_battery_level
            self.sensors[BATTERY_SOURCE] = self.dev_data_battery_source
            self.sensors[BATTERY_STATUS] = self.format_battery_status
            self.sensors[BATTERY_UPDATE_TIME] = self.format_battery_time

            self.write_ha_sensors_state([BATTERY, BATTERY_STATUS])

            return True

        except Exception as err:
            log_exception(err)
            return False

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   Update the Device data from the iOS App raw data or from the RawData
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def update_dev_loc_data_from_raw_data_IOSAPP(self, RawData=None):
        if (self.iosapp_data_secs <= self.loc_data_secs
                or self.iosapp_data_secs == 0):
            return

        self.last_data_update_secs = time_now_secs()

        self.dev_data_source            = IOSAPP_FNAME
        self.dev_data_fname             = self.fname
        self.dev_data_device_class      = self.device_type
        self.dev_data_device_status     = "Online"
        self.dev_data_device_status_code = 200

        if (self.iosapp_data_battery_level > 0
                and self.iosapp_data_battery_status
                and self.iosapp_data_battery_update_secs > self.dev_data_battery_update_secs):
            self.dev_data_battery_source = IOSAPP_FNAME
            self.dev_data_battery_level  = self.iosapp_data_battery_level
            self.dev_data_battery_status = self.iosapp_data_battery_status
            self.dev_data_battery_update_secs = self.iosapp_data_battery_update_secs

        self.loc_data_latitude          = self.iosapp_data_latitude
        self.loc_data_longitude         = self.iosapp_data_longitude
        self.loc_data_gps_accuracy      = self.iosapp_data_gps_accuracy
        self.loc_data_vertical_accuracy = self.iosapp_data_vertical_accuracy
        self.loc_data_altitude          = self.iosapp_data_altitude
        self.loc_data_secs              = self.iosapp_data_secs
        self.loc_data_datetime          = secs_to_datetime(self.iosapp_data_secs)
        self.loc_data_time              = secs_to_time(self.iosapp_data_secs)

        self.calculate_distance_moved()
        self.update_distance_to_other_devices()
        self.write_ha_sensor_state(LAST_LOCATED, self.loc_data_time)
        self.display_update_location_msg()

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def update_dev_loc_data_from_raw_data_FAMSHR_FMF(self, RawData, requesting_device_flag=True):
        '''
        Update the Device's location data with the RawData (FamShr or FmF) from the iCloud Account.

        Parameters:
            RawData - FamShr or FmF object to be used to update this Device
            requesting_device_flag - Multiple devices can be updated since all device info is returned
                    from iCloud on a location request.
                        True-   This is the Device that requested the update and the Update Location
                                info should be displayed in the Event Log
                        False - This is another device and do not display the Update Location msg
        '''
        if (LOCATION not in RawData.device_data
                or RawData.device_data[LOCATION] is None
                or (RawData.location_secs <= self.loc_data_secs and self.loc_data_secs > 0)):
            return

        self.last_data_update_secs = time_now_secs()

        location                       = RawData.device_data[LOCATION]
        location_secs                  = RawData.location_secs
        RawData.last_used_location_secs = RawData.location_secs
        RawData.last_used_location_time = RawData.location_time

        self.dev_data_source           = RawData.data_source
        self.dev_data_fname            = RawData.device_data.get(NAME, "")
        self.dev_data_device_class     = RawData.device_data.get(ICLOUD_DEVICE_CLASS, "")
        self.dev_data_low_power_mode   = RawData.device_data.get(ICLOUD_LOW_POWER_MODE, "")

        icloud_rawdata_battery_level = round(RawData.device_data.get(ICLOUD_BATTERY_LEVEL, 0) * 100)
        icloud_rawdata_battery_status = RawData.device_data.get(ICLOUD_BATTERY_STATUS, '')
        if (RawData.is_data_source_FAMSHR
                and icloud_rawdata_battery_level > 0
                and icloud_rawdata_battery_status
                and location_secs > self.dev_data_battery_update_secs):
            self.dev_data_battery_source = RawData.data_source
            self.dev_data_battery_level  = icloud_rawdata_battery_level
            self.dev_data_battery_status = icloud_rawdata_battery_status
            self.dev_data_battery_update_secs = location_secs

        self.dev_data_device_status_code = RawData.device_data.get(ICLOUD_DEVICE_STATUS, 0)
        self.dev_data_device_status      = DEVICE_STATUS_CODES.get(self.dev_data_device_status_code, UNKNOWN)

        self.loc_data_latitude       = location.get(LATITUDE, 0)
        self.loc_data_longitude      = location.get(LONGITUDE, 0)
        self.loc_data_gps_accuracy   = round(location.get(ICLOUD_HORIZONTAL_ACCURACY, 0))
        self.loc_data_secs           = location_secs
        self.loc_data_datetime       = secs_to_datetime(location_secs)
        self.loc_data_time           = secs_to_time(location_secs)
        self.loc_data_altitude       = float(f"{location.get(ALTITUDE, 0):.1f}")
        self.loc_data_vert_accuracy  = round(location.get(ICLOUD_VERTICAL_ACCURACY, 0))
        self.loc_data_isold          = location.get('isOld', False)
        self.loc_data_ispoorgps      = location.get('isInaccurate', False)

        self.calculate_distance_moved()
        self.update_distance_to_other_devices()
        self.write_ha_sensor_state(LAST_LOCATED, self.loc_data_time)
        if requesting_device_flag or self.is_monitored:
            self.display_update_location_msg()

#-------------------------------------------------------------------
    def display_update_location_msg(self):

        if self.loc_data_time_gps == self.last_loc_data_time_gps:
            return

        if self.isnot_inzone or self.moved_since_last_update > .015:
            event_msg =(f"Updated > {self.dev_data_source}-"
                        f"{self.last_loc_data_time_gps}"
                        f"{RARROW}{self.loc_data_time_gps} "
                        f"({secs_to_age_str(self.loc_data_secs)}), "
                        f"Moved-{format_dist_km(self.moved_since_last_update)}")
            post_event(self.devicename,event_msg)

        self.last_loc_data_time_gps = self.loc_data_time_gps

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def update_sensor_values_from_data_fields(self):
        #Note: Final prep and update device attributes via
        #device_tracker.see. The gps location, battery, and
        #gps accuracy are not part of the attrs variable and are
        #reformatted into device attributes by 'See'. The gps
        #location goes to 'See' as a "(latitude, longitude)" pair.
        #'See' converts them to LATITUDE and LONGITUDE
        #and discards the 'gps' item.

        # Determine the soonest DeviceFmZone to update, then get the sensor
        # values to be displayed with the Device sensors

        try:
            self._set_next_DfZ_to_update()

            # self.sensors_um   = {}
            # self.sensors_icon = {}

            # Device related sensors
            if self.dev_data_battery_level > 1:
                self.sensors[BATTERY]          = self.dev_data_battery_level
                self.sensors[BATTERY_STATUS]   = self.format_battery_status
                self.sensors[BATTERY_SOURCE]   = self.dev_data_battery_source
                self.sensors[BATTERY_UPDATE_TIME] = self.format_battery_time

            self.sensors[DEVICE_STATUS]        = self.device_status
            self.sensors[LOW_POWER_MODE]       = self.dev_data_low_power_mode
            self.sensors[BADGE]                = self.badge_sensor_value
            self.sensors[INFO]                 = self.format_info_msg

            # Location related items
            self.sensors[GPS]                  = (self.loc_data_latitude, self.loc_data_longitude)
            self.sensors[LATITUDE]             = self.loc_data_latitude
            self.sensors[LONGITUDE]            = self.loc_data_longitude
            self.sensors[GPS_ACCURACY]         = self.loc_data_gps_accuracy
            self.sensors[ALTITUDE]             = self.loc_data_altitude
            self.sensors[VERT_ACCURACY]        = self.loc_data_vert_accuracy
            self.sensors[LOCATION_SOURCE]      = self.dev_data_source
            self.sensors[TRIGGER]              = self.trigger
            self.sensors[LAST_LOCATED_DATETIME]= self.loc_data_datetime
            self.sensors[LAST_LOCATED_TIME]    = self.loc_data_time
            self.sensors[LAST_LOCATED]         = self.loc_data_time
            self.sensors[DISTANCE_TO_DEVICES]  = self.dist_apart_msg.rstrip(', ')
            self.sensors[MOVED_DISTANCE]       = self.loc_data_dist_moved_km
            self.sensors[MOVED_TIME_FROM]      = self.loc_data_time_moved_from
            self.sensors[MOVED_TIME_TO]        = self.loc_data_time_moved_to

            self.interval_secs                 = self.DeviceFmZoneNextToUpdate.interval_secs
            self.interval_str                  = self.DeviceFmZoneNextToUpdate.interval_str
            self.next_update_secs              = self.DeviceFmZoneNextToUpdate.next_update_secs
            self.sensors[INTERVAL]             = self.DeviceFmZoneNextToUpdate.sensors[INTERVAL]
            self.sensors[NEXT_UPDATE_DATETIME] = self.DeviceFmZoneNextToUpdate.sensors[NEXT_UPDATE_DATETIME]
            self.sensors[NEXT_UPDATE_TIME]     = self.DeviceFmZoneNextToUpdate.sensors[NEXT_UPDATE_TIME]
            self.sensors[NEXT_UPDATE]          = self.DeviceFmZoneNextToUpdate.sensors[NEXT_UPDATE]

            self.sensors[FROM_ZONE]            = self.DeviceFmZoneClosest.from_zone
            self.sensors[LAST_UPDATE_DATETIME] = self.DeviceFmZoneClosest.sensors[LAST_UPDATE_DATETIME]
            self.sensors[LAST_UPDATE_TIME]     = self.DeviceFmZoneClosest.sensors[LAST_UPDATE_TIME]
            self.sensors[LAST_UPDATE]          = self.DeviceFmZoneClosest.sensors[LAST_UPDATE]
            self.sensors[TRAVEL_TIME_MIN]      = self.DeviceFmZoneClosest.sensors[TRAVEL_TIME_MIN]
            self.sensors[TRAVEL_TIME]          = self.DeviceFmZoneClosest.sensors[TRAVEL_TIME]
            self.sensors[ZONE_DISTANCE]        = self.DeviceFmZoneClosest.sensors[ZONE_DISTANCE]
            self.sensors[ZONE_DISTANCE_M]      = self.DeviceFmZoneClosest.sensors[ZONE_DISTANCE_M]
            self.sensors[ZONE_DISTANCE_M_EDGE] = self.DeviceFmZoneClosest.sensors[ZONE_DISTANCE_M_EDGE]
            self.sensors[MAX_DISTANCE]         = self.DeviceFmZoneClosest.sensors[MAX_DISTANCE]
            self.sensors[WAZE_DISTANCE]        = self.DeviceFmZoneClosest.sensors[WAZE_DISTANCE]
            self.sensors[WAZE_METHOD]          = self.DeviceFmZoneClosest.sensors[WAZE_METHOD]
            self.sensors[CALC_DISTANCE]        = self.DeviceFmZoneClosest.sensors[CALC_DISTANCE]
            self.sensors[HOME_DISTANCE]        = self.DeviceFmZoneHome.sensors[ZONE_DISTANCE]
            self.DeviceFmZoneClosest.dir_of_travel = dir_of_travel = \
                    self.DeviceFmZoneClosest.sensors[DIR_OF_TRAVEL]

            # If moving towards a tracked from zone, change the direction to 'To-[zonename]'
            from_zone = zone_display_as(self.sensors[FROM_ZONE]).replace(' ', '')[:8]
            if dir_of_travel in [TOWARDS, AWAY_FROM]:
                self.sensors[DIR_OF_TRAVEL] = dir_of_travel if self.is_tracked_from_home else from_zone

            elif dir_of_travel in [INZONE, STATIONARY_FNAME]:
                self.sensors[DIR_OF_TRAVEL] = f"@{zone_display_as(self.loc_data_zone)[:8]}"

            else:
                self.sensors[DIR_OF_TRAVEL] = dir_of_travel

            # Update the last zone info if the device was in a zone and now not in a zone or went immediatelly from
            # one zone to another (it was in a zone and still is in a zone and the old zone is differenent than the new zone)
            if (self.wasnot_in_statzone
                    and (self.was_inzone and self.isnot_inzone)
                    or  (self.was_inzone and self.is_inzone and self.sensors[ZONE] != self.loc_data_zone)):
                self.sensors[LAST_ZONE]            = self.sensors[ZONE]
                self.sensors[LAST_ZONE_DISPLAY_AS] = self.sensors[ZONE_DISPLAY_AS]
                self.sensors[LAST_ZONE_NAME]       = self.sensors[ZONE_NAME]
                self.sensors[LAST_ZONE_FNAME]      = self.sensors[ZONE_FNAME]
                self.sensors[LAST_ZONE_DATETIME]   = secs_to_datetime(time_now_secs())

            if Zone := Gb.Zones_by_zone.get(self.loc_data_zone):
                self.sensors[ZONE] = self.loc_data_zone
            else:
                Zone = Gb.HomeZone
                self.sensors[ZONE] = self.loc_data_zone = HOME

            self.sensors[ZONE_DISPLAY_AS] = Zone.display_as
            self.sensors[ZONE_NAME]  = Zone.name
            self.sensors[ZONE_FNAME] = Zone.fname

            self.last_update_loc_secs = self.loc_data_secs
            self.last_update_loc_time = self.loc_data_time
            self.last_update_gps_accuracy = self.loc_data_gps_accuracy

            self._set_sensors_special_icon()

        except Exception as err:
            post_internal_error('Set Attributes', traceback.format_exc)

#----------------------------------------------------------------------------
    def _set_sensors_special_icon(self):
        '''
        Determine if the sensor icon should be customized for the sensor's value. If so,
        set it.

        The values are:
            - zone sensosr: icons are home or for a generic zone
            - direction-of-travel sensor:  based on towards, away from or inzone
            - next_update sensor: icon when the time is for a track-from-zone
        '''

        self.sensors_icon = {}
        for sensor_name in SENSOR_LIST_ZONE_NAME:
            zone = self.sensors[sensor_name]
            if is_statzone(zone):
                self.sensors_icon[sensor_name] = SENSOR_ICONS[INZONE_STATIONARY]
            if zone in [HOME, HOME_FNAME]:
                self.sensors_icon[sensor_name] = SENSOR_ICONS[INZONE_HOME]

        dir_of_travel = self.sensors[DIR_OF_TRAVEL]
        if dir_of_travel == TOWARDS:
            icon = TOWARDS_HOME if self.is_tracked_from_home else TOWARDS
            self.sensors_icon[DIR_OF_TRAVEL] = SENSOR_ICONS[icon]

        elif dir_of_travel == AWAY_FROM:
            icon = AWAY_FROM_HOME if self.is_tracked_from_home else AWAY_FROM
            self.sensors_icon[DIR_OF_TRAVEL] = SENSOR_ICONS[icon]

        elif dir_of_travel.startswith('@') or dir_of_travel in [INZONE, STATIONARY_FNAME]:
            if self.loc_data_zone == HOME:
                self.sensors_icon[DIR_OF_TRAVEL] = SENSOR_ICONS[INZONE_HOME]
            elif self.is_in_statzone:
                self.sensors_icon[DIR_OF_TRAVEL] = SENSOR_ICONS[INZONE_STATIONARY]
            else:
                self.sensors_icon[DIR_OF_TRAVEL] = SENSOR_ICONS[INZONE]

        if self.DeviceFmZoneNextToUpdate.from_zone != HOME:
            self.sensors_icon[NEXT_UPDATE] = \
                    f"mdi:alpha-{self.DeviceFmZoneNextToUpdate.from_zone[:1]}-circle"
                    # f"mdi:alpha-{self.DeviceFmZoneNextToUpdate.from_zone[:1]}-circle-outline"
                    # f"mdi:alpha-{self.DeviceFmZoneNextToUpdate.from_zone[:1]}-box-outline"

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   INFO MESSAGES AND OTHER SUPPORT FUNCTIONSS
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    @property
    def format_info_msg(self):
        """
        Analyze the Device's fields.

        Return: Info text to be displayed in the info field
        """
        try:
            if self.is_passthru_zone_delay_active:
                info_msg = (f"Enter Zone Delayed - {zone_display_as(self.passthru_zone)}, "
                    f"Expires-{secs_to_time(self.passthru_zone_timer)} "
                    f"({secs_to_time_str(secs_to(self.passthru_zone_timer))})")
                return info_msg

            # info_msg = f"{DOT}"
            info_msg = ''
            if Gb.info_notification != '':
                info_msg = f"◈◈ {Gb.info_notification} ◈◈"
                Gb.info_notification = ''

            if self.offline_secs > 0:
                info_msg +=(f"DeviceOffline@{secs_to_time_age_str(self.offline_secs)} "
                            f"({self.device_status}) ")

            if (self.is_statzone_timer_set
                    and secs_to(self.statzone_timer) < 90
                    and self.sensors[MOVED_DISTANCE] == 0):
                info_msg += (f"IntoStatZone-{secs_to_time(self.statzone_timer)}, ")

            elif self.zone_change_secs > 0:
                if self.is_inzone:
                    info_msg += f"@{zone_display_as(self.loc_data_zone)}-"
                else:
                    info_msg += f"Left-{zone_display_as(self.sensors[LAST_ZONE])}-"
                info_msg += f"{secs_to_time_age_str(self.zone_change_secs)}, "

            if self.sensors[FROM_ZONE] and self.sensors[FROM_ZONE] != NOT_SET and self.sensors[FROM_ZONE] != HOME:
                from_zone = self.sensors[FROM_ZONE]
                Zone = Gb.Zones_by_zone[from_zone]
                info_msg += f"FromZone-{Zone.display_as}, "

            # if self.DeviceFmZoneNextToUpdate is not self.DeviceFmZoneHome:
            #     info_msg += f"NextUpdateFor-{self.DeviceFmZoneNextToUpdate.from_zone_display_as[:8]}, "

            if self.NearDeviceUsed:
                info_msg +=(f"UsedNearbyDevice-{self.NearDeviceUsed.fname}, "
                            f"({format_dist_m(self.near_device_distance)}")

            if self.data_source != self.dev_data_source.lower():
                info_msg += (f"LocSource-{self.dev_data_source}, ")

            # if self.dev_data_battery_level > 0:
            #     info_msg += f"Battery-{self.format_battery_level}, "

            if self.is_gps_poor:
                info_msg += (f"PoorGPS-±{self.loc_data_gps_accuracy}m "
                            f"#{self.old_loc_poor_gps_cnt}")
                if (is_zone(self.loc_data_zone)
                        and Gb.discard_poor_gps_inzone_flag):
                    info_msg += "(Ignored)"
                info_msg += ", "

            if self.old_loc_poor_gps_cnt > 16:
                info_msg += (f"May Be Offline, "
                            f"LocTime-{self.loc_data_12hrtime_age}, "
                            f"OldCnt-#{self.old_loc_poor_gps_cnt}, ")

        except Exception as err:
            log_exception(err)

        self.info_msg = info_msg[:-2]
        return self.info_msg

#-------------------------------------------------------------------
    def display_info_msg(self, info_msg, new_base_msg=False):
        '''
        Display the info msg in the Device's sensor.[devicename]_info entity.

        Parameters:
            info_msg    - message to display
            append_msg  - True = Append the info_msg to the existing info_msg
                        - False = Only display the info_msg
        Return:
            Message text
        '''
        Gb.broadcast_info_msg = None

        # PassThru zone msg has priority over all other messages
        if self.is_passthru_zone_delay_active and instr(info_msg, 'PassThru') is False:
            return
        if new_base_msg is False:
            return

        #info_msg = info_msg if new_base_msg else f"《{info_msg}》{self.info_msg}"

        try:
            self.write_ha_sensor_state(INFO, info_msg)
        except:
            pass

        return info_msg

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def log_data_fields(self):

        if self.NearDevice:
            near_devicename = self.NearDevice.devicename
        else:
            near_devicename = 'None'

        log_msg = ( f"Device Status > {self.devicename} > "
                    f"NearDevice-{near_devicename}, "
                    f"iOSAppZone-{self.iosapp_data_state}, "
                    f"iC3Zone-{self.loc_data_zone}, ")
        if self.DeviceFmZoneHome:
            log_msg += (f"Interval-{self.sensors[INTERVAL]}, "
                        f"TravTime-{self.sensors[TRAVEL_TIME]}, "
                        f"Dist-{self.sensors[HOME_DISTANCE]} {Gb.um}, "
                        f"NextUpdt-{self.sensors[NEXT_UPDATE]}, "
                        f"Dir-{self.sensors[DIR_OF_TRAVEL]}, ")
        log_msg += (f"Moved-{self.sensors[MOVED_DISTANCE]}, "
                    f"LastUpdate-{self.sensors[LAST_UPDATE_TIME]}, "
                    f"IntoStatZone@{secs_to_time(self.statzone_timer)}, "
                    f"GPS-{self.loc_data_fgps}, "
                    f"LocAge-{secs_to_age_str(self.loc_data_secs)}, "
                    f"OldThreshold-{secs_to_time_str(self.old_loc_threshold_secs)}, "
                    f"LastEvLogMsg-{secs_to_time(self.last_evlog_msg_secs)}, "
                    f"Battery-{self.format_battery_level_status_source}@"
                    f"{self.format_battery_time}")

        log_debug_msg(log_msg)
