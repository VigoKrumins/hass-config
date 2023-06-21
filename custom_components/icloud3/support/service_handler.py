#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   ICLOUD SERVICE HANDLER MODULE
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import homeassistant.helpers.config_validation as cv
from homeassistant          import data_entry_flow
import voluptuous as vol

from ..global_variables     import GlobalVariables as Gb
from ..const                import (DOMAIN,
                                    HHMMSS_ZERO, HIGH_INTEGER, EVLOG_ALERT, EVLOG_ERROR,
                                    WAZE,
                                    CMD_RESET_PYICLOUD_SESSION,
                                    LOCATION, NEXT_UPDATE_TIME, NEXT_UPDATE, INTERVAL,
                                    CONF_DEVICENAME, CONF_ZONE, CONF_COMMAND, CONF_LOG_LEVEL,
                                    ICLOUD_LOST_MODE_CAPABLE,
                                    )

from ..support              import iosapp_interface
from ..support              import start_ic3
from ..support              import determine_interval as det_interval
from ..helpers.common       import (instr, )
from ..helpers.messaging    import (post_event, post_error_msg, post_monitor_msg,
                                    write_ic3_log_recd,
                                    log_info_msg, log_debug_msg, log_exception,
                                    open_ic3_log_file, close_ic3_log_file,
                                    close_reopen_ic3_log_file, delete_open_log_file,
                                    _trace, _traceha, )
from ..helpers.time_util    import (secs_to_time, time_str_to_secs, datetime_now, secs_since, time_now, )
# from ..config_flow          import ActionSettingsFlowManager


# EvLog Action Commands
CMD_ERROR                  = 'error'
CMD_PAUSE                  = 'pause'
CMD_RESUME                 = 'resume'
CMD_WAZE                   = 'waze'
CMD_REQUEST_LOCATION       = 'location'
CMD_EXPORT_EVENT_LOG       = 'export_event_log'
CMD_WAZEHIST_MAINTENANCE   = 'wazehist_maint'
CMD_WAZEHIST_TRACK         = 'wazehist_track'
CMD_DISPLAY_STARTUP_EVENTS = 'startuplog'
CMD_RESET_PYICLOUD_SESSION = 'reset_session'
CMD_LOG_LEVEL              = 'log_level'
CMD_REFRESH_EVENT_LOG      = 'refresh_event_log'
CMD_RESTART                = 'restart'
CMD_CONFIG_FLOW            = 'config_flow'
CMD_FIND_DEVICE_ALERT      = 'find_alert'
CMD_LOCATE                 = 'locate'

REFRESH_EVLOG_FNAME             = 'Refresh Event Log'
HIDE_TRACKING_MONITORS_FNAME    = 'Hide Tracking Monitors'
SHOW_TRACKING_MONITORS_FNAME    = 'Show Tracking Monitors'


GLOBAL_ACTIONS =  [CMD_EXPORT_EVENT_LOG,
                    CMD_DISPLAY_STARTUP_EVENTS,
                    CMD_RESET_PYICLOUD_SESSION,
                    CMD_WAZE,
                    CMD_REFRESH_EVENT_LOG,
                    CMD_RESTART,
                    CMD_CONFIG_FLOW,
                    CMD_LOG_LEVEL,
                    CMD_WAZEHIST_MAINTENANCE,
                    CMD_WAZEHIST_TRACK, ]
DEVICE_ACTIONS =  [CMD_REQUEST_LOCATION,
                    CMD_PAUSE,
                    CMD_RESUME,
                    CMD_FIND_DEVICE_ALERT,
                    CMD_LOCATE, ]

NO_EVLOG_ACTION_POST_EVENT = [
                    'Show Startup Log, Errors & Alerts',
                    REFRESH_EVLOG_FNAME,
                    HIDE_TRACKING_MONITORS_FNAME,
                    SHOW_TRACKING_MONITORS_FNAME,
                    CMD_DISPLAY_STARTUP_EVENTS, ]

SERVICE_SCHEMA = vol.Schema({
    vol.Optional('command'): cv.string,
    vol.Optional('action'): cv.string,
    vol.Optional(CONF_DEVICENAME): cv.slugify,
    vol.Optional('action_fname'): cv.string,
    vol.Optional('number'): cv.string,
    vol.Optional('message'): cv.string,
})

from   homeassistant.util.location import distance

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   DEFINE THE PROCESS INVOKED BY THE HASS.SERVICES.REGISTER FOR EACH SERVICE
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def process_update_service_request(call):
    """ icloud3.update service call request """

    action       = call.data.get('command') or call.data.get('action')
    action_fname = call.data.get('action_fname')
    devicename   = call.data.get(CONF_DEVICENAME)

    update_service_handler(action, action_fname, devicename)

#--------------------------------------------------------------------
def process_restart_icloud3_service_request(call):
    """ icloud3.restart service call request  """

    Gb.restart_icloud3_request_flag = True

#--------------------------------------------------------------------
def process_find_iphone_alert_service_request(call):
    """Call the find_iphone_alert to play a sound on the phone"""

    devicename = call.data.get(CONF_DEVICENAME)

    find_iphone_alert_service_handler(devicename)

#--------------------------------------------------------------------
def process_lost_device_alert_service_request(call):
    """Call the find_iphone_alert to play a sound on the phone"""

    devicename = call.data.get(CONF_DEVICENAME)
    number     = call.data.get('number')
    message    = call.data.get('message')

    try:
        Device = Gb.Devices_by_devicename.get(devicename)
        devicename = devicename or '?'
        number = number or '?'
        message = message or ('This Phone has been lost. \
                                Please call this number to report it found.')

        if Device is None:
            result_msg = f"Failed, Unknown device_name-{devicename}"

        elif devicename == '?' or number == '?' or message == '?' :
            result_msg = (  f"Required field missing, device_name-{devicename}, "
                            f"number-{number}, message-{message}")

        elif (Device.PyiCloud_RawData_famshr
                and Device.PyiCloud_RawData_famshr.device_data
                and Device.PyiCloud_RawData_famshr.device_data.get(ICLOUD_LOST_MODE_CAPABLE, False)):

            lost_device_alert_service_handler(devicename, number, message)

            result_msg = (  f"Alert Notification sent, Device-{Device.fname_devicename}, "
                            f"Number-{number}, Message-{message}")
        else:
            result_msg = f"Device {Device.fname_devicename} can not receive Lost Device Alerts"

    except Exception as err:
        log_exception(err)
        result_msg = "Internal Error"

    post_event(f"{EVLOG_ERROR}Lost Mode Alert > {result_msg}")

#--------------------------------------------------------------------
def _post_device_event_msg(devicename, msg):
    if devicename:
        post_event(devicename, msg)
    else:
        post_event(msg)

def _post_device_monitor_msg(devicename, msg):
    if devicename:
        post_monitor_msg(devicename, msg)
    else:
        post_monitor_msg(msg)

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   DEFINE THE PROCESS INVOKED BY THE HASS.SERVICES.REGISTER FOR EACH SERVICE
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def register_icloud3_services():
    ''' Register iCloud3 Service Call Handlers '''

    try:
        Gb.hass.services.register(DOMAIN, 'action',
                    process_update_service_request, schema=SERVICE_SCHEMA)
        Gb.hass.services.register(DOMAIN, 'update',
                    process_update_service_request, schema=SERVICE_SCHEMA)
        Gb.hass.services.register(DOMAIN, 'restart',
                    process_restart_icloud3_service_request, schema=SERVICE_SCHEMA)
        Gb.hass.services.register(DOMAIN, 'find_iphone_alert',
                    process_find_iphone_alert_service_request, schema=SERVICE_SCHEMA)
        Gb.hass.services.register(DOMAIN, 'lost_device_alert',
                    process_lost_device_alert_service_request, schema=SERVICE_SCHEMA)

        return True

    except Exception as err:
        log_exception(err)

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   ROUTINES THAT HANDLE THE INDIVIDUAL SERVICE REQUESTS
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def update_service_handler(action_entry=None, action_fname=None, devicename=None):
    """
    Authenticate against iCloud and scan for devices.


    Actions:
    - pause             - stop polling for the devicename or all devices
    - resume            - resume polling devicename or all devices, reset
                            the interval override to normal interval
                            calculations
    - pause-resume      - same as above but toggles between pause and resume
    - reset             - reset everything and rescans all of the devices
    - location          - request location update from ios app
    - locate x mins     - locate in x minutes from FamShr or FmF
    - locate iosapp     - request location update from ios app
    - config_flow       - Display the Configure screens handled by the config_flow module
    """
    # Ignore Action requests during startup. They are caused by the devicename changes
    # to the EvLog attributes indicating the startup stage.
    if Gb.start_icloud3_inprocess_flag:
        return

    action = action_entry
    if action == f"{CMD_REFRESH_EVENT_LOG}+clear_alerts":
        action = CMD_REFRESH_EVENT_LOG
        Gb.EvLog.clear_alert_events()

    Gb.EvLog.clear_alert_events()
    if (action == CMD_REFRESH_EVENT_LOG
            and Gb.EvLog.secs_since_refresh <= 2
            and Gb.EvLog.last_refresh_devicename == devicename):
        _post_device_monitor_msg(devicename, f"Service Action Ignored > {action_fname}, Action-{action_entry}")
        return

    if action_fname not in NO_EVLOG_ACTION_POST_EVENT:
        _post_device_monitor_msg(devicename, f"Service Action Received > Action-{action_entry}")

    action_entry  = action_entry.replace('eventlog', 'monitor')
    action_entry  = action_entry.replace(':', '')
    action        = action_entry.split(' ')[0]
    action_option = action_entry.replace(action, '').strip()

    devicename_msg = devicename if devicename in Gb.Devices_by_devicename else None
    action_msg     = action_fname if action_fname else f"{action.title()}"

    event_msg = f"Service Action > Action-{action_msg}"
    if action_option: event_msg += f", Options-{action_option}"
    if devicename:    event_msg += f", Device-{devicename}"

    if action_fname not in NO_EVLOG_ACTION_POST_EVENT:
        _post_device_event_msg(devicename_msg, event_msg)

    if action in GLOBAL_ACTIONS:
        _handle_global_action(action, action_option)

    elif devicename == 'startup_log':
        pass

    elif action in DEVICE_ACTIONS:
        if devicename:
            Devices = [Gb.Devices_by_devicename[devicename]]
        else:
            Devices = [Device for Device in Gb.Devices_by_devicename.values()]

        if action == CMD_PAUSE:
            if devicename is None:
                Gb.all_tracking_paused_flag = True
                Gb.EvLog.display_user_message('Tracking is Paused', alert=True)
            for Device in Devices:
                Device.pause_tracking()

        elif action == CMD_RESUME:
            Gb.all_tracking_paused_flag = False
            Gb.EvLog.display_user_message('', clear_alert=True)
            for Device in Devices:
                Device.resume_tracking()

        elif action == CMD_LOCATE:
            for Device in Devices:
                _handle_action_device_locate(Device, action_option)

        elif action == CMD_REQUEST_LOCATION:
            for Device in Devices:
                _handle_action_device_location_iosapp(Device)

        elif action == 'delete_log':
            delete_open_log_file()


    if devicename == 'startup_log':
        pass
    elif (Gb.EvLog.evlog_attrs['fname'] == 'Startup Events'
            and action == 'log_level'
            and action_option == 'monitor'):
        devicename = 'startup_log'

    Gb.EvLog.update_event_log_display(devicename)
    # Gb.EvLog.clear_alert_events()


#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   HANDLER THE VARIOUS ACTION ACTION REQUESTS
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def _handle_global_action(global_action, action_option):

    if global_action == CMD_RESTART:
        Gb.log_debug_flag_restart     = Gb.log_debug_flag
        Gb.log_rawdata_flag_restart   = Gb.log_rawdata_flag
        Gb.restart_icloud3_request_flag = True
        Gb.EvLog.display_user_message('iCloud3 is Restarting', clear_alert=True)

        close_ic3_log_file()
        open_ic3_log_file()
        write_ic3_log_recd(f"\n{'-'*25} Opened by Event Log > Actions > Restart {'-'*25}")
        return

    elif global_action == CMD_EXPORT_EVENT_LOG:
        Gb.EvLog.export_event_log()
        return

    elif global_action == CMD_REFRESH_EVENT_LOG:
        return

    elif global_action == CMD_CONFIG_FLOW:
        _handle_action_config_flow_settings()
        return

    elif global_action == CMD_DISPLAY_STARTUP_EVENTS:
        return

    elif global_action == CMD_RESET_PYICLOUD_SESSION:
        # This will be handled in the 5-second ic3 loop
        Gb.evlog_action_request = CMD_RESET_PYICLOUD_SESSION
        return

    elif global_action == CMD_LOG_LEVEL:
        handle_action_log_level(action_option)
        return

    elif global_action == CMD_WAZEHIST_MAINTENANCE:
        event_msg = "Waze History > Recalculate Route Time/Distance "
        if Gb.wazehist_recalculate_time_dist_flag:
            event_msg += "Starting Immediately"
            post_event(event_msg)
            Gb.WazeHist.wazehist_recalculate_time_dist_all_zones()
        else:
            Gb.wazehist_recalculate_time_dist_flag = True
            event_msg += "Scheduled to run tonight at Midnight"
            post_event(event_msg)

    elif global_action == CMD_WAZEHIST_TRACK:
        event_msg = ("Waze History > Update Location Map Display Points "
                    "Scheduled for Midnight")
        post_event(event_msg)
        Gb.WazeHist.wazehist_update_track_sensor()
        return

#--------------------------------------------------------------------
def handle_action_log_level(action_option, change_conf_log_level=True):

    if instr(action_option, 'monitor'):
        Gb.evlog_trk_monitors_flag = (not Gb.evlog_trk_monitors_flag)
        return

    new_log_debug_flag   = Gb.log_debug_flag
    new_log_rawdata_flag = Gb.log_rawdata_flag

    if instr(action_option, 'debug'):
        new_log_debug_flag   = (not Gb.log_debug_flag)
        new_log_rawdata_flag = False

    if instr(action_option, 'rawdata'):
        new_log_rawdata_flag = (not Gb.log_rawdata_flag)
        new_log_debug_flag   = new_log_rawdata_flag

    if new_log_rawdata_flag is False:
        Gb.log_rawdata_flag_unfiltered = False

    new_log_level = 'rawdata' if new_log_rawdata_flag \
        else 'debug-auto-reset' if new_log_debug_flag \
        else 'info'

    start_ic3.set_log_level(new_log_level)
    start_ic3.update_conf_file_log_level(new_log_level)

    log_level_fname = new_log_level.replace('-', ' ').title()
    event_msg = f"Debug Log Level > {log_level_fname}"
    post_event(event_msg)

    open_ic3_log_file()
    write_ic3_log_recd(f"\n{'-'*25} Change Log Level to: {log_level_fname} {'-'*25}")

def _on_off_text(condition):
    return 'On' if condition else 'Off'

#--------------------------------------------------------------------
def _handle_action_config_flow_settings():
    '''
    Handle displaying and updating the parameters using the config_flow screens
    '''
    try:
        if Gb.SettingsFlowManager is not None:
            Gb.hass.loop.create_task(Gb.SettingsFlowManager.async_show_menu_handler())

    except Exception as err:
        log_exception(err)

#--------------------------------------------------------------------
def _handle_action_device_location_iosapp(Device):
    '''
    Request ios app location from the EvLog > Actions
    '''

    Device.display_info_msg('Updating Location')

    if Device.iosapp_monitor_flag:
        Device.iosapp_data_change_reason = f"Location Requested@{time_now()}"
        iosapp_interface.request_location(Device, force_request=True)

    Device.resume_tracking()
    Device.write_ha_sensor_state(NEXT_UPDATE, 'Locating')

#--------------------------------------------------------------------
def _handle_action_device_locate(Device, action_option):
    '''
    Set the next update time & interval from the Action > locate service call
    '''
    if action_option == 'iosapp':
        _handle_action_device_location_iosapp(Device)
        return

    if Gb.primary_data_source_ICLOUD is False or Device.is_data_source_ICLOUD is False:
        post_event(Device.devicename, "iCloud Location Tracking is not available")
        return
    try:
        interval_secs = time_str_to_secs(action_option)
        if interval_secs == 0:
            interval_secs = 5
    except:
        interval_secs = 5

    Gb.force_icloud_update_flag = True
    det_interval.update_all_device_fm_zone_sensors_interval(Device, interval_secs)
    Device.icloud_update_reason = f"Location Requested@{time_now()}"
    post_event(Device.devicename, f"Location will be updated at {Device.sensors[NEXT_UPDATE_TIME]}")
    Device.write_ha_sensors_state([NEXT_UPDATE, INTERVAL])

#--------------------------------------------------------------------
def set_ha_notification(title, message, issue=True):
    '''
    Format an HA Notification
    '''
    Gb.ha_notification = {
        'title': title,
        'message': f'{message}<br><br>*iCloud3 Notification {datetime_now()}*',
        'notification_id': DOMAIN}

    if issue:
        issue_ha_notification()

#--------------------------------------------------------------------
def issue_ha_notification():

    if Gb.ha_notification == {}:
        return

    Gb.hass.services.call("persistent_notification", "create", Gb.ha_notification)
    Gb.ha_notification = {}


#--------------------------------------------------------------------
def find_iphone_alert_service_handler(devicename):
    """
    Call the lost iPhone function if using th e FamShr tracking method.
    Otherwise, send a notification to the iOS App
    """
    Device = Gb.Devices_by_devicename[devicename]
    if Device.is_data_source_FAMSHR:
        device_id = Device.device_id_famshr
        if device_id and Gb.PyiCloud and Gb.PyiCloud.FamilySharing:
            Gb.PyiCloud.FamilySharing.play_sound(device_id, subject="Find My iPhone Alert")

            post_event(devicename, "iCloud Find My iPhone Alert sent")
            return

    event_msg =("iCloud Device not available, the alert will be sent to the iOS App")
    post_event(devicename, event_msg)

    message =   {"message": "Find My iPhone Alert",
                    "data": {
                        "push": {
                            "sound": {
                            "name": "alarm.caf",
                            "critical": 1,
                            "volume": 1
                            }
                        }
                    }
                }
    iosapp_interface.send_message_to_device(Device, message)

#--------------------------------------------------------------------
def lost_device_alert_service_handler(devicename, number, message=None):
    """
    Call the lost iPhone function if using th e FamShr tracking method.
    Otherwise, send a notification to the iOS App
    """
    if message is None:
        message = 'This Phone has been lost. Please call this number to report it found.'

    Device = Gb.Devices_by_devicename[devicename]
    if Device.is_data_source_FAMSHR:
        device_id = Device.device_id_famshr
        if device_id and Gb.PyiCloud and Gb.PyiCloud.FamilySharing:
            Gb.PyiCloud.FamilySharing.lost_device(device_id, number=number, message=message)

            post_event(devicename, "iCloud Lost Device Alert sent")
            return
