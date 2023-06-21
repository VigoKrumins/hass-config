from ..global_variables     import GlobalVariables as Gb
from ..const                import (NOT_SET,
                                    NEW_LINE, CRLF, CRLF_DOT,
                                    EVLOG_ALERT, EVLOG_IC3_STARTING, EVLOG_IC3_STAGE_HDR,
                                    SETTINGS_INTEGRATIONS_MSG, INTEGRATIONS_IC3_CONFIG_MSG,
                                    CONF_VERSION, ICLOUD_FNAME,
                                    )

from ..support              import start_ic3
from ..support              import config_file
from ..support              import pyicloud_ic3_interface
from ..support              import icloud_data_handler
from ..support              import determine_interval as det_interval

from ..helpers.common       import (instr, obscure_field, list_to_str, )
from ..helpers.messaging    import (broadcast_info_msg,
                                    post_event, post_error_msg, log_error_msg, post_startup_alert,
                                    post_monitor_msg, post_internal_error,
                                    log_debug_msg, log_info_msg, log_exception, log_rawdata,
                                    _trace, _traceha, )
from ..helpers.time_util    import (time_now_secs, calculate_time_zone_offset, )

import homeassistant.util.dt as dt_util


#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def stage_1_setup_variables():

    Gb.trace_prefix = 'STAGE 1 > '
    stage_title = 'Stage 1 > Initial Preparations'

    broadcast_info_msg(stage_title)

    #check to see if restart is in process
    if Gb.start_icloud3_inprocess_flag:
        return

    Gb.EvLog.display_user_message('iCloud3 > Initializiing')

    try:
        Gb.this_update_secs             = time_now_secs()
        Gb.start_icloud3_inprocess_flag = True
        Gb.restart_icloud3_request_flag = False
        Gb.all_tracking_paused_flag     = False
        Gb.config_track_devices_change_flag = False
        Gb.startup_alerts               = []
        Gb.EvLog.alert_message          = ''

        if Gb.initial_icloud3_loading_flag is False:
            post_event( f"{EVLOG_IC3_STARTING}Restarting iCloud3 v{Gb.version} > "
                        f"{dt_util.now().strftime('%A, %b %d')}")
            # Gb.EvLog.update_event_log_display("")
            # start_ic3.reinitialize_config_parameters()
            config_file.load_storage_icloud3_configuration_file()
            start_ic3.initialize_global_variables()
            start_ic3.set_global_variables_from_conf_parameters()
            start_ic3.set_zone_display_as()


        start_ic3.define_tracking_control_fields()

        post_event(f"iCloud3 Directory > {Gb.icloud3_directory}")
        if Gb.conf_profile[CONF_VERSION] == 0:
            post_event(f"iCloud3 Configuration File > {Gb.config_ic3_yaml_filename}")
        else:
            post_event(f"iCloud3 Configuration File > {Gb.icloud3_config_filename}")

        start_ic3.display_platform_operating_mode_msg()
        Gb.hass.loop.create_task(start_ic3.update_lovelace_resource_event_log_js_entry())
        start_ic3.check_ic3_event_log_file_version()

        post_monitor_msg(f"LocationInfo-{Gb.ha_location_info}")

        calculate_time_zone_offset()
        start_ic3.set_evlog_table_max_cnt()

        post_event(f"{EVLOG_IC3_STAGE_HDR}{stage_title}")
        Gb.EvLog.update_event_log_display("")

    except Exception as err:
        log_exception(err)

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def stage_2_prepare_configuration():

    Gb.trace_prefix = 'STAGE 2 > '
    stage_title = 'Stage 2 > Prepare Support Services'

    try:
        Gb.EvLog.display_user_message(stage_title)
        broadcast_info_msg(stage_title)

        if Gb.initial_icloud3_loading_flag is False:
            Gb.PyiCloud = None
            # start_ic3.initialize_PyiCloud()

        start_ic3.create_Zones_object()
        # start_ic3.reset_StationaryZones_object()
        start_ic3.create_Waze_object()

        Gb.WazeHist.load_track_from_zone_table()

    except Exception as err:
        log_exception(err)

    post_event(f"{EVLOG_IC3_STAGE_HDR}{stage_title}")
    Gb.EvLog.update_event_log_display("")

    try:
        configuration_needed_msg = ''
        # Default configuration that has not been updated or migrated from v2
        if Gb.conf_profile[CONF_VERSION] == -1:
            configuration_needed_msg = 'INITIAL INSTALLATION - CONFIGURATION IS REQUIRED'

        elif Gb.conf_profile[CONF_VERSION] == 0:
            configuration_needed_msg = 'CONFIGURATION PARAMETERS WERE MIGRATED FROM v2 to v3 - ' \
                                        'THEY MUST BE REVIEWED BEFORE STARTING ICLOUD3'
        elif Gb.conf_devices == []:
            configuration_needed_msg = 'DEVICES MUST BE SET UP TO ENABLE TRACKING'

        if configuration_needed_msg:
            post_startup_alert('iCloud3 Integration not set up')
            event_msg =(f"{EVLOG_ALERT}CONFIGURATION ALERT > {configuration_needed_msg}{CRLF}"
                        f"{CRLF}1. Select {SETTINGS_INTEGRATIONS_MSG}"
                        f"{CRLF}2. Select `+Add Integration` to add the iCloud3 integration if it is not dislayed. Then search "
                        f"for `iCloud3`, select it and complete the installation."
                        f"{CRLF}3. Select {INTEGRATIONS_IC3_CONFIG_MSG} to open the iCloud3 Configuration Wizard"
                        f"{CRLF}4. Review and setup the `iCloud Account` and `iCloud3 Devices` configuration windows "
                        f"{CRLF}5. Exit the configurator and `Restart iCloud3`")
            post_event(event_msg)

            Gb.EvLog.update_event_log_display("")

    except Exception as err:
        log_exception(err)


#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def stage_3_setup_configured_devices():

    Gb.trace_prefix = 'STAGE 3 > '
    stage_title = 'Stage 3 > Prepare Configured Devices'

    try:
        Gb.EvLog.display_user_message(stage_title)
        broadcast_info_msg(stage_title)

        # Make sure a full restart is done if all of the devices were not found in the iCloud data
        if Gb.config_track_devices_change_flag:
            pass
        elif (Gb.conf_data_source_FMF
                and Gb.fmf_device_verified_cnt < len(Gb.Devices)):
            Gb.config_track_devices_change_flag = True
        elif (Gb.conf_data_source_FAMSHR
                and Gb.famshr_device_verified_cnt < len(Gb.Devices)):
            Gb.config_track_devices_change_flag = True
        elif Gb.log_debug_flag:
            Gb.config_track_devices_change_flag = True

        start_ic3.create_Devices_object()

    except Exception as err:
        log_exception(err)

    post_event(f"{EVLOG_IC3_STAGE_HDR}{stage_title}")
    Gb.EvLog.update_event_log_display("")

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def stage_4_setup_data_sources(retry=False):

    Gb.trace_prefix = 'STAGE 4 > '
    stage_title = 'Stage 4 > Setup iCloud & iOSApp Data Source'

    # Missing username/password, PyiCloud can not be started
    if Gb.primary_data_source_ICLOUD:
        if Gb.username == '' or Gb.password == '':
            Gb.conf_data_source_FAMSHR = False
            Gb.conf_data_source_FMF    = False
            Gb.primary_data_source_ICLOUD = False
            post_startup_alert('iCloud username/password not set up')
            event_msg =(f"{EVLOG_ALERT}CONFIGURATION ALERT > The iCloud username or password has not been "
                        f"configured. iCloud will not be used for location tracking")
            post_event(event_msg)

    return_code = True
    retry_msg = ', Retrying iCloud Device Setup' if retry else ''
    Gb.EvLog.display_user_message(stage_title)
    broadcast_info_msg(stage_title)

    try:
        if Gb.primary_data_source_ICLOUD:
            post_event(f"iCloud Account Used > {obscure_field(Gb.username)}")

            if Gb.PyiCloud is None and Gb.PyiCloudInit is None:
                pyicloud_ic3_interface.create_PyiCloudService(Gb.PyiCloudInit, called_from='stage4')

            pyicloud_ic3_interface.verify_pyicloud_setup_status()

            if Gb.PyiCloud:
                if start_ic3.setup_tracked_devices_for_famshr() is False:
                    if Gb.stage_4_no_devices_found_cnt <= 10:
                        return stage_4_setup_data_sources()

                start_ic3.setup_tracked_devices_for_fmf()
                start_ic3.set_device_data_source_famshr_fmf()
                start_ic3.tune_device_data_source_famshr_fmf()
            else:
                event_msg = 'iCloud Location Services > Not used as a data source'
                post_event(event_msg)

        if Gb.conf_data_source_IOSAPP:
            start_ic3.setup_tracked_devices_for_iosapp()
        else:
            event_msg = 'iOS App > Not used as a data source'
            post_event(event_msg)

        return_code = _list_unverified_devices(retry=retry)

    except Exception as err:
        log_exception(err)
        return_code = False

    post_event(f"{EVLOG_IC3_STAGE_HDR}{stage_title}{retry_msg}")
    Gb.EvLog.update_event_log_display("")

    return return_code

#------------------------------------------------------------------
def _list_unverified_devices(retry=False):
    '''
    See if all tracked devices are verified.

    Arguments:
        retry   - True  - The verification was retried
                - False - This is the first time the verification was done

    Return:
        True  - All were verifice
        False - Some were not verified
    '''

    # Get a list of all tracked devices that have not been set p by icloud or the ios app
    unverified_devices = [devicename for devicename, Device in Gb.Devices_by_devicename_tracked.items() \
                                        if Device.verified_flag is False and Device.is_tracked]

    # Remove the unverified devices that have a famshr/fmf id but that data source is not being used
    not_tracked_devices = [devicename for devicename, Device in Gb.Devices_by_devicename_tracked.items() \
                                        if (devicename in unverified_devices \
                                            and ((Device.device_id_famshr and Gb.conf_data_source_FAMSHR) \
                                            or (Device.device_id_fmf and Gb.conf_data_source_FMF)))]

    if unverified_devices == [] or not_tracked_devices == []:
        return True

    if retry:
        post_startup_alert('Some devices could not be verified. Restart iCloud3')
        event_msg = (f"{EVLOG_ALERT}Some devices could not be verified. iCloud3 needs to be "
                        f"restarted to see if the unverified devices are available for "
                        f"tracking. If not, check the device parameters in the iCloud3 Configuration Wizard:"
                        f"{CRLF}1. {SETTINGS_INTEGRATIONS_MSG} >"
                        f"{CRLF}2. {INTEGRATIONS_IC3_CONFIG_MSG}"
                        f"{CRLF}3. iCloud3 Devices")
    else:
        event_msg = (f"{EVLOG_ALERT}ALERT > Some devices could not be verified. iCloud Location Services "
                        f"will be reinitialized")
    event_msg += (f"{CRLF}{CRLF}Unverified Devices > {', '.join(unverified_devices)}")
    post_event(event_msg)

    return False


#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def stage_5_configure_tracked_devices():

    Gb.trace_prefix = 'STAGE 5 > '
    stage_title = 'Stage 5 > Tracked Devices Configuration Summary'

    try:
        Gb.EvLog.display_user_message(stage_title)
        broadcast_info_msg(stage_title)

        # start_ic3.remove_unverified_untrackable_devices()
        start_ic3.identify_tracked_monitored_devices()
        Gb.EvLog.setup_event_log_trackable_device_info()

        start_ic3.setup_trackable_devices()
        start_ic3.display_inactive_devices()
        Gb.EvLog.update_event_log_display("")

    except Exception as err:
        log_exception(err)

    post_event(f"{EVLOG_IC3_STAGE_HDR}{stage_title}")
    Gb.EvLog.display_user_message('')

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def stage_6_initialization_complete():

    Gb.trace_prefix = 'STAGE 6 > '
    stage_title = 'iCloud3 Initialization Complete'

    broadcast_info_msg(stage_title)

    start_ic3.display_platform_operating_mode_msg()
    Gb.EvLog.display_user_message('')

    if Gb.log_debug_flag is False:
        Gb.startup_log_msgs = (NEW_LINE + '-'*55 +
                                Gb.startup_log_msgs.replace(CRLF, NEW_LINE) +
                                NEW_LINE + '-'*55)
        log_info_msg(Gb.startup_log_msgs)
    Gb.startup_log_msgs = ''

    try:
        start_ic3.display_object_lists()

        if Gb.startup_alerts != []:
            Gb.EvLog.alert_message = 'Problems occured during startup up that should be reviewed'
            alert_msg = (f"{EVLOG_ALERT}The following issues were detected when starting iCloud3. "
                        f"Scroll through the Startup Log for more information:")

            alert_msg+= list_to_str(Gb.startup_alerts, CRLF_DOT)
            post_event(alert_msg)

            # Gb.startup_alerts = []

    except Exception as err:
        log_exception(err)

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def stage_7_initial_locate():
    '''
    The PyiCloud Authentication function updates the FamShr raw data after the account
    has been authenticated. Requesting the initial data update there speeds up loading iC3
    since the iCloud acct login & authentication was started in the __init__ module.

    This routine processes the new raw FamShr data and set the initial location.

    If there are devices that use FmF and not FamShr, the FamF data will be requested
    and those devices will be updated.
    '''


    # The restart will be requested if using iCloud as a data source and no data was returned
    # from PyiCloud
    if Gb.reinitialize_icloud_devices_flag and Gb.conf_famshr_device_cnt > 0:
        return_code = reinitialize_icloud_devices()

    Gb.trace_prefix = 'INITLOC > '
    post_event("Requesting Initial Locate")
    event_msg =(f"{EVLOG_IC3_STARTING}Initializing iCloud3 v{Gb.version} > Complete")
    post_event(event_msg)

    for Device in Gb.Devices:
        if Device.PyiCloud_RawData_famshr:
            Device.update_dev_loc_data_from_raw_data_FAMSHR_FMF(Device.PyiCloud_RawData_famshr)

        elif Device.PyiCloud_RawData_fmf:
            icloud_data_handler.update_PyiCloud_RawData_data(Device, results_msg_flag=False)
            Device.update_dev_loc_data_from_raw_data_FAMSHR_FMF(Device.PyiCloud_RawData_fmf)

        else:
            continue

        Device.update_sensors_flag = True

        Gb.iCloud3.process_updated_location_data(Device, ICLOUD_FNAME)

        Device.icloud_initial_locate_done = True

#------------------------------------------------------------------
def reinitialize_icloud_devices():
    '''
    Setup restarting iCloud3 if it has not already been done.

    Return  - True - Continue with Initial Locate
            - False - Restart failes
    '''
    try:
        Gb.reinitialize_icloud_devices_cnt += 1
        if Gb.reinitialize_icloud_devices_cnt > 2:
            return

        Gb.start_icloud3_inprocess_flag = False
        Gb.reinitialize_icloud_devices_flag = False
        Gb.initial_icloud3_loading_flag = False
        Gb.all_tracking_paused_flag = True

        alert_msg = f"{EVLOG_ALERT}"
        if Gb.conf_data_source_ICLOUD:
            alert_msg +=(f"One or more devices was not verified. iCloud Location Svcs "
                        f"may be down, slow to respond or the internet may be down")
        post_event(alert_msg)

        event_msg =(f"{EVLOG_IC3_STARTING}Initializing iCloud3 > Restarting iCloud Location Services")
        post_event(event_msg)

        if Gb.PyiCloud and Gb.PyiCloud.FamilySharing:
            Gb.PyiCloud.FamilySharing.refresh_client()

        if stage_4_setup_data_sources():
            stage_4_setup_data_sources()

        stage_5_configure_tracked_devices()
        stage_6_initialization_complete()
        # stage_7_initial_locate()

        Gb.all_tracking_paused_flag = False

        alert_msg =(f"{EVLOG_ALERT}One or more devices was still not verified"
                    f"{CRLF}This can be caused by:"
                    f"{CRLF_DOT}iCloud3 Configuration Errors"
                    f"{CRLF_DOT}iCloud Location Svcs may be down or slow"
                    f"{CRLF_DOT}The internet may be down"
                    f"{CRLF}{'-'*50}{CRLF}Check the Event Log error messages, "
                    f"correct any problems and restart iCloud3")
        post_event(alert_msg)

        return False

    except Exception as err:
        log_exception(err)

    return