import os
import json
import time
import datetime
import requests
from nextpvrinfo import *

FileConfig = 'autoplayer_config.json'
"""Config File filename"""
FileStatus = 'autoplayer_status.json'
"""Status File filename"""

Config_json = {}
"""Current Config"""


def fnGetCurrentWeekday():
    """Takes the Current DateTime, and returns the weekday"""
    currentdatetime = datetime.datetime.now()
    return (currentdatetime.weekday()) + 1


def fnConvertTime(timetext):
    """ Convert Time to Number
    timetext: Time as Text ie '12:30'
    :return: Integer of hours and minutes
    """
    timetextsplit = timetext.split(':')
    return (int(timetextsplit[0])*60) + int(timetextsplit[1])


def fnConvertPlaytime(timeint):
    """ Convert Playtime to seconds
    timeint: Play time in milliseconds
    :return: timeint / 1000
    """
    return int(timeint / 1000)


def fnLoadConfig():
    """Reads the main config file into a global object"""
    global Config_json
    global FileConfig
    try:
        with open(FileConfig) as fp:
            Config_json = json.load(fp)

        if not 'manual' in Config_json:
            Config_json['manual'] = {}
        if not 'mode' in Config_json['manual']:
            Config_json['manual']['mode'] = 0

    except Exception as ex:
        print("autoplayerfunc.fnLoadConfig() ", ex)
        Config_json = { "sources": [], "schedules": [], "reloadtimeout": 300, "manual": { "mode": 0} }
    Config_json['dt'] = int(time.time())


def fnSaveConfigSetMode(newmode):
    """Save the New Mode to config file"""
    global Config_json
    global FileConfig
    try:
        with open(FileConfig) as fp:
            Config_json = json.load(fp)

        if not 'manual' in Config_json:
            Config_json['manual'] = {}
        if not 'mode' in Config_json['manual']:
            Config_json['manual']['mode'] = 0

        Config_json['manual']['mode'] = newmode
        
        with open(FileConfig, 'w') as fp:
            json.dump(Config_json, fp, indent=4)

    except Exception as ex:
        print("autoplayerfunc.fnSaveConfigSetMode() ", ex)
        Config_json = { "sources": [], "schedules": [], "reloadtimeout": 300, "manual": { "mode": 0} }
    Config_json['dt'] = int(time.time())


def fnGetCurrentSchedule():
    """ Takes the Current DateTime, and finds the current Source ID
    :return: Current SourceID or 0
    """
    global Config_json

    currentdatetime = datetime.datetime.now()
    currentweekday = fnGetCurrentWeekday()
    currenttimeint = fnConvertTime(currentdatetime.strftime('%H:%M'))
    if (currentweekday == 7):
        currentweekday = 0

    for scheduleitem in Config_json['schedules']:
        if currentweekday in scheduleitem['day']:
            if currenttimeint >= fnConvertTime(scheduleitem['start']) and currenttimeint < fnConvertTime(scheduleitem['stop']):
                return scheduleitem['source']
    return 0


def fnGetSource(sourceid):
    """ Finds the Source Object from the Config List
    sourceid: Source ID to lookup (int)
    :return: Source Object or None
    """
    global Config_json
    for sourceitem in Config_json['sources']:
        if sourceitem['id'] == sourceid:
            return sourceitem
    return None


def fnGetSourceProgrammeTitle(sourceid):
    """ Gets the Programme Title from NextPvr
    sourceid: SourceID to lookup from
    :return: Will return the lookup from system or empty string
    """
    _Source = fnGetSource(sourceid)
    if (_Source is not None and 'programme' in _Source and _Source['programme'] is not None):
        try:
            if 'nextpvr' in _Source['programme']:
                # Get Existing NextPvr SID
                pvrSid = NextpvrSid(hostip=_Source['programme']['nextpvr']['hostip'], hostport=_Source['programme']['nextpvr']['hostport'])
                cSid = pvrSid.GetSid()

                # Get NextPvr Info
                pvrInfo = NextpvrInfo(hostip=_Source['programme']['nextpvr']['hostip'], hostport=_Source['programme']['nextpvr']['hostport'], pin=_Source['programme']['nextpvr']['pin'], sid=cSid)
                responseJSON = pvrInfo.GetChannelCurrent(_Source['programme']['nextpvr']['channel_id'])
                cSid = pvrInfo.sid
                pvrInfo = None

                # Save Sid
                pvrSid.SaveSid(cSid)
                pvrSid = None
                if responseJSON[0]['channel']['listings'][0]['name'] == 'To Be Announced':
                    return ""
                else:
                    return responseJSON[0]['channel']['listings'][0]['name']
            else:
                response = requests.get(_Source['programme'])
                responseJSON = json.loads(response.text)
                return responseJSON
        except Exception as ex:
            print("fnGetSourceProgrammeTitle(" + str(sourceid) + ") ", ex)
    return ""
