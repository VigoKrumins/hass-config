

from ..global_variables     import GlobalVariables as Gb
from ..const                import (NOTIFY,
                                    EVLOG_NOTICE,
                                    CRLF_DOT,
                                    )
from ..helpers.common       import (instr, )
from ..helpers.messaging    import (post_event, post_error_msg,
                                    log_info_msg, log_exception, log_rawdata, _trace, _traceha, )
from ..helpers.time_util    import (secs_to_time, secs_since, secs_to_time, secs_to_time_age_str, )
from homeassistant.helpers  import entity_registry as er, device_registry as dr

import json
from homeassistant.components import ios
from homeassistant.components.ios import notify
from homeassistant.components.notify import (
    ATTR_DATA,
    ATTR_MESSAGE,
    ATTR_TARGET,
    ATTR_TITLE,
    ATTR_TITLE_DEFAULT,
)
PUSH_URL = "https://ios-push.home-assistant.io/push"
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   Cycle through HA entity registry and get mobile_app device info that
#   can be monitored for the config_flow iosapp device selection list and
#   setting up the Device object
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def get_entity_registry_mobile_app_devices():
    iosapp_id_by_iosapp_devicename      = {}
    iosapp_devicename_by_iosapp_id      = {}
    device_info_by_iosapp_devicename    = {}
    device_model_info_by_iosapp_devicename = {} # [raw_model, model, model_display_name]
                                                # ['iPhone15,2', 'iPhone', 'iPhone 14 Pro']
    last_updt_trig_by_iosapp_devicename = {}
    notify_iosapp_devicenames           = []
    battery_level_sensors_by_iosapp_devicename = {}
    battery_state_sensors_by_iosapp_devicename = {}

    device_registry = dr.async_get(Gb.hass)

    try:
        with open(Gb.entity_registry_file, 'r') as f:
            entity_reg_data   = json.load(f)
            mobile_app_entities = [x for x in entity_reg_data['data']['entities']
                                        if x['platform'] == 'mobile_app']
            dev_trkr_entities = [x for x in mobile_app_entities
                                    if x['entity_id'].startswith('device_tracker')]
            last_updt_trigger_sensors = [x for x in mobile_app_entities
                                    if x['unique_id'].endswith('_last_update_trigger')]
            battery_level_sensors = [x for x in mobile_app_entities
                                    if x['unique_id'].endswith('_battery_level')]
            battery_state_sensors = [x for x in mobile_app_entities
                                    if x['unique_id'].endswith('_battery_state')]

            for dev_trkr_entity in dev_trkr_entities:
                if 'device_id' not in dev_trkr_entity: continue

                iosapp_devicename = dev_trkr_entity['entity_id'].replace('device_tracker.', '')
                raw_model = 'Unknown'

                log_title = (f"iosapp entity_registry entry -- {iosapp_devicename})")
                log_rawdata(log_title, dev_trkr_entity, log_rawdata_flag=True)

                device_id = dev_trkr_entity['device_id']
                try:
                    # Get raw_model from HA device_registry
                    device_reg_data = device_registry.async_get(device_id)

                    log_title = (f"iosapp device_registry entry -- {iosapp_devicename})")
                    log_rawdata(log_title, str(device_reg_data), log_rawdata_flag=True)

                    raw_model = device_reg_data.model

                except Exception as err:
                    log_exception(err)
                    pass

                disisabled_prefix = '' if dev_trkr_entity['disabled_by'] is None else 'DISABLED'
                iosapp_id_by_iosapp_devicename[iosapp_devicename]            = f"{disisabled_prefix}{dev_trkr_entity['device_id']}"
                iosapp_devicename_by_iosapp_id[dev_trkr_entity['device_id']] = iosapp_devicename

                iosapp_fname = dev_trkr_entity['name'] or dev_trkr_entity['original_name']
                device_info_by_iosapp_devicename[iosapp_devicename]       = f"{iosapp_fname} ({raw_model})"
                device_model_info_by_iosapp_devicename[iosapp_devicename] = [raw_model,'','']    # iPhone15,2;iPhone;iPhone 14 Pro

            for sensor in last_updt_trigger_sensors:
                if iosapp_devicename := iosapp_devicename_by_iosapp_id.get(sensor['device_id']):
                    last_updt_trig_by_iosapp_devicename[iosapp_devicename] = sensor['entity_id'].replace('sensor.', '')

            for sensor in battery_level_sensors:
                if iosapp_devicename := iosapp_devicename_by_iosapp_id.get(sensor['device_id']):
                    battery_level_sensors_by_iosapp_devicename[iosapp_devicename] = sensor['entity_id'].replace('sensor.', '')

            for sensor in battery_state_sensors:
                if iosapp_devicename := iosapp_devicename_by_iosapp_id.get(sensor['device_id']):
                    battery_state_sensors_by_iosapp_devicename[iosapp_devicename] = sensor['entity_id'].replace('sensor.', '')

        #notify_iosapp_devicenames = get_mobile_app_notifications()

    except Exception as err:
        log_exception(err)

    return [iosapp_id_by_iosapp_devicename,
            iosapp_devicename_by_iosapp_id,
            device_info_by_iosapp_devicename,
            device_model_info_by_iosapp_devicename,
            last_updt_trig_by_iosapp_devicename,
            notify_iosapp_devicenames,
            battery_level_sensors_by_iosapp_devicename,
            battery_state_sensors_by_iosapp_devicename]

#-----------------------------------------------------------------------------------------------------
def get_mobile_app_notifications():
    '''
    Get the mobile_app_[devicename] notify services entries from ha that are used to
    send notifications to a device.
    '''

    notify_iosapp_devicenames = []
    try:
        # Get notification ids for each device
        services = Gb.hass.services
        notify_services = dict(services.__dict__)['_services']['notify']

        for notify_service in notify_services:
            if notify_service.startswith("mobile_app_"):
                notify_iosapp_devicenames.append(notify_service)

    except Exception as err:
        #log_info_msg("iOS App Notify Service has not been set up yet. iCloud3 will retry later.")
        # log_exception(err)
        pass

    return notify_iosapp_devicenames

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   Send a message to the iosapp
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def send_message_to_device(Device, service_data):
    '''
    Send a message to the device. An example message is:
        service_data = {
            "title": "iCloud3/iOSApp Zone Action Needed",
            "message": "The iCloud3 Stationary Zone may "\
                "not be loaded in the iOSApp. Force close "\
                "the iOSApp from the iOS App Switcher. "\
                "Then restart the iOSApp to reload the HA zones. "\
                f"Distance-{dist_fm_zone_m} m, "
                f"StatZoneTestDist-{zone_radius * 2} m",
            "data": {"subtitle": "Stationary Zone Exit "\
                "Trigger was not received"}}
    '''
    try:
        if Device.iosapp_entity[NOTIFY] == '':
            return


        if service_data.get('message') != "request_location_update":
            evlog_msg = (f"{EVLOG_NOTICE}Sending Message to Device > "
                        f"Message-{service_data.get('message')}")
            post_event(Device.devicename, evlog_msg)

        Gb.hass.services.call("notify", Device.iosapp_entity[NOTIFY], service_data)

        return True

    except Exception as err:
        log_exception(err)
        event_msg =(f"iCloud3 Error > An error occurred sending a message to device "
                    f"{Device.iosapp_entity[NOTIFY]} via the Notify service. "
                    f"{CRLF_DOT}Message-{str(service_data)}")
        if instr(err, "notify/none"):
            event_msg += (f"{CRLF_DOT}The devicename can not be found")
        else:
            event_msg += f"{CRLF_DOT}Error-{err}"
        post_error_msg(Device.devicename, event_msg)

    return False

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   Using the iosapp tracking method or iCloud is disabled
#   so trigger the osapp to send a
#   location transaction
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def request_location(Device, is_alive_check=False, force_request=False):
    '''
    Send location request to phone. Check to see if one has been sent but not responded to
    and, if true, set interval based on the retry count.
    '''

    if (Gb.used_data_source_IOSAPP is False
            or Device.iosapp_monitor_flag is False
            or Device.is_offline):
        return

    devicename = Device.devicename

    try:
        # Do not send a request if one has already been sent until it is older than the offline interval
        # mod-7/5/2022-add 1200 chk, add loc_data_secs > inzone_secs
        send_msg_interval_secs = max(Gb.offline_interval_secs, 1800)
        if force_request:
            pass

        elif (Device.iosapp_request_loc_last_secs > 0
                and secs_since(Device.iosapp_request_loc_last_secs) < send_msg_interval_secs):
            return

        elif Device.is_iosapp_data_good:
            return

        if is_alive_check:
            event_msg =(f"iOSApp Alive Check > Location Requested, "
                        f"LastContact-{secs_to_time_age_str(Device.iosapp_data_secs)}")

            if Device.iosapp_request_loc_last_secs > 0:
                event_msg +=  f", LastRequest-{secs_to_time(Device.iosapp_request_loc_last_secs)}"
        else:
            event_msg =(f"iOSApp Location Requested > "
                        f"LastLocated-{secs_to_time_age_str(Device.iosapp_data_secs)}")
        post_event(devicename, event_msg)

        if Device.iosapp_request_loc_first_secs == 0:
            Device.iosapp_request_loc_first_secs = Gb.this_update_secs
        Device.iosapp_request_loc_last_secs = Gb.this_update_secs
        Device.iosapp_request_loc_sent_secs = Gb.this_update_secs
        message = {"message": "request_location_update"}
        return_code = send_message_to_device(Device, message)

        #Gb.hass.async_create_task(
        #    Gb.hass.services.async_call('notify',  entity_id, service_data))

        if return_code:
            Device.display_info_msg(event_msg)
        else:
            event_msg = f"{EVLOG_NOTICE}{event_msg} > Failed to send message"
            post_event(devicename, event_msg)

    except Exception as err:
        log_exception(err)
        error_msg = (f"iCloud3 Error > An error occurred sending a location request > "
                    f"Device-{Device.fname_devicename}, Error-{err}")
        post_error_msg(devicename, error_msg)
