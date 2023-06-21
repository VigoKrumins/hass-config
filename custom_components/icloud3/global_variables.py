#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   Global Variables Class Object
#
#   Global Variables is a general class to allow access to iCloud3 shared variables from
#   multiple classes. The variable to be referenced is defined in the __init__
#   function with it's default value.
#
#   Usage:
#       The following code is added to the module.py file containing another class
#       that needs access to the shared global variables.
#
#       Add the following code before the class statement:
#           from .globals import GlobalVariables as GbObj
#
#       Add the following code in the __init__ function:
#           def __init(self, var1, var2, ...):
#               global Gb
#               Gb = GbObj.MasterGbObject
#
#       The shared variables can then be shared using the Gb object:
#           Gb.time_format
#           Gb.Zones_by_zone
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

from .const          import (DEVICENAME_IOSAPP, VERSION, NOT_SET, HOME_FNAME, HOME, STORAGE_DIR, WAZE_USED,
                            FAMSHR, FMF, FAMSHR_FMF, ICLOUD, IOSAPP, FNAME, HIGH_INTEGER,
                            DEFAULT_GENERAL_CONF,
                            CONF_UNIT_OF_MEASUREMENT,
                            CONF_DISPLAY_ZONE_FORMAT,
                            CONF_CENTER_IN_ZONE, CONF_DISPLAY_GPS_LAT_LONG,
                            CONF_TRAVEL_TIME_FACTOR, CONF_GPS_ACCURACY_THRESHOLD,
                            CONF_DISCARD_POOR_GPS_INZONE, CONF_OLD_LOCATION_THRESHOLD, CONF_OLD_LOCATION_ADJUSTMENT,
                            CONF_MAX_INTERVAL, CONF_OFFLINE_INTERVAL, CONF_EXIT_ZONE_INTERVAL, CONF_IOSAPP_ALIVE_INTERVAL,
                            CONF_WAZE_REGION, CONF_WAZE_MAX_DISTANCE, CONF_WAZE_MIN_DISTANCE,
                            CONF_WAZE_REALTIME,
                            CONF_WAZE_HISTORY_DATABASE_USED, CONF_WAZE_HISTORY_MAX_DISTANCE ,
                            CONF_WAZE_HISTORY_TRACK_DIRECTION,
                            CONF_STAT_ZONE_FNAME,
                            CONF_STAT_ZONE_BASE_LATITUDE, CONF_STAT_ZONE_BASE_LONGITUDE,
                            CONF_STAT_ZONE_INZONE_INTERVAL, CONF_LOG_LEVEL,
                            CONF_IOSAPP_REQUEST_LOC_MAX_CNT, CONF_DISTANCE_BETWEEN_DEVICES,
                            CONF_PASSTHRU_ZONE_TIME, CONF_TRACK_FROM_BASE_ZONE, CONF_TRACK_FROM_HOME_ZONE,
                            CONF_TFZ_TRACKING_MAX_DISTANCE,

                            CONF_STAT_ZONE_STILL_TIME,
                            CONF_STAT_ZONE_INZONE_INTERVAL,
                            )


import logging
_LOGGER = logging.getLogger("icloud3_cf")

#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
class GlobalVariables(object):
    '''
    Define global variables used in the various iCloud3 modules
    '''
    # Fixed variables set during iCloud3 loading that will not change
    version         = VERSION
    version_evlog   = ''

    hass            = None      # hass: HomeAssistant set in __init__
    config_entry    = None      # hass.config_entry set in __init__ (integration)
    config          = None      # has config parmaeter swt in __init__ (platform)
    entry_id        = None      # Has entry_id for iCloud3
    async_add_entities_sensor = None            # Initial add_entities link passed to sensor during ha startup
    async_add_entities_device_tracker = None    # Initial add_entities link passed to device_tracker during ha startup
    async_executor_call_parameters = None

    ha_location_info= {'country_code': 'us', 'use_metric': False}
    # ha_country_code = 'us'
    # ha_use_metric   = False
    country_code = 'us'
    use_metric   = False

    iCloud3             = None   # iCloud3 Platform object
    OptionsFlowHandler  = None   # config_flow OptionsFlowHandler
    SettingsFlowManager = None
    SettingsOptionsFlowHandler = None

    EvLog           = None
    EvLogSensor     = None
    HALogger        = None
    iC3_LogFile     = None
    Sensors         = None
    iC3EntityPlatform = None    # iCloud3 Entity Platform (homeassistant.helpers.entity_component)
    PyiCloud        = None      # iCloud Account service
    PyiCloudInit    = None      # iCloud Account service when started from __init__ via executive job
    PyiCloudConfigFlow = None   # iCloud Account service when started from config_flow
    Waze            = None
    WazeHist        = None
    WazeHistTrackSensor = None    # Sensor for updating the lat/long values for the WazeHist Map display

    operating_mode          = 0         # Platform (Legacy using configuration.yaml) or Integration
    ha_config_platform_stmt = False     # a platform: icloud3 stmt is in the configurationyaml file that needs to be removed
    v2v3_config_migrated    = False     # Th v2 configuration parameters were migrated to v3
    add_entities = None

    # iCloud3 Directory & File Names
    ha_config_directory       = ''
    ha_storage_directory      = ''      # 'config/.storage' directory
    ha_storage_icloud3        = ''      # 'config/.storage/icloud3'
    icloud3_config_filename   = ''      # 'config/.storage/icloud3.configuration' - iC3 Configuration File
    icloud3_restore_state_filename = '' # 'config/.storage/icloud3.restore_state'
    config_ic3_yaml_filename  = ''      # 'config/config_ic3.yaml' (v2 config file name)
    icloud3_directory         = ''
    ha_config_www_directory   = ''
    www_evlog_js_directory    = ''
    www_evlog_js_filename     = ''
    wazehist_database_filename= ''      # Waze Location History sql database (.storage/icloud3.waze_route_history.db)

    # Platform and iCloud account parameters
    username                     = ''
    username_base                = ''
    password                     = ''
    encode_password_flag         = True
    all_famshr_devices           = True
    entity_registry_file         = ''
    evlog_card_directory         = ''
    evlog_card_program           = ''
    devices                      = ''

    # Global Object Dictionaries
    Devices                           = []  # Devices objects list
    Devices_by_devicename             = {}  # All Devices by devicename
    Devices_by_devicename_monitored   = {}  # All monitored Devices by devicename
    Devices_by_devicename_tracked     = {}  # All monitored Devices by devicename
    Devices_by_icloud_device_id       = {}  # FmF/FamShr Device Configuration
    Devices_by_iosapp_devicename      = {}  # All Devices by the iosapp device_tracker.iosapp_devicename
    # Devices_by_statzonename           = {}  # All Devices by the statzone.zone and statzone.display_as
    Zones                             = []  # Zones object list
    Zones_by_zone                     = {}  # Zone object by zone name
    zone_display_as                   = {}   # Zone display_as by zone distionary to ease displaying zone fname
    TrackedZones_by_zone              = {HOME, None}  # Tracked zones object by zone name set up with Devices.DeviceFmZones object
    StatZones                         = []  # Stationary Zone objects
    StatZones_by_zone                 = {}  # Stationary Zone objects by their id number (1-10 --> ic3_#_stationary)
    HomeZone                          = None # Home Zone object

    # HA device_tracker and sensor entity info
    DeviceTrackers_by_devicename      = {}  # HA device_tracker.[devicename] entity objects
    Sensors_by_devicename             = {}  # HA sensor.[devicename]_[sensor_name]_[from_zone] objects
    Sensors_by_devicename_from_zone   = {}  # HA sensor.[devicename]_[sensor_name]_[from_zone] objects
    Sensor_EventLog                   = None    # Event Log sensor object
    dr_device_id_by_devicename        = {}  # HA device_registry device_id
    dr_area_id_by_devicename          = {}  # HA device_registry area_id


    # System Wide variables control iCloud3 start/restart procedures
    polling_5_sec_loop_running      = False     # Indicates the 5-sec polling loop is set up
    start_icloud3_inprocess_flag    = False
    restart_icloud3_request_flag    = False     # iC3 needs to be restarted, set when a new_2fa code is needed in pyicloud_ic3_interface
    evlog_disable_refresh_flag      = False
    any_device_was_updated_reason   = ''
    evlog_action_request            = ''
    startup_alerts                  = []

    stage_4_no_devices_found_cnt    = 0         # Retry count to connect to iCloud and retrieve FamShr devices
    reinitialize_icloud_devices_flag= False         # Set when no devices are tracked and iC3 needs to automatically restart
    reinitialize_icloud_devices_cnt = 0
    initial_icloud3_loading_flag    = False


    # Debug and trace flags
    log_debug_flag               = False
    log_rawdata_flag             = False
    log_rawdata_flag_unfiltered  = False
    log_debug_flag_restart       = None
    log_rawdata_flag_restart     = None
    evlog_trk_monitors_flag      = False
    ic3_log_file_update_flag     = False
    ic3_log_file_create_secs     = 0
    ic3_log_file_last_write_secs = 0
    info_notification            = ''
    ha_notification              = {}
    trace_prefix                 = ''
    trace_text_change_1          = ''
    trace_text_change_2          = ''
    debug_flag                   = False
    debug_integer                = 0

    # Startup variables
    startup_log_msgs          = ''
    startup_log_msgs_prefix   = ''
    iosapp_entities           = ''
    iosapp_notify_devicenames = ''


    # Configuration parameters that can be changed in config_ic3.yaml
    um                     = DEFAULT_GENERAL_CONF[CONF_UNIT_OF_MEASUREMENT]
    time_format_12_hour    = True
    um_km_mi_factor        = .62137
    um_m_ft                = 'ft'
    um_kph_mph             = 'mph'
    um_time_strfmt         = '%I:%M:%S'
    um_time_strfmt_ampm    = '%I:%M:%S%P'
    um_date_time_strfmt    = '%Y-%m-%d %H:%M:%S'

    # Time conversion variables used in global_utilities
    time_zone_offset_seconds    = 0
    timestamp_local_offset_secs = 0

    # Configuration parameters
    config_parm                     = {}        # Config parms from HA config.yaml and config_ic3.yaml
    config_parm_initial_load        = {}        # Config parms from HA config.yaml used to reset eveerything on restart
    ha_config_yaml_icloud3_platform = {}        # Config parms from HA config.yaml used during initial conversion to config_flow

    conf_file_data    = {}
    conf_profile      = {}
    conf_data         = {}
    conf_tracking     = {}
    conf_devices      = []
    conf_general      = {}
    conf_sensors      = {}
    conf_devicenames  = []
    conf_famshr_devicenames = []
    conf_famshr_device_cnt  = 0                   # Number of devices with FamShr tracking set up
    conf_fmf_device_cnt     = 0                   # Number of devices with FmF tracking set up
    conf_iosapp_device_cnt  = 0                   # Number of devices with iOS App  tracking set up

    sensors_cnt                 = 0               # Number of sensors that will be creted (__init__.py)
    sensors_created_cnt         = 0               # Number of sensors that have been set up (incremented in sensor.py)
    device_trackers_cnt         = 0               # Number of device_trackers that will be creted (__init__.py)
    device_trackers_created_cnt = 0               # Number of device_trackers that have been set up (incremented in device_tracker.py)

    # restore_state file
    restore_state_file_data = {}
    restore_state_profile   = {}
    restore_state_devices   = {}

    # This stores the type of configuration parameter change done in the config_flow module
    # It indicates the type of change and if a restart is required to load device or sensor changes.
    # Items in the set are 'tracking', 'devices', 'profile', 'sensors', 'general', 'restart'
    config_flow_updated_parms = {''}

    distance_method_waze_flag       = True
    max_interval_secs               = DEFAULT_GENERAL_CONF[CONF_MAX_INTERVAL] * 60
    offline_interval_secs           = DEFAULT_GENERAL_CONF[CONF_OFFLINE_INTERVAL] * 60
    exit_zone_interval_secs         = DEFAULT_GENERAL_CONF[CONF_EXIT_ZONE_INTERVAL] * 60
    iosapp_alive_interval_secs      = DEFAULT_GENERAL_CONF[CONF_IOSAPP_ALIVE_INTERVAL] * 3600
    old_location_threshold          = DEFAULT_GENERAL_CONF[CONF_OLD_LOCATION_THRESHOLD] * 60
    old_location_adjustment         = DEFAULT_GENERAL_CONF[CONF_OLD_LOCATION_ADJUSTMENT] * 60
    passthru_zone_interval_secs     = DEFAULT_GENERAL_CONF[CONF_PASSTHRU_ZONE_TIME] * 60
    is_passthru_zone_used           = (14400 > passthru_zone_interval_secs > 0)  # time > 0 and < 4 hrs
    track_from_base_zone            = DEFAULT_GENERAL_CONF[CONF_TRACK_FROM_BASE_ZONE]
    track_from_home_zone            = DEFAULT_GENERAL_CONF[CONF_TRACK_FROM_HOME_ZONE]
    gps_accuracy_threshold          = DEFAULT_GENERAL_CONF[CONF_GPS_ACCURACY_THRESHOLD]
    travel_time_factor              = DEFAULT_GENERAL_CONF[CONF_TRAVEL_TIME_FACTOR]
    log_level                       = DEFAULT_GENERAL_CONF[CONF_LOG_LEVEL]

    display_gps_lat_long_flag       = DEFAULT_GENERAL_CONF[CONF_DISPLAY_GPS_LAT_LONG]
    center_in_zone_flag             = DEFAULT_GENERAL_CONF[CONF_CENTER_IN_ZONE]
    display_zone_format             = DEFAULT_GENERAL_CONF[CONF_DISPLAY_ZONE_FORMAT]
    display_gps_lat_long_flag       = DEFAULT_GENERAL_CONF[CONF_DISPLAY_GPS_LAT_LONG]
    # device_tracker_state_format     = DEFAULT_GENERAL_CONF[CONF_DEVICE_TRACKER_STATE_FORMAT]
    # if device_tracker_state_format == 'display_as': device_tracker_state_format = display_zone_format

    # device_tracker_state_evlog_format_flag = (device_tracker_state_format == FNAME)
    discard_poor_gps_inzone_flag    = DEFAULT_GENERAL_CONF[CONF_DISCARD_POOR_GPS_INZONE]
    distance_between_device_flag    = DEFAULT_GENERAL_CONF[CONF_DISTANCE_BETWEEN_DEVICES]

    tfz_tracking_max_distance       = DEFAULT_GENERAL_CONF[CONF_TFZ_TRACKING_MAX_DISTANCE]

    waze_region                     = DEFAULT_GENERAL_CONF[CONF_WAZE_REGION]
    waze_max_distance               = DEFAULT_GENERAL_CONF[CONF_WAZE_MAX_DISTANCE]
    waze_min_distance               = DEFAULT_GENERAL_CONF[CONF_WAZE_MIN_DISTANCE]
    waze_realtime                   = DEFAULT_GENERAL_CONF[CONF_WAZE_REALTIME]
    waze_history_database_used      = DEFAULT_GENERAL_CONF[CONF_WAZE_HISTORY_DATABASE_USED]
    waze_history_max_distance       = DEFAULT_GENERAL_CONF[CONF_WAZE_HISTORY_MAX_DISTANCE]
    waze_history_track_direction    = DEFAULT_GENERAL_CONF[CONF_WAZE_HISTORY_TRACK_DIRECTION]

    statzone_fname                  = DEFAULT_GENERAL_CONF[CONF_STAT_ZONE_FNAME]
    statzone_base_latitude          = DEFAULT_GENERAL_CONF[CONF_STAT_ZONE_BASE_LATITUDE]
    statzone_base_longitude         = DEFAULT_GENERAL_CONF[CONF_STAT_ZONE_BASE_LONGITUDE]
    statzone_inzone_interval_secs   = DEFAULT_GENERAL_CONF[CONF_STAT_ZONE_INZONE_INTERVAL] * 60
    statzone_still_time_secs        = DEFAULT_GENERAL_CONF[CONF_STAT_ZONE_STILL_TIME] * 60
    is_statzone_used                = (14400 > statzone_still_time_secs > 0)   # time > 0 and < 4 hrs

    # Initialize Stat Zone size based on Home zone size
    statzone_min_dist_from_zone_km = .2
    statzone_dist_move_limit_km    = .125
    statzone_radius_m              = 100

    # Variables used to config the device variables when setting up
    # intervals and determining the tracking method
    inzone_interval_secs = {}

    # Data source control variables
    # Used to reset Gb.is_data_source after pyicloud/icloud account successful reset

    # Specifed in configuration file (set in config_flow icloud credentials screen)
    conf_data_source_FAMSHR   = True
    conf_data_source_FMF      = False
    conf_data_source_IOSAPP   = True
    conf_data_source_ICLOUD   = conf_data_source_FAMSHR or conf_data_source_FMF

    # A trackable device uses this data source (set in start_ic3.set trackable_devices)
    used_data_source_FAMSHR  = False
    used_data_source_FMF     = False
    used_data_source_IOSAPP  = False

    # Primary data source being used that can be turned off if errors
    primary_data_source_ICLOUD = conf_data_source_ICLOUD
    primary_data_source        = ICLOUD if primary_data_source_ICLOUD else IOSAPP

    # iCloud account authorization variables
    icloud_acct_error_cnt         = 0
    authenticated_time            = 0
    authentication_error_cnt      = 0
    authentication_error_retry_secs = HIGH_INTEGER
    pyicloud_refresh_time         = {}     # Last time Pyicloud was refreshed for the trk method
    pyicloud_refresh_time[FMF]    = 0
    pyicloud_refresh_time[FAMSHR] = 0

    # Pyicloud counts, times and common variables
    force_icloud_update_flag     = False
    pyicloud_auth_started_secs   = 0
    pyicloud_authentication_cnt  = 0
    pyicloud_location_update_cnt = 0
    pyicloud_calls_time          = 0.0
    trusted_device               = None
    verification_code            = None
    icloud_cookies_dir           = ''
    icloud_cookies_file          = ''
    fmf_device_verified_cnt      = 0
    famshr_device_verified_cnt   = 0
    iosapp_device_verified_cnt   = 0
    authentication_alert_displayed_flag = False

    unverified_Devices           = []               # Devices that have not been verified in start_ic3.check_unverified_devices
    unverified_devices_cnt       = 0                #
    unverified_devices_retry_cnt = 0                # Decreased in icloud_data_handler. Retry verify until cnt=0

    # Waze History for DeviceFmZone
    wazehist_zone_id            = {}
    waze_status                 = WAZE_USED
    waze_manual_pause_flag      = False             # Paused using service call
    waze_close_to_zone_pause_flag = False           # Close to home pauses Waze
    wazehist_recalculate_time_dist_flag = False     # Set in config_flow > Actions to schedule a db rebuild at midnight

    # Variables to be moved to Device object when available
    # iosapp entity data
    last_iosapp_state                = {}
    last_iosapp_state_changed_time   = {}
    last_iosapp_state_changed_secs   = {}
    last_iosapp_trigger              = {}
    last_iosapp_trigger_changed_time = {}
    last_iosapp_trigger_changed_secs = {}
    iosapp_monitor_error_cnt         = {}

    # Device state, zone data from icloud and iosapp
    state_to_zone     = {}
    this_update_secs  = 0
    this_update_time  = ''
    state_this_poll   = {}
    state_last_poll   = {}
    zone_last         = {}
    zone_current      = {}
    zone_timestamp    = {}
    state_change_flag = {}

    # Device status and tracking fields
    devicename                     = ''             # Current devicename being updated
    config_track_devices_change_flag = True         # Set in config_handler when parms are loaded. Do Stave 1 only if no device changes
    device_tracker_entity_ic3      = {}
    trigger                        = {}
    got_exit_trigger_flag          = {}
    device_being_updated_flag      = {}
    device_being_updated_retry_cnt = {}
    iosapp_update_flag             = {}
    attr_tracking_msg              = '' # tracking msg on attributes
    all_tracking_paused_flag       = False
    dist_to_other_devices_update_sensor_list = set()    # Contains a list of devicenames that need their distance sensors updated
                                                        # at the end of polling loop after all devices have been processed

    # Miscellenous variables
    broadcast_msg                  = ''
    broadcast_info_msg             = None

    #<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

    config_flow_flag = False
