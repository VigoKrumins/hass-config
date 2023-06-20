#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   Define the iCloud3 General Constants
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

VERSION                         = '3.0.0b18c'

DOMAIN                          = 'icloud3'
ICLOUD3                         = 'iCloud3'
MODE_PLATFORM                   = -1
MODE_INTEGRATION                = 1
DEBUG_TRACE_CONTROL_FLAG        = False
STORAGE_KEY                     = DOMAIN
STORAGE_VERSION                 = 1

HA_ENTITY_REGISTRY_FILE_NAME    = 'config/.storage/core.entity_registry'
ENTITY_REGISTRY_FILE_KEY        = 'core.entity_registry'
DEFAULT_CONFIG_IC3_FILE_NAME    = 'config/config_ic3.yaml'

STORAGE_DIR                     = ".storage"
STORAGE_KEY_ENTITY_REGISTRY     = 'core.entity_registry'
SENSOR_EVENT_LOG_NAME           = 'icloud3_event_log'
EVLOG_CARD_WWW_DIRECTORY        = 'www/icloud3'
EVLOG_CARD_WWW_JS_PROG          = 'icloud3-event-log-card.js'
WAZE_LOCATION_HISTORY_DATABASE  = 'icloud3.waze_location_history.db'
SENSOR_WAZEHIST_TRACK_NAME      = 'icloud3_wazehist_track'
IC3LOGGER_FILENAME              = 'icloud3-0.log'
IC3_LOG_FILENAME                = 'icloud3-0.log'

DEVICE_TRACKER                  = 'device_tracker'
DEVICE_TRACKER_DOT              = 'device_tracker.'
PLATFORMS                       = ['sensor', 'device_tracker']
PLATFORM                        = 'device_tracker'
SENSOR                          = 'sensor'
ATTRIBUTES                      = 'attributes'
ENTITY_ID                       = 'entity_id'
HA_DEVICE_TRACKER_LEGACY_MODE   = False
MOBILE_APP                      = 'mobile_app_'
NOTIFY                          = 'notify'
DISTANCE_TO_DEVICES             = 'distance_to'
DISTANCE_TO_OTHER_DEVICES       = 'distance_to_other_devices'
DISTANCE_TO_OTHER_DEVICES_DATETIME = 'distance_to_other_devices_datetime'

# General constants
HOME                            = 'home'
HOME_FNAME                      = 'Home'
NOT_HOME                        = 'not_home'
NOT_HOME_FNAME                  = 'NotHome'
NEAR_HOME                       = 'NearHome'
NOT_SET                         = 'not_set'
NOT_SET_FNAME                   = 'NotSet'
UNKNOWN                         = 'Unknown'
STATIONARY                      = 'statzone'
STATIONARY_FNAME                = 'StatZone'
AWAY_FROM                       = 'AwayFrom'
AWAY_FROM_HOME                  = 'AwayFromHome'
AWAY                            = 'Away'
NEAR                            = 'Near'
TOWARDS                         = 'Towards'
TOWARDS_HOME                    = 'TowardsHome'
INZONE                          = 'inZone'
INZONE_HOME                     = 'inHomeZone'
INZONE_STATIONARY               = 'inStatZone'
PAUSED                          = 'PAUSED'
PAUSED_CAPS                     = 'PAUSED'
RESUMING                        = 'RESUMING'
RESUMING_CAPS                   = 'RESUMING'
NEVER                           = 'Never'
ERROR                           = 0
NONE                            = 'none'
NONE_FNAME                      = 'None'
SEARCH                          = 'search'
SEARCH_FNAME                    = 'Search'
VALID_DATA                      = 1
UTC_TIME                        = True
LOCAL_TIME                      = False
NUMERIC                         = True
NEW_LINE                        = '\n'
WAZE                            = 'waze'
CALC                            = 'calc'
DIST                            = 'dist'

IPHONE_FNAME                    = 'iPhone'
IPHONE                          = 'iphone'
IPAD_FNAME                      = 'iPad'
IPAD                            = 'ipad'
IPOD_FNAME                      = 'iPod'
IPOD                            = 'ipod'
WATCH_FNAME                     = 'Watch'
WATCH                           = 'watch'
AIRPODS_FNAME                   = 'AirPods'
AIRPODS                         = 'airpods'
ICLOUD_FNAME                    = 'iCloud'
ICLOUD                          = 'icloud'
OTHER_FNAME                     = 'Other'
OTHER                           = 'other'

# Apple is using a country specific iCloud server based on the country code in pyicloud_ic3.
# Add to the HOME_ENDPOINT & SETUP_ENDPOINT urls if the HA country code is one of these values.
APPLE_SPECIAL_ICLOUD_SERVER_COUNTRY_CODE = ['cn']

DEVICE_TYPES = [
        IPHONE, IPAD, IPOD, WATCH, ICLOUD_FNAME, AIRPODS,
        IPHONE_FNAME, IPAD_FNAME, IPOD_FNAME, WATCH_FNAME, ICLOUD_FNAME, AIRPODS_FNAME,
]
DEVICE_TYPE_FNAME = {
        IPHONE: IPHONE_FNAME,
        IPAD: IPAD_FNAME,
        WATCH: WATCH_FNAME,
        AIRPODS: AIRPODS_FNAME,
        IPOD: IPOD_FNAME,
        OTHER: OTHER_FNAME,
}
DEVICE_TYPE_ICONS = {
        IPHONE: "mdi:cellphone",
        IPAD: "mdi:tablet",
        IPOD: "mdi:ipod",
        AIRPODS: "mdi:earbuds-outline",
        WATCH: "mdi:watch-variant",
        OTHER: 'mdi:laptop'
}

UM_FNAME        = {'mi': 'Miles', 'km': 'Kilometers'}
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATETIME_ZERO   = '0000-00-00 00:00:00'
HHMMSS_ZERO     = '00:00:00'
HIGH_INTEGER    = 9999999999

# Device Tracking Status
TRACKING_NORMAL  = 0
TRACKING_PAUSED  = 1
TRACKING_RESUMED = 2

# Config Parameter Range Index (used in RANGE_DEVICE_CONF, RANGE_GENERAL_CONF lists)
MIN      = 0
MAX      = 1
STEP     = 2
RANGE_UM = 3

#Other constants
IOSAPP_DT_ENTITY = True
ICLOUD_DT_ENTITY = False
ICLOUD_LOCATION_DATA_ERROR = False
CMD_RESET_PYICLOUD_SESSION = 'reset_session'
NEAR_DEVICE_DISTANCE       = 20
PASS_THRU_ZONE_INTERVAL_SECS = 60       # Delay time before moving into a non-tracked zone to see if if just passing thru
STATZONE_BASE_RADIUS_M     = 100

EVLOG_TABLE_MAX_CNT_BASE = 1500         # Used to calculate the max recds to store
EVLOG_TABLE_MAX_CNT_ZONE = 2000         # Used to calculate the max recds to store
EVENT_LOG_CLEAR_SECS     = 900          # Clear event log data interval
EVENT_LOG_CLEAR_CNT      = 50           # Number of recds to display when clearing event log
ICLOUD3_ERROR_MSG        = "ICLOUD3 ERROR-SEE EVENT LOG"

#Devicename config parameter file extraction
DI_DEVICENAME           = 0
DI_DEVICE_TYPE          = 1
DI_NAME                 = 2
DI_EMAIL                = 3
DI_BADGE_PICTURE        = 4
DI_IOSAPP_ENTITY        = 5
DI_IOSAPP_SUFFIX        = 6
DI_ZONES                = 7

# Waze status codes
# WAZE_REGIONS      = ['US', 'NA', 'EU', 'IL', 'AU']
WAZE_SERVERS_BY_COUNTRY_CODE = {'us': 'us', 'ca': 'us', 'il': 'il', 'row': 'row'}
WAZE_SERVERS_FNAME =           {'us': 'United States, Canada',
                                'US': 'United States, Canada',
                                'il': 'Israel',
                                'IL': 'Israel',
                                'row': 'Rest of the World',
                                'ROW': 'Rest of the World'}
WAZE_USED         = 0
WAZE_NOT_USED     = 1
WAZE_PAUSED       = 2
WAZE_OUT_OF_RANGE = 3
WAZE_NO_DATA      = 4

# Interval range table used for setting the interval based on a retry count
# The key is starting retry count range, the value is the interval (in minutes)
# poor_location_gps cnt, icloud_authentication cnt (default)
OLD_LOC_POOR_GPS_CNT   = 1.1
AUTH_ERROR_CNT         = 1.2
RETRY_INTERVAL_RANGE_1 = {0:.25, 4:1, 8:5, 12:30, 16:60, 20:120, 22:240, 24:240}
IOSAPP_REQUEST_LOC_CNT = 2.1
RETRY_INTERVAL_RANGE_2 = {0:.5, 4:2, 8:30, 12:60, 14:120, 16:180, 18:240, 20:240}

# Used by the 'update_method' in the polling_5_sec loop
IOSAPP_UPDATE     = "IOSAPP"
ICLOUD_UPDATE     = "ICLOUD"

# The event_log lovelace card will display the event in a special color if
# the text starts with a special character:
# ^1^ - LightSeaGreen
# ^2^ - BlueViolet
# ^3^ - OrangeRed
# ^4^ - DeepPink
# ^5^ - MediumVioletRed
# ^6^ - --dark-primary-color
EVLOG_TIME_RECD   = '^t^'       # iosState, ic3Zone, interval, travel time, distance event
EVLOG_UPDATE_HDR  = '^u^'       # update start-to-complete highlight and edge bar block
EVLOG_UPDATE_START= '^s^'       # update start-to-complete highlight and edge bar block
EVLOG_UPDATE_END  = '^c^'       # update start-to-complete highlight and edge bar block
EVLOG_ERROR       = '^e^'
EVLOG_ALERT       = '^a^'
EVLOG_WARNING     = '^w^'
EVLOG_INIT_HDR    = '^i^'       # iC3 initialization start/complete event
EVLOG_HIGHLIGHT   = '^h^'       # Display item in green highlight bar
EVLOG_IC3_STARTING  = '^i^'
EVLOG_IC3_STAGE_HDR = '^g^'


EVLOG_NOTICE      = '^5^'
EVLOG_TRACE       = '^6^'
EVLOG_DEBUG       = '^6^'
EVLOG_MONITOR     = '^6^'
# SETTINGS_INTEGRATIONS_MSG, INTEGRATIONS_IC3_CONFIG_MSG,
SETTINGS_INTEGRATIONS_MSG   = '`Settings > Devices & Services > Integrations`'
INTEGRATIONS_IC3_CONFIG_MSG = '`iCloud3 > Configuration`'

CIRCLE_LETTERS_DARK =  {'a':'🅐', 'b':'🅑', 'c':'🅒', 'd':'🅓', 'e':'🅔', 'f':'🅕', 'g':'🅖',
                        'h':'🅗', 'i':'🅘', 'j':'🅙', 'k':'🅚', 'l':'🅛', 'm':'🅜', 'n':'🅝',
                        'q':'🅞', 'p':'🅟', 'q':'🅠', 'r':'🅡', 's':'🅢', 't':'🅣', 'u':'🅤',
                        'v':'🅥', 'w':'🅦', 'x':'🅧', 'y':'🅨', 'z':'🅩', 'other': '✪'}
CIRCLE_LETTERS_LITE =  {'a':'Ⓐ', 'b':'Ⓑ', 'c':'Ⓒ', 'd':'Ⓓ', 'e':'Ⓔ', 'f':'Ⓕ', 'g':'Ⓖ',
                        'h':'Ⓗ', 'i':'Ⓘ', 'j':'Ⓙ', 'k':'Ⓚ', 'l':'Ⓛ', 'm':'Ⓜ', 'n':'Ⓝ',
                        'q':'Ⓞ', 'p':'Ⓟ', 'q':'Ⓠ', 'r':'Ⓡ', 's':'Ⓢ', 't':'Ⓣ', 'u':'Ⓤ',
                        'v':'Ⓥ', 'w':'Ⓦ', 'x':'Ⓧ', 'y':'Ⓨ', 'z':'Ⓩ', 'other': '✪'}
'''
lite_circled_letters = "Ⓐ Ⓑ Ⓒ Ⓓ Ⓔ Ⓕ Ⓖ Ⓗ Ⓘ Ⓙ Ⓚ Ⓛ Ⓜ Ⓝ Ⓞ Ⓟ Ⓠ Ⓡ Ⓢ Ⓣ Ⓤ Ⓥ Ⓦ Ⓧ Ⓨ Ⓩ"
dark_circled_letters = "🅐 🅑 🅒 🅓 🅔 🅕 🅖 🅗 🅘 🅙 🅚 🅛 🅜 🅝 🅞 🅟 🅠 🅡 🅢 🅣 🅤 🅥 🅦 🅧 🅨 🅩 ✪"
Symbols = ±▪•●▬⮾ ⊗ ⊘✓×ø¦ ▶◀ ►◄▲▼ ∙▪ »« oPhone=►▶→⟾➤➟➜➔➤🡆🡪🡺⟹🡆➔ᐅ◈🝱☒☢⛒❌⊘Ɵ⊗ⓧⓍ⛒🜔
  — – ⁃ » ━▶ ━➤🡺 —> > > ❯↦ … 🡪ᗕ ᗒ ᐳ ─🡢 ──ᗒ 🡢 ─ᐅ ↣ ➙ →《》◆◈◉●▐‖  ▹▻▷◁◅◃▶➤➜➔❰❰❱❱ ⠤
 ⣇⠈⠉⠋⠛⠟⠿⡿⣿       https://www.fileformat.info/info/unicode/block/braille_patterns/utf8test.htm
'''
NBSP              = '⠈' #'&nbsp;'
NBSP2             = '⠉' #'&nbsp;&nbsp;'
NBSP3             = '⠋' #'&nbsp;&nbsp;&nbsp;'
NBSP4             = '⠛' #'&nbsp;&nbsp;&nbsp;&nbsp;'
NBSP5             = '⠟' #'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
NBSP6             = '⠿' #'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
CRLF              = '⣇' #'<br>'
CHECK_MARK        = '✓ '
CIRCLE_STAR       = '✪ '
CIRCLE_STAR2      = '✪'
CIRCLE_BIG_X      = '⊗'
CIRCLE_SLASH      = '⊘'
CIRCLE_X          = 'ⓧ'
DOT               = '• '
DOT2              = '•'
HDOT              = '◦ '
HDOT2             = '◦'
LT                = '&lt;'
GT                = '&gt;'
LTE               = '≤'
GTE               = '≥'
CRLF_DOT          = f'{CRLF}{NBSP3}•{NBSP2}'
CRLF_X            = f'{CRLF}{NBSP3}×{NBSP2}'
CRLF_HDOT         = f'{CRLF}{NBSP6}◦{NBSP2}'
CRLF_CHK          = f'{CRLF}{NBSP3}✓{NBSP}'
CTRL_STAR         = f'{CRLF}{NBSP2}✪{NBSP}'
CRLF_STAR         = f'{CRLF}{NBSP2}✪{NBSP}'
CRLF_CIRCLE_X     = f'{CRLF}{NBSP2}ⓧ{NBSP}'
CRLF_SP3_DOT      = f'{CRLF}{NBSP3}•{NBSP}'
CRLF_SP5_DOT      = f'{CRLF}{NBSP5}•{NBSP}'
CRLF_SP3_HDOT     = f'{CRLF}{NBSP3}◦{NBSP}'
CRLF_SP3_STAR     = f'{CRLF}{NBSP3}✪{NBSP}'

NEARBY_DEVICE_USEABLE_SYM = '✓'
BLANK_SENSOR_FIELD = '———'
RARROW            = ' → '       #U+27F6 (Long Arrow Right)  ⟹ ⟾
RARROW2           = '→'         #U+27F6 (Long Arrow Right)  ⟹ ⟾
LARROW            = ' <-- '     #U+27F5 (Long Arrow Left) ⟸ ⟽
LARROW2           = '<--'       #U+27F5 (Long Arrow Left) ⟸ ⟽
INFO_SEPARATOR    = '/' #'∻'

#tracking_method config parameter being used
ICLOUD            = 'icloud'    #iCloud Location Services (FmF & FamShr)
ICLOUD_FNAME      = 'iCloud'
FMF               = 'fmf'       #Find My Friends
FAMSHR            = 'famshr'    #Family Sharing
IOSAPP            = 'iosapp'    #HA IOS App v1.5x or v2.x
IOSAPP_FNAME      = 'iOSApp'
NO_IOSAPP         = 'no_iosapp'
FMF_FNAME         = 'FmF'
FAMSHR_FNAME      = 'FamShr'
FAMSHR_FMF        = 'famshr_fmf'
FAMSHR_FMF_FNAME  = 'FamShr-FmF'
DATA_SOURCE_FNAME = {FMF: FMF_FNAME, FAMSHR: FAMSHR_FNAME, FAMSHR_FMF: FAMSHR_FMF_FNAME,
                        IOSAPP: IOSAPP_FNAME, ICLOUD: ICLOUD_FNAME}

# Device tracking modes
TRACK_DEVICE      = 'track'
MONITOR_DEVICE    = 'monitor'
INACTIVE_DEVICE   = 'inactive'

#Zone field names
NAME              = 'name'
FNAME             = 'fname'
FNAME_HOME        = 'fname/Home'
TITLE             = 'title'
RADIUS            = 'radius'
NON_ZONE_ITEM_LIST = {
        'not_home': 'Away',
        'Not_Home': 'Away',
        'not_set': 'NotSet',
        'Not_Set': 'NotSet',
        # 'stationary': 'Stationary',
        # 'Stationary': 'Stationary',
        STATIONARY: STATIONARY_FNAME,
        STATIONARY_FNAME: STATIONARY_FNAME,
        'unknown': 'Unknown'}

#config_ic3.yaml parameter validation items
#LIST = 1
#TIME = 2
#NUMBER = 3
#TRUE_FALSE = 4
#VALID_TIME_TYPES = ['sec', 'secs', 'min', 'mins', 'hr', 'hrs']

#-----►►Test configuration parameters ----------
# VALID_CONF_DEVICES_ITEMS = [
#         CONF_DEVICENAME, CONF_EMAIL, CONF_PICTURE, CONF_NAME,
#         CONF_INZONE_INTERVAL, CONF_TRACK_FROM_ZONES, CONF_IOSAPP_SUFFIX,
#         CONF_IOSAPP_ENTITY, CONF_IOSAPP_INSTALLED, CONF_NO_IOSAPP,
#         CONF_NO_IOSAPP, CONF_TRACKING_METHOD, ]

DASH_20  = '━'*20
OPT_NONE = 0


TRK_METHOD_SHORT_NAME = {
        FMF: FMF_FNAME,
        FAMSHR: FAMSHR_FNAME,
        IOSAPP: IOSAPP_FNAME, }

#iOS App Triggers defined in /iOS/Shared/Location/LocatioTrigger.swift
BACKGROUND_FETCH          = 'Background Fetch'
BKGND_FETCH               = 'Bkgnd Fetch'
GEOGRAPHIC_REGION_ENTERED = 'Geographic Region Entered'
GEOGRAPHIC_REGION_EXITED  = 'Geographic Region Exited'
IBEACON_REGION_ENTERED    = 'iBeacon Region Entered'
IBEACON_REGION_EXITED     = 'iBeacon Region Exited'
REGION_ENTERED            = 'Region Entered'
REGION_EXITED             = 'Region Exited'
ENTER_ZONE                = 'Enter Zone'
EXIT_ZONE                 = 'Exit Zone'
INITIAL                   = 'Initial'
MANUAL                    = 'Manual'
LAUNCH                    = "Launch",
SIGNIFICANT_LOC_CHANGE    = 'Significant Location Change'
SIGNIFICANT_LOC_UPDATE    = 'Significant Location Update'
SIG_LOC_CHANGE            = 'Sig Loc Change'
PUSH_NOTIFICATION         = 'Push Notification'
REQUEST_IOSAPP_LOC        = 'Request iOSApp Loc'
IOSAPP_LOC_CHANGE         = 'iOSApp Loc Change'
SIGNALED                  = 'Signaled'

#Trigger is converted to abbreviation after getting last_update_trigger
IOS_TRIGGER_ABBREVIATIONS = {
        GEOGRAPHIC_REGION_ENTERED: ENTER_ZONE,
        GEOGRAPHIC_REGION_EXITED: EXIT_ZONE,
        IBEACON_REGION_ENTERED: ENTER_ZONE,
        IBEACON_REGION_EXITED: EXIT_ZONE,
        SIGNIFICANT_LOC_CHANGE: SIG_LOC_CHANGE,
        SIGNIFICANT_LOC_UPDATE: SIG_LOC_CHANGE,
        PUSH_NOTIFICATION: REQUEST_IOSAPP_LOC,
        BACKGROUND_FETCH: BKGND_FETCH,
        }
IOS_TRIGGERS_VERIFY_LOCATION = [
        INITIAL,
        LAUNCH,
        SIGNALED,
        MANUAL,
        IOSAPP_LOC_CHANGE,
        BKGND_FETCH,
        SIG_LOC_CHANGE,
        REQUEST_IOSAPP_LOC,
        ]
IOS_TRIGGERS_ENTER      = [ENTER_ZONE, ]
IOS_TRIGGERS_EXIT       = [EXIT_ZONE, ]
IOS_TRIGGERS_ENTER_EXIT = [ENTER_ZONE, EXIT_ZONE, ]

#Convert state non-fname value to internal zone/state value
STATE_TO_ZONE_BASE = {
        'NotSet': 'not_set',
        'Away': 'not_home',
        "away": 'not_home',
        'NotHome': 'not_home',
        "nothome": 'not_home',
        # 'Stationary': 'stationary',
        # 'stationary': 'stationary',
        STATIONARY: STATIONARY_FNAME,
        STATIONARY_FNAME: STATIONARY_FNAME,
        }

#Lists to hold the group names, group objects and iCloud device configuration
#The ICLOUD3_GROUPS is filled in on each platform load, the GROUP_OBJS is
#filled in after the polling timer is setup.
ICLOUD3_GROUPS     = []
ICLOUD3_GROUP_OBJS = {}
ICLOUD3_TRACKED_DEVICES = {}


#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
#
#       OTHER WORKING VARIABLES
#
#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

# v2 to v3 migration items
CONF_ENTITY_REGISTRY_FILE  = 'entity_registry_file_name'
CONFIG_IC3                 = 'config_ic3'
CONF_CREATE_SENSORS        = 'create_sensors'
CONF_EXCLUDE_SENSORS       = 'exclude_sensors'
CONF_CONFIG_IC3_FILE_NAME  = 'config_ic3_file_name'

# entity attributes (iCloud FmF & FamShr)
ICLOUD_TIMESTAMP           = 'timeStamp'
ICLOUD_HORIZONTAL_ACCURACY = 'horizontalAccuracy'
ICLOUD_VERTICAL_ACCURACY   = 'verticalAccuracy'
ICLOUD_BATTERY_STATUS      = 'batteryStatus'
ICLOUD_BATTERY_LEVEL       = 'batteryLevel'
ICLOUD_DEVICE_CLASS        = 'deviceClass'
ICLOUD_DEVICE_STATUS       = 'deviceStatus'
ICLOUD_LOW_POWER_MODE      = 'lowPowerMode'
ICLOUD_LOST_MODE_CAPABLE   = 'lostModeCapable'
ID                         = 'id'
LAST_CHANGED_SECS          = 'last_changed_secs'
LAST_CHANGED_TIME          = 'last_changed_time'
STATE                      = 'state'

# device tracker attributes
LOCATION                   = 'location'
ATTRIBUTES                 = 'attributes'
RADIUS                     = 'radius'
NAME                       = 'name'
FRIENDLY_NAME              = 'friendly_name'
LATITUDE                   = 'latitude'
LONGITUDE                  = 'longitude'
DEVICE_CLASS               = 'device_class'
DEVICE_ID                  = 'device_id'
PASSIVE                    = 'passive'

# entity attributes
LOCATION_SOURCE            = 'location_source'
INTO_ZONE_DATETIME         = 'into_zone'
FROM_ZONE                  = 'from_zone'
TIMESTAMP                  = 'timestamp'
TIMESTAMP_SECS             = 'timestamp_secs'
TIMESTAMP_TIME             = 'timestamp_time'
LOCATION_TIME              = 'location_time'
TRACKING_METHOD            = 'data_source'
DATA_SOURCE                = 'data_source'
DATETIME                   = 'date_time'
AGE                        = 'age'
BATTERY_SOURCE             = 'battery_data_source'
BATTERY_LEVEL              = 'battery_level'
BATTERY_UPDATE_TIME        = 'battery_level_updated'
WAZE_METHOD                = 'waze_method'
MAX_DISTANCE               = 'max_distance'

DEVICE_STATUS              = 'device_status'
LOW_POWER_MODE             = 'low_power_mode'
TRACKING                   = 'tracking'
DEVICENAME_IOSAPP          = 'iosapp_device'
AUTHENTICATED              = 'authenticated'

LAST_UPDATE_TIME           = 'last_update_time'
LAST_UPDATE_DATETIME       = 'last_updated_date/time'
NEXT_UPDATE_TIME           = 'next_update_time'
NEXT_UPDATE_DATETIME       = 'next_update_date/time'
LAST_LOCATED_TIME          = 'last_located_time'
LAST_LOCATED_DATETIME      = 'last_located_date/time'

GPS                        = 'gps'
POLL_COUNT                 = 'poll_count'
ICLOUD3_VERSION            = 'icloud3_version'
VERT_ACCURACY              = 'vertical_accuracy'
EVENT_LOG                  = 'event_log'
PICTURE                    = 'entity_picture'
ICON                       = 'icon'
RAW_MODEL                  = 'raw_model'
MODEL                      = 'model'
MODEL_DISPLAY_NAME         = 'model_display_name'
RAW_MODEL2                 = 'raw_model2'
MODEL2                     = 'model2'
MODEL_DISPLAY_NAME2        = 'model_display_name2'


#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

ICLOUD3_EVENT_LOG    = 'icloud3_event_log'
DEVTRKR_ONLY_MONITOR = 'devtrkr_only_monitored_devices'

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#           CONFIG_FLOW CONSTANTS - CONFIGURATION PARAMETERS IN
#                                       .storage/icloud.configuration FILE
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# to store the cookie
STORAGE_KEY = DOMAIN
STORAGE_VERSION = 1

# Platform
CONF_VERSION                    = 'version'
CONF_IC3_VERSION                = 'ic3_version'
CONF_VERSION_INSTALL_DATE       = 'version_install_date'
CONF_UPDATE_DATE                = 'config_update_date'
CONF_EVLOG_CARD_DIRECTORY       = 'event_log_card_directory'
CONF_EVLOG_CARD_PROGRAM         = 'event_log_card_program'

# Account, Devices, Tracking Parameters
CONF_USERNAME                   = 'username'
CONF_PASSWORD                   = 'password'
CONF_DEVICES                    = 'devices'
CONF_DATA_SOURCE                = 'data_source'
CONF_VERIFICATION_CODE          = 'verification_code'
CONF_ICLOUD_SERVER_ENDPOINT_SUFFIX = 'icloud_server_endpoint_suffix'
CONF_ENCODE_PASSWORD            = 'encode_password'
CONF_SETUP_ICLOUD_SESSION_EARLY = 'setup_icloud_session_early'

#devices_schema parameters used for v2->v3 migration
CONF_DEVICENAME                 = 'device_name'
CONF_IOSAPP_SUFFIX              = 'iosapp_suffix'
CONF_IOSAPP_ENTITY              = 'iosapp_entity'
CONF_NOIOSAPP                   = 'noiosapp'
CONF_NO_IOSAPP                  = 'no_iosapp'
CONF_IOSAPP_INSTALLED           = 'iosapp_installed'
CONF_EMAIL                      = 'email'
CONF_CONFIG                     = 'config'
CONF_SOURCE                     = 'source'

# General Parameters
CONF_UNIT_OF_MEASUREMENT        = 'unit_of_measurement'
CONF_TIME_FORMAT                = 'time_format'
CONF_MAX_INTERVAL               = 'max_interval'
CONF_OFFLINE_INTERVAL           = 'offline_interval'
CONF_EXIT_ZONE_INTERVAL         = 'exit_zone_interval'
CONF_IOSAPP_ALIVE_INTERVAL      = 'iosapp_alive_interval'
CONF_GPS_ACCURACY_THRESHOLD     = 'gps_accuracy_threshold'
CONF_OLD_LOCATION_THRESHOLD     = 'old_location_threshold'
CONF_OLD_LOCATION_ADJUSTMENT    = 'old_location_adjustment'
CONF_TRAVEL_TIME_FACTOR         = 'travel_time_factor'
CONF_TFZ_TRACKING_MAX_DISTANCE  = 'tfz_tracking_max_distance'
CONF_PASSTHRU_ZONE_TIME         = 'passthru_zone_time'
CONF_LOG_LEVEL                  = 'log_level'
CONF_DISPLAY_GPS_LAT_LONG       = 'display_gps_lat_long'

# inZone Parameters
CONF_DISPLAY_ZONE_FORMAT        = 'display_zone_format'
CONF_CENTER_IN_ZONE             = 'center_in_zone'
CONF_DISCARD_POOR_GPS_INZONE    = 'discard_poor_gps_inzone'
CONF_DISTANCE_BETWEEN_DEVICES   = 'distance_between_devices'
CONF_INZONE_INTERVALS           = 'inzone_intervals'

# Waze Parameters
CONF_DISTANCE_METHOD            = 'distance_method'
CONF_WAZE_USED                  = 'waze_used'
CONF_WAZE_REGION                = 'waze_region'
CONF_WAZE_SERVER                = 'waze_region'
CONF_WAZE_MAX_DISTANCE          = 'waze_max_distance'
CONF_WAZE_MIN_DISTANCE          = 'waze_min_distance'
CONF_WAZE_REALTIME              = 'waze_realtime'
CONF_WAZE_HISTORY_DATABASE_USED = 'waze_history_database_used'
CONF_WAZE_HISTORY_MAX_DISTANCE  = 'waze_history_max_distance'
CONF_WAZE_HISTORY_TRACK_DIRECTION= 'waze_history_track_direction'

# Stationary Zone Parameters
CONF_STAT_ZONE_FNAME            = 'stat_zone_fname'
CONF_STAT_ZONE_STILL_TIME       = 'stat_zone_still_time'
CONF_STAT_ZONE_INZONE_INTERVAL  = 'stat_zone_inzone_interval'
CONF_STAT_ZONE_BASE_LATITUDE    = 'stat_zone_base_latitude'
CONF_STAT_ZONE_BASE_LONGITUDE   = 'stat_zone_base_longitude'
CONF_SENSORS                    = 'sensors'

# Display Text As Parameter
CONF_DISPLAY_TEXT_AS            = 'display_text_as'

# Devices Parameters
CONF_IC3_DEVICENAME             = 'ic3_devicename'
CONF_FNAME                      = 'fname'
CONF_FAMSHR_DEVICENAME          = 'famshr_devicename'
CONF_FAMSHR_DEVICE_ID           = 'famshr_device_id'
CONF_RAW_MODEL                  = 'raw_model'
CONF_MODEL                      = 'model'
CONF_MODEL_DISPLAY_NAME         = 'model_display_name'
CONF_FAMSHR_DEVICENAME2         = 'famshr_devicename2'
CONF_FAMSHR_DEVICE_ID2          = 'famshr_device_id2'
CONF_RAW_MODEL2                 = 'raw_model2'
CONF_MODEL2                     = 'model2'
CONF_MODEL_DISPLAY_NAME2        = 'model_display_name2'
CONF_FMF_EMAIL                  = 'fmf_email'
CONF_FMF_DEVICE_ID              = 'fmf_device_id'
CONF_IOSAPP_DEVICE              = 'iosapp_device'
CONF_IOSAPP_DEVICE2             = 'iosapp_device2'
CONF_PICTURE                    = 'picture'
CONF_TRACKING_MODE              = 'tracking_mode'
CONF_TRACK_FROM_BASE_ZONE       = 'track_from_base_zone'          # Primary Zone a device is tracking from, normally Home
CONF_TRACK_FROM_HOME_ZONE       = 'track_from_home_zone'
CONF_TRACK_FROM_ZONES           = 'track_from_zones'            # All zones the device is tracking from
CONF_DEVICE_TYPE                = 'device_type'
CONF_INZONE_INTERVAL            = 'inzone_interval'
CONF_UNIQUE_ID                  = 'unique_id'
CONF_EVLOG_DISPLAY_ORDER        = 'evlog_display_order'
CONF_STAT_ZONE_FNAME            = 'stat_zone_fname'

CONF_ZONE                       = 'zone'
CONF_COMMAND                    = 'command'
CONF_NAME                       = 'name'
CONF_IOSAPP_REQUEST_LOC_MAX_CNT = 'iosapp_request_loc_max_cnt'
CONF_INTERVAL                   = 'interval'

CONF_SENSORS_MONITORED_DEVICES = 'monitored_devices'

CONF_SENSORS_DEVICE            = 'device'
NAME                           = "name"
BADGE                          = "badge"
BATTERY                        = "battery"
BATTERY_STATUS                 = "battery_status"
INFO                           = "info"

CONF_SENSORS_TRACKING_UPDATE   = 'tracking_update'
INTERVAL                       = "interval"
LAST_LOCATED                   = "last_located"
LAST_UPDATE                    = "last_update"
NEXT_UPDATE                    = "next_update"

CONF_SENSORS_TRACKING_TIME     = 'tracking_time'
TRAVEL_TIME                    = "travel_time"
TRAVEL_TIME_MIN                = "travel_time_min"

CONF_SENSORS_TRACKING_DISTANCE = 'tracking_distance'
ZONE_DISTANCE_M                = 'meters_distance'
ZONE_DISTANCE_M_EDGE           = 'meters_distance_to_zone_edge'
ZONE_DISTANCE                  = "zone_distance"
HOME_DISTANCE                  = "home_distance"
DISTANCE_HOME                  = "distance_home"
DIR_OF_TRAVEL                  = "dir_of_travel"
MOVED_DISTANCE                 = "moved_distance"
MOVED_TIME_FROM                = 'moved_from'
MOVED_TIME_TO                  = 'moved_to'

CONF_SENSORS_TRACK_FROM_ZONES = 'track_from_zones'
TFZ_ZONE_INFO                 = 'tfz_zone_info'
TFZ_DISTANCE                  = 'tfz_distance'
TFZ_ZONE_DISTANCE             = 'tfz_zone_distance'
TFZ_TRAVEL_TIME               = 'tfz_travel_time'
TFZ_TRAVEL_TIME_MIN           = 'tfz_travel_time_min'
TFZ_DIR_OF_TRAVEL             = 'tfz_dir_of_travel'

CONF_SENSORS_TRACKING_OTHER   = 'tracking_other'
TRIGGER                       = "trigger"
WAZE_DISTANCE                 = "waze_distance"
CALC_DISTANCE                 = "calc_distance"

CONF_EXCLUDED_SENSORS         = "excluded_sensors"


DISTANCE           = 'distance'
CONF_SENSORS_ZONE  = 'zone'
ZONE_INFO          = 'zone_info'
ZONE               = "zone"
ZONE_DISPLAY_AS    = "zone_display_as"
ZONE_FNAME         = "zone_fname"
ZONE_NAME          = "zone_name"
ZONE_DATETIME      = "zone_changed"
LAST_ZONE          = "last_zone"
LAST_ZONE_DISPLAY_AS= "last_zone_display_as"
LAST_ZONE_FNAME    = "last_zone_fname"
LAST_ZONE_NAME     = "last_zone_name"
LAST_ZONE_DATETIME = "last_zone_changed"

CONF_SENSORS_OTHER = 'other'
GPS_ACCURACY       = "gps_accuracy"
ALTITUDE           = "altitude"
VERTICAL_ACCURACY  = "vertical_accuracy"

CF_PROFILE         = 'profile'
CF_DATA            = 'data'
CF_DATA_TRACKING   = 'tracking'
CF_DATA_DEVICES    = 'devices'
CF_DATA_GENERAL    = 'general'
CF_DATA_SENSORS    = 'sensors'

#--------------------------------------------------------
DEFAULT_PROFILE_CONF = {
        CONF_VERSION: -1,
        CONF_IC3_VERSION: VERSION,
        CONF_VERSION_INSTALL_DATE: DATETIME_ZERO,
        CONF_UPDATE_DATE: DATETIME_ZERO,
        CONF_EVLOG_CARD_DIRECTORY: EVLOG_CARD_WWW_DIRECTORY,
        CONF_EVLOG_CARD_PROGRAM: EVLOG_CARD_WWW_JS_PROG,
}

DEFAULT_TRACKING_CONF = {
        CONF_USERNAME: '',
        CONF_PASSWORD: '',
        CONF_ENCODE_PASSWORD: True,
        CONF_ICLOUD_SERVER_ENDPOINT_SUFFIX: '',
        CONF_SETUP_ICLOUD_SESSION_EARLY: True,
        CONF_DATA_SOURCE: 'famshr,iosapp',
        CONF_DEVICES: [],
}

DEFAULT_DEVICE_CONF = {
        CONF_IC3_DEVICENAME: ' ',
        CONF_FNAME: '',
        CONF_PICTURE: 'None',
        CONF_EVLOG_DISPLAY_ORDER: 0,
        CONF_UNIQUE_ID: '',
        CONF_DEVICE_TYPE: 'iPhone',
        CONF_INZONE_INTERVAL: 120,
        CONF_TRACKING_MODE: TRACK_DEVICE,
        CONF_FAMSHR_DEVICENAME: 'None',
        CONF_FAMSHR_DEVICE_ID: '',
        CONF_RAW_MODEL : '',
        CONF_MODEL: '',
        CONF_MODEL_DISPLAY_NAME: '',
        CONF_FMF_EMAIL: 'None',
        CONF_FMF_DEVICE_ID: '',
        CONF_IOSAPP_DEVICE: 'None',
        CONF_TRACK_FROM_BASE_ZONE: HOME,
        CONF_TRACK_FROM_ZONES: [HOME],
}

RANGE_DEVICE_CONF = {
        CONF_INZONE_INTERVAL: [5, 240],
}

# Used in conf_flow to reinialize the Configuration Devices
# Reset the FamShe FmF iOS App track_from_zone fields
DEFAULT_DEVICE_REINITIALIZE_CONF = DEFAULT_DEVICE_CONF.copy()
DEFAULT_DEVICE_REINITIALIZE_CONF.pop(CONF_IC3_DEVICENAME, None)
DEFAULT_DEVICE_REINITIALIZE_CONF.pop(CONF_FNAME, None)
DEFAULT_DEVICE_REINITIALIZE_CONF.pop(CONF_PICTURE, None)
DEFAULT_DEVICE_REINITIALIZE_CONF.pop(CONF_EVLOG_DISPLAY_ORDER, None)
DEFAULT_DEVICE_REINITIALIZE_CONF.pop(CONF_DEVICE_TYPE, None)
DEFAULT_DEVICE_REINITIALIZE_CONF.pop(CONF_UNIQUE_ID, None)

DEFAULT_GENERAL_CONF = {
        CONF_LOG_LEVEL: 'debug-auto-reset',

        # General Configuration Parameters
        CONF_UNIT_OF_MEASUREMENT: 'mi',
        CONF_TIME_FORMAT: '12-hour',
        CONF_DISPLAY_ZONE_FORMAT: 'fname',
        CONF_MAX_INTERVAL: 240,
        CONF_OFFLINE_INTERVAL: 20,
        CONF_EXIT_ZONE_INTERVAL: 3,
        CONF_IOSAPP_ALIVE_INTERVAL: 60,
        CONF_OLD_LOCATION_THRESHOLD: 3,
        CONF_OLD_LOCATION_ADJUSTMENT: 0,
        CONF_GPS_ACCURACY_THRESHOLD: 100,
        CONF_DISPLAY_GPS_LAT_LONG: True,
        CONF_TRAVEL_TIME_FACTOR: .6,
        CONF_TFZ_TRACKING_MAX_DISTANCE: 8,
        CONF_PASSTHRU_ZONE_TIME: .5,
        CONF_TRACK_FROM_BASE_ZONE: HOME,
        CONF_TRACK_FROM_HOME_ZONE: True,

        # inZone Configuration Parameters
        CONF_CENTER_IN_ZONE: False,
        CONF_DISCARD_POOR_GPS_INZONE: False,
        CONF_DISTANCE_BETWEEN_DEVICES: True,
        CONF_INZONE_INTERVALS: {
                IPHONE: 120,
                IPAD: 120,
                WATCH: 15,
                AIRPODS: 15,
                NO_IOSAPP: 15,
                OTHER: 120,
                },

        # Waze Configuration Parameters
        CONF_WAZE_USED: True,
        CONF_WAZE_REGION: 'us',
        CONF_WAZE_MIN_DISTANCE: 1,
        CONF_WAZE_MAX_DISTANCE: 1000,
        CONF_WAZE_REALTIME: False,
        CONF_WAZE_HISTORY_DATABASE_USED: True,
        CONF_WAZE_HISTORY_MAX_DISTANCE: 20,
        CONF_WAZE_HISTORY_TRACK_DIRECTION: 'north_south',

        # Stationary Zone Configuration Parameters
        CONF_STAT_ZONE_FNAME: 'StatZon#',
        CONF_STAT_ZONE_STILL_TIME: 8,
        CONF_STAT_ZONE_INZONE_INTERVAL: 30,
        CONF_STAT_ZONE_BASE_LATITUDE: 1,
        CONF_STAT_ZONE_BASE_LONGITUDE: 0,

        CONF_DISPLAY_TEXT_AS: ['#1', '#2', '#3', '#4', '#5', '#6', '#7', '#8', '#9', '#10'],
}

RANGE_GENERAL_CONF = {
        # General Configuration Parameters
        CONF_GPS_ACCURACY_THRESHOLD: [5, 250, 5, 'm'],
        CONF_OLD_LOCATION_THRESHOLD: [1, 60],
        CONF_OLD_LOCATION_ADJUSTMENT: [0, 60],
        CONF_MAX_INTERVAL: [15, 240],
        CONF_EXIT_ZONE_INTERVAL: [.5, 10, .5],
        CONF_IOSAPP_ALIVE_INTERVAL: [15, 240],
        CONF_OFFLINE_INTERVAL: [1, 240],
        CONF_TFZ_TRACKING_MAX_DISTANCE: [1, 100, 1, 'km'],
        CONF_TRAVEL_TIME_FACTOR: [.1, 1, .1, ''],
        CONF_PASSTHRU_ZONE_TIME: [0, 5],

        # inZone Configuration Parameters
        # CONF_INZONE_INTERVALS: {
        #         IPHONE: [5, 240],
        #         IPAD: [5, 240],
        #         WATCH: [5, 240],
        #         AIRPODS: [5, 240],
        #         NO_IOSAPP: [5, 240],
        #         OTHER: [5, 240],
        #         },

        # Waze Configuration Parameters
        CONF_WAZE_MIN_DISTANCE: [0, 1000, 5, 'km'],
        CONF_WAZE_MAX_DISTANCE: [0, 1000, 5, 'km'],
        CONF_WAZE_HISTORY_MAX_DISTANCE: [0, 1000, 5, 'km'],

        # Stationary Zone Configuration Parameters
        CONF_STAT_ZONE_STILL_TIME: [0, 60],
        CONF_STAT_ZONE_INZONE_INTERVAL: [5, 60],
        CONF_STAT_ZONE_BASE_LATITUDE:  [-90, 90, 1, ''],
        CONF_STAT_ZONE_BASE_LONGITUDE: [-180, 180, 1, ''],
}

# Default Create Sensor Field Parameter
DEFAULT_SENSORS_CONF = {
        CONF_SENSORS_MONITORED_DEVICES: [
                'md_badge',
                'md_battery', ],
        CONF_SENSORS_DEVICE: [
                NAME,
                BADGE,
                BATTERY,
                INFO, ],
        CONF_SENSORS_TRACKING_UPDATE: [
                INTERVAL,
                LAST_LOCATED,
                LAST_UPDATE,
                NEXT_UPDATE, ],
        CONF_SENSORS_TRACKING_TIME: [
                TRAVEL_TIME,
                TRAVEL_TIME_MIN, ],
        CONF_SENSORS_TRACKING_DISTANCE: [
                HOME_DISTANCE,
                ZONE_DISTANCE,
                MOVED_DISTANCE,
                DIR_OF_TRAVEL, ],
        CONF_SENSORS_TRACK_FROM_ZONES: [
                TFZ_ZONE_INFO, ],
        CONF_SENSORS_TRACKING_OTHER: [],
        CONF_SENSORS_ZONE: [
                ZONE_NAME],
        CONF_SENSORS_OTHER: [],
        CONF_EXCLUDED_SENSORS: [
                NONE_FNAME],
}

DEFAULT_DATA_CONF =  {
        CF_DATA_TRACKING: DEFAULT_TRACKING_CONF,
        CF_DATA_GENERAL: DEFAULT_GENERAL_CONF,
        CF_DATA_SENSORS: DEFAULT_SENSORS_CONF,
}

CF_DEFAULT_IC3_CONF_FILE = {
        CF_PROFILE: {
                CONF_VERSION: -1,
                CONF_VERSION_INSTALL_DATE: DATETIME_ZERO,
                CONF_UPDATE_DATE: DATETIME_ZERO,
                CONF_EVLOG_CARD_DIRECTORY: EVLOG_CARD_WWW_DIRECTORY,
                CONF_EVLOG_CARD_PROGRAM: EVLOG_CARD_WWW_JS_PROG,
        },
        CF_DATA: {
                CF_DATA_TRACKING: DEFAULT_TRACKING_CONF,
                CF_DATA_GENERAL: DEFAULT_GENERAL_CONF,
                CF_DATA_SENSORS: DEFAULT_SENSORS_CONF,
        }
}

CONF_PARAMETER_TIME_STR = [
        CONF_INZONE_INTERVAL,
        CONF_MAX_INTERVAL,
        CONF_OFFLINE_INTERVAL,
        CONF_EXIT_ZONE_INTERVAL,
        CONF_IOSAPP_ALIVE_INTERVAL,
        CONF_PASSTHRU_ZONE_TIME,
        CONF_STAT_ZONE_STILL_TIME,
        CONF_STAT_ZONE_INZONE_INTERVAL,
        CONF_OLD_LOCATION_THRESHOLD,
        CONF_OLD_LOCATION_ADJUSTMENT,
        IPHONE,
        IPAD,
        WATCH,
        AIRPODS,
        NO_IOSAPP,
        OTHER,
]

CONF_PARAMETER_FLOAT = [
        CONF_TRAVEL_TIME_FACTOR,
        CONF_STAT_ZONE_BASE_LATITUDE,
        CONF_STAT_ZONE_BASE_LONGITUDE,
]

CONF_ALL_FAMSHR_DEVICES = "all_famshr_devices"
DEFAULT_ALL_FAMSHR_DEVICES = True

# .storage/icloud3.restore_state file used to resore the device_trackers
# and sensors state during start up
RESTORE_STATE_FILE = {
        'profile': {
                CONF_VERSION: 0,
                LAST_UPDATE: DATETIME_ZERO, },
        'devices': {}
}

# Initialize the Device sensors[xxx] value from the restore_state file if
# the sensor is in the file. Otherwise, initialize to this value
USE_RESTORE_STATE_VALUE_ON_STARTUP = {
        BATTERY: 0,
        BATTERY_STATUS: '',
        BATTERY_SOURCE: '',
}

BATTERY_STATUS_FNAME = {
        'full': 'Full',
        'charging': 'Charging',
        'notcharging': 'Not Charging',
        'not charging': 'Not Charging',
        'not_charging': 'Not Charging',
        'unknown': 'Unknown',
        '': 'Unknown',
        }
# Standardize the battery status text between the ios app and icloud famshr
BATTERY_STATUS_REFORMAT = {
        'notcharging': 'not charging',
        'Not Charging': 'not charging',
        'unknown': '',
        }
DEVICE_STATUS_SET = [
        ICLOUD_DEVICE_CLASS,
        ICLOUD_BATTERY_STATUS,
        ICLOUD_LOW_POWER_MODE,
        LOCATION
        ]
DEVICE_STATUS_CODES = {
        '200': 'Online',
        '201': 'Offline',
        '203': 'Pending',
        '204': 'Unregistered',
        '0': 'Unknown',
        }
DEVICE_STATUS_ONLINE = ['Online', 'Pending', 'Unknown', 'unknown', '']
DEVICE_STATUS_OFFLINE = ['Offline']
DEVICE_STATUS_PENDING = ['Pending']

#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
#
#       TRACE AND RAWDATA VARIABLES
#
#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
TRACE_ATTRS_BASE = {
        NAME: '',
        ZONE: '',
        LAST_ZONE: '',
        INTO_ZONE_DATETIME: '',
        LATITUDE: 0,
        LONGITUDE: 0,
        TRIGGER: '',
        TIMESTAMP: DATETIME_ZERO,
        ZONE_DISTANCE: 0,
        HOME_DISTANCE: 0,
        INTERVAL: 0,
        DIR_OF_TRAVEL: '',
        MOVED_DISTANCE: 0,
        WAZE_DISTANCE: '',
        CALC_DISTANCE: 0,
        LAST_LOCATED_DATETIME: '',
        LAST_UPDATE_TIME: '',
        NEXT_UPDATE_TIME: '',
        POLL_COUNT: '',
        INFO: '',
        BATTERY: 0,
        BATTERY_LEVEL: 0,
        GPS: 0,
        GPS_ACCURACY: 0,
        VERT_ACCURACY: 0,
        }

TRACE_ICLOUD_ATTRS_BASE = {
        'name': '',
        ICLOUD_DEVICE_STATUS: '',
        LATITUDE: 0,
        LONGITUDE: 0,
        ICLOUD_TIMESTAMP: 0,
        ICLOUD_HORIZONTAL_ACCURACY: 0,
        ICLOUD_VERTICAL_ACCURACY: 0,
        'positionType': 'Wifi',
        }
FMF_FAMSHR_LOCATION_FIELDS = [
        ALTITUDE,
        LATITUDE,
        LONGITUDE,
        TIMESTAMP,
        ICLOUD_HORIZONTAL_ACCURACY,
        ICLOUD_VERTICAL_ACCURACY,
        ICLOUD_BATTERY_STATUS, ]

LOG_RAWDATA_FIELDS = [
        LATITUDE,  LONGITUDE, LOCATION_SOURCE, TRACKING_METHOD, DATA_SOURCE,
        ZONE, ZONE_DATETIME, INTO_ZONE_DATETIME, LAST_ZONE,
        TIMESTAMP, TIMESTAMP_SECS, TIMESTAMP_TIME, LOCATION_TIME, DATETIME, AGE,
        TRIGGER, BATTERY, BATTERY_LEVEL, BATTERY_STATUS,
        INTERVAL, ZONE_DISTANCE, HOME_DISTANCE, CALC_DISTANCE, WAZE_DISTANCE,
        TRAVEL_TIME, TRAVEL_TIME_MIN, DIR_OF_TRAVEL, MOVED_DISTANCE,
        DEVICE_STATUS, LOW_POWER_MODE,
        TRACKING, DEVICENAME_IOSAPP,
        AUTHENTICATED,
        LAST_UPDATE_TIME, LAST_UPDATE_DATETIME, NEXT_UPDATE_TIME, LAST_LOCATED_DATETIME,
        INFO, GPS_ACCURACY, GPS, POLL_COUNT, VERT_ACCURACY, ALTITUDE,
        ICLOUD3_VERSION,
        BADGE,
        DEVICE_ID, ID,
        ICLOUD_HORIZONTAL_ACCURACY, ICLOUD_VERTICAL_ACCURACY,
        ICLOUD_BATTERY_LEVEL, ICLOUD_BATTERY_STATUS,
        ICLOUD_DEVICE_CLASS, ICLOUD_DEVICE_STATUS, ICLOUD_LOW_POWER_MODE, ICLOUD_TIMESTAMP,
        NAME, 'emails', 'firstName', 'laststName',
        'prsId', 'batteryLevel', 'isOld', 'isInaccurate', 'phones',
        'invitationAcceptedByEmail', 'invitationFromEmail', 'invitationSentToEmail', 'data',
        'original_name',
        ]
