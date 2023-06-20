

from ..global_variables         import GlobalVariables as Gb
from ..const                    import ( HIGH_INTEGER, HHMMSS_ZERO, DATETIME_ZERO, DATETIME_FORMAT, WAZE_USED, )

from .messaging                 import (_trace, _traceha, post_event, internal_error_msg, )
from .common                    import instr

import homeassistant.util.dt    as dt_util
import time


#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   Time conversion and formatting functions
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def time_now():
    ''' Return now in MM/DD/YYYY hh:mm:ss format'''
    return (dt_util.now().strftime(DATETIME_FORMAT)[11:19])

#--------------------------------------------------------------------
def time_now_secs():
    ''' Return the current timestamp seconds '''
    return int(time.time())

#--------------------------------------------------------------------
def time_secs():
    ''' Return the current timestamp seconds '''
    return int(time.time())

#--------------------------------------------------------------------
def time_msecs():
    ''' Return the current timestamp milli-seconds '''
    return time.time()

#--------------------------------------------------------------------
def datetime_now():
    ''' Return now in MM/DD/YYYY hh:mm:ss format'''
    return (dt_util.now().strftime(DATETIME_FORMAT)[0:19])

#--------------------------------------------------------------------
def msecs_to_time(secs):
    """ Convert milliseconds (e.g., iCloud timestamp) to hh:mm:ss """
    return secs_to_time(int(secs/1000))

#--------------------------------------------------------------------
def secs_to_time_str(secs):
    """ Create the time string from seconds """

    try:
        if secs >= 86400:
            time_str = f"{secs/86400:.2f} days"   #secs_to_dhms_str(secs)
        elif secs < 60:
            time_str = f"{secs:.0f} sec"
        elif secs < 3600:
            time_str = f"{secs/60:.0f} min"
        elif secs == 3600:
            time_str = "1 hr"
        else:
            time_str = f"{secs/3600:.1f} hrs"

        # change xx.0 min/hr --> xx min/hr
        time_str = time_str.replace('.0 ', ' ')

    except Exception as err:
        #_LOGGER.exception(err)
        time_str = ''

    return time_str

#--------------------------------------------------------------------
def mins_to_time_str(mins):
    """ Create the time string from seconds """

    try:
        if mins >= 86400:
            time_str = secs_to_dhms_str(mins*60)
        elif mins < 60:
            time_str = f"{mins:.1f} min"
        elif mins == 60:
            time_str = "1 hr"
        else:
            time_str = f"{mins/60:.1f} hrs"

        # change xx.0 min/hr --> xx min/hr
        time_str = time_str.replace('.0 ', ' ')

    except Exception as err:
        time_str = ''

    return time_str
#--------------------------------------------------------------------
def secs_to_hrs_mins_secs_str(secs):
    """ Create # hrs, # mins, # secs string """
    return f"{secs/86400:.2f} days"
    #hms_str = secs_to_dhms_str(secs)
    #hms_str = hms_str.replace('s', ' secs')
    #hms_str = hms_str.replace('m', ' mins, ')
    #hms_str = hms_str.replace('h', ' hrs, ')

    #return hms_str

#---------------------------------------------------------
def secs_to_hhmmss(secs):
    """ secs --> hh:mm:ss """

    try:
        if instr(secs, ':'):
            return secs

        w_secs = float(secs)

        hh = f"{int(w_secs // 3600):02}" if (w_secs >= 3600) else '00'
        w_secs = w_secs % 3600
        mm = f"{int(w_secs // 60):02}" if (w_secs >= 60) else '00'
        w_secs = w_secs % 60
        ss = f"{int(w_secs):02}"

    except:
        return '00:00:00'

    return f"{hh}:{mm}:{ss}"
#--------------------------------------------------------------------
def secs_to_dhms_str(secs):
    """ Create the time 0w0d0h0m0s time string from seconds """

    return f"{secs/86400:.2f} days"

    #try:
    #    secs_dhms = float(secs)
    #    dhms_str = ""
    #    if (secs >= 31557600):
    #        return f"{round(secs_dhms/31557600, 2)}y "

    #    if (secs >= 604800): dhms_str += f"{secs_dhms // 604800}w "
    #    secs_dhms = secs_dhms % 604800
    #    if (secs >= 86400): dhms_str += f"{secs_dhms // 86400}d "
    #    secs_dhms = secs_dhms % 86400
    #    if (secs >= 3600): dhms_str += f"{secs_dhms / 3600:.1f}h"

    #    dhms_str = dhms_str.replace('.0', '')

    #except:
    #    dhms_str = ""

    #return dhms_str

#--------------------------------------------------------------------
def waze_mins_to_time_str(waze_time_from_zone):
    '''
    Return:
        Waze used:
            The waze time string (hrs/mins) if Waze is used
        Waze not used:
            'N/A'
    '''

    #Display time to the nearest minute if more than 3 min away
    if Gb.waze_status != WAZE_USED:
        return  'N/A'

    mins = waze_time_from_zone * 60
    secs = 0
    if mins > 180:
        mins, secs = divmod(mins, 60)
        mins = mins + 1 if secs > 30 else mins
        secs = mins * 60

    return secs_to_time_str(secs)

#--------------------------------------------------------------------
def secs_since(secs) -> int:
    if secs == 0:
        return 0

    return round(time.time() - secs)
#--------------------------------------------------------------------
def secs_to(secs) -> int:
    if secs == 0:
        return 0

    return round(secs - time.time())
#--------------------------------------------------------------------
def hhmmss_to_secs(hhmmss):
    return time_to_secs(hhmmss)

def time_to_secs(hhmmss):
    """ Convert hh:mm:ss into seconds """
    try:
        hh_mm_ss = hhmmss.split(":")
        secs = int(hh_mm_ss[0]) * 3600 + int(hh_mm_ss[1]) * 60 + int(hh_mm_ss[2])

    except:
        secs = 0

    return secs

#--------------------------------------------------------------------
def secs_to_24hr_time(secs):
    """ Convert seconds to hh:mm:ss """
    if secs is None or secs == 0 or secs == HIGH_INTEGER:
        return HHMMSS_ZERO

    secs        = secs + Gb.timestamp_local_offset_secs
    time_format = '%H:%M:%S'
    t_struct    = time.localtime(secs)
    hhmmss      = f"{time.strftime(time_format, t_struct)}"

    return hhmmss

#--------------------------------------------------------------------
def secs_to_time(secs):
    """ Convert seconds to hh:mm:ss """
    if secs is None or secs == 0 or secs == HIGH_INTEGER:
        return HHMMSS_ZERO

    return time_to_12hrtime(secs_to_24hr_time(secs))

#--------------------------------------------------------------------
def time_to_12hrtime(hhmmss, ampm=True):
    '''
    Change hh:mm:ss time to a 12 hour time
    Input : hh:mm:ss where hh=(0-23)
            : hh:mm:ss (30s)
    Return: hh:mm:ss where hh=(0-11) with 'a' or 'p'
    '''

    try:
        if hhmmss == HHMMSS_ZERO:
            return HHMMSS_ZERO

        if (Gb.time_format_12_hour is False
                or hhmmss.endswith('a')
                or hhmmss.endswith('p')):
            return hhmmss


        hh_mm_ss    = hhmmss.split(':')
        hhmmss_hh   = int(hh_mm_ss[0])
        secs_suffix = hh_mm_ss[2].split('-')

        ap = 'a'
        if hhmmss_hh > 12:
            hhmmss_hh -= 12
            ap = 'p'
        elif hhmmss_hh == 12:
            ap = 'p'
        elif hhmmss_hh == 0:
            hhmmss_hh = 12

        if ampm is False:
            ap = ''

        hhmmss = f"{hhmmss_hh}:{hh_mm_ss[1]}:{secs_suffix[0]}{ap}"
        if len(secs_suffix) == 2:
            hhmmss += f"-{secs_suffix[1]}"
    except:
            pass

    return hhmmss

#--------------------------------------------------------------------
def time_remove_am_pm(hhmmssap):
    return hhmmssap.replace('a', '').replace('p', '')

#--------------------------------------------------------------------
def time_str_to_secs(time_str='30 min') -> int:
    """
    Calculate the seconds in the time string.
    The time attribute is in the form of '15 sec' ',
    '2 min', '60 min', etc
    """

    if time_str == "":
        return 0

    try:
        s1 = str(time_str).replace('_', ' ') + " min"
        time_part = float((s1.split(" ")[0]))
        text_part = s1.split(" ")[1]

        if text_part in ('sec', 'secs'):
            secs = time_part
        elif text_part in ('min', 'mins'):
            secs = time_part * 60
        elif text_part in ('hr', 'hrs'):
            secs = time_part * 3600
        else:
            secs = 0

        if secs < 0: secs = 0

    except:
        secs = 0

    return secs

#--------------------------------------------------------------------
def timestamp_to_time_utcsecs(utc_timestamp) -> int:
    """
    Convert iCloud timeStamp into the local time zone and
    return hh:mm:ss
    """
    ts_local = int(float(utc_timestamp)/1000) + Gb.time_zone_offset_seconds
    hhmmss   = dt_util.utc_from_timestamp(ts_local).strftime(Gb.um_time_strfmt)
    if hhmmss[0] == "0":
        hhmmss = hhmmss[1:]

    return hhmmss

#--------------------------------------------------------------------
def datetime_to_time(datetime):
    """
    Extract the time from the device timeStamp attribute
    updated by the IOS app.
    Format #1 is --'datetime': '2019-02-02 12:12:38.358-0500'
    Format #2 is --'datetime': '2019-02-02 12:12:38 (30s)'
    """

    try:
        #'0000-00-00 00:00:00' --> '00:00:00'
        if datetime == DATETIME_ZERO:
            return HHMMSS_ZERO

        #'2019-02-02 12:12:38.358-0500' --> '12:12:38'
        elif datetime.find('.') >= 0:
            return datetime[11:19]

        #'2019-02-02 12:12:38 (30s)' --> '12:12:38 (30s)'
        elif datetime.find('-') >= 0:
            return datetime[11:]

        else:
            return datetime

    except:
        pass

    return datetime

#--------------------------------------------------------------------
def datetime_to_12hrtime(datetime):
    """
    Convert 2120-07-19 14:28:34 to 2:28:34
    """
    return(time_to_12hrtime(datetime_to_time(datetime)))
#--------------------------------------------------------------------
def secs_to_datetime(secs):
    """
    Convert seconds to timestamp
    Return timestamp (2020-05-19 09:12:30)
    """

    try:
        time_struct = time.localtime(secs)
        timestamp   = time.strftime("%Y-%m-%d %H:%M:%S", time_struct)

    except Exception as err:
        timestamp = DATETIME_ZERO

    return timestamp

#--------------------------------------------------------------------
def datetime_to_secs(datetime, utc_local=False) -> int:
    """
    Convert the timestamp from the device timestamp attribute
    updated by the IOS app.
    Format is --'timestamp': '2019-02-02T12:12:38.358-0500'
    Return epoch seconds
    """
    try:
        if datetime is None or datetime == '' or datetime[0:19] == DATETIME_ZERO:
            return 0

        datetime = datetime.replace("T", " ")[0:19]
        secs = time.mktime(time.strptime(datetime, "%Y-%m-%d %H:%M:%S"))
        if utc_local is True:
            secs += Gb.time_zone_offset_seconds

    except:
        secs = 0

    return secs

#--------------------------------------------------------------------
def timestamp4(secs):
    ts_str = str(secs).replace('.0', '')
    return str(ts_str)[-4:]

#--------------------------------------------------------------------
def secs_to_time_age_str(time_secs):
    """ Secs to '17:36:05 (2 sec ago)' """
    if time_secs == 0 or time_secs == HIGH_INTEGER:
        return '00:00:00'

    time_age_str = (f"{secs_to_time(time_secs)} "
                    f"({secs_to_time_str(secs_since(time_secs))} ago)")

    return time_age_str

#--------------------------------------------------------------------
def secs_to_age_str(time_secs):
    """ Secs to `2 sec ago`, `3 mins ago`/, 1.5 hrs ago` """
    return f"{secs_to_time_str(secs_since(time_secs))} ago"

#--------------------------------------------------------------------
def format_date_time_now(strftime_parameters):
    return dt_util.now().strftime(strftime_parameters)

#--------------------------------------------------------------------
def format_time_age(time_secs):
    if time_secs == 0 or time_secs == HIGH_INTEGER:
        return 'Never'

    time_age_str = (f"{secs_to_time(time_secs)} "
                    f"({secs_to_time_str(secs_since(time_secs))} ago)")

    return time_age_str

#--------------------------------------------------------------------
def format_age(secs):
    """ Secs to `52.3y ago` """
    if secs == 0:
        return 'Never'

    return f"{secs_to_time_str(secs)} ago"

#--------------------------------------------------------------------
def format_age_ts(time_secs):
    if time_secs == 0:
        return 'Never'

    return (f"{secs_to_time_str(secs_since(time_secs))} ago")

#########################################################
#
#   TIME UTILITY ROUTINES
#
#########################################################
def calculate_time_zone_offset():
    """
    Calculate time zone offset seconds
    """
    try:
        local_zone_offset = dt_util.now().strftime('%z')
        local_zone_name   = dt_util.now().strftime('%Z')
        local_zone_offset_secs = int(local_zone_offset[1:3])*3600 + int(local_zone_offset[3:])*60
        if local_zone_offset[:1] == "-":
            local_zone_offset_secs = -1*local_zone_offset_secs

        t_now    = int(time.time())
        t_hhmmss = dt_util.now().strftime('%H%M%S')
        l_now    = time.localtime(t_now)
        l_hhmmss = time.strftime('%H%M%S', l_now)
        g_now    = time.gmtime(t_now)
        g_hhmmss = time.strftime('%H%M%S', g_now)

        if (l_hhmmss == g_hhmmss):
            Gb.timestamp_local_offset_secs = local_zone_offset_secs

        post_event( f"Local Time Zone Offset > "
                    f"UTC{local_zone_offset[:3]}:{local_zone_offset[-2:]} hrs, "
                    f"{local_zone_name}, "
                    f"Country Code-{Gb.country_code.upper()}")

    except Exception as err:
        internal_error_msg(err, 'CalcTimeOffset')
        local_zone_offset_secs = 0

    Gb.time_zone_offset_seconds = local_zone_offset_secs

    return local_zone_offset_secs
