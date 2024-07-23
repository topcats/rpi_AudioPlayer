#!/usr/bin/python3
import sys
if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

import os
import json
import time
import datetime
import vlc
import requests
from webapiplayer import *
from nextpvrinfo import *

# Swap to working folder
os.chdir('/home/pi/AudioPlayer')

_fileConfig = 'autoplayer_config.json'
_fileStatus = 'autoplayer_status.json'

# VLC player Init
args = []
aPlayer = vlc.MediaPlayer()
aInstance = vlc.Instance()
aPlayer = aInstance.media_player_new()
aPlayerList = aInstance.media_list_player_new()
aPlayerPlayTime = 0
config_json = {}
currentsourceid = 0


def fnLoadConfig():
    """Reads the main config file into a global object"""
    global config_json
    try:
        with open(_fileConfig) as fp:
            config_json = json.load(fp)
    except Exception as ex:
        print("fnLoadConfig() ", ex)
        config_json = { "sources": [], "schedules": [], "reloadtimeout": 300}
    config_json['dt'] = int(time.time())


def fnGetCurrentSchedule():
    """Takes the Current DateTime, and finds the current Source ID"""
    global config_json

    currentdatetime = datetime.datetime.now()
    currentweekday = (currentdatetime.weekday()) + 1
    currenttimeint = fnConvertTime(currentdatetime.strftime('%H:%M'))
    if (currentweekday == 7):
        currentweekday = 0

    for scheduleitem in config_json['schedules']:
        if currentweekday in scheduleitem['day']:
            if currenttimeint >= fnConvertTime(scheduleitem['start']) and currenttimeint < fnConvertTime(scheduleitem['stop']):
                return scheduleitem['source']
    return 0


def fnGetSource(sourceid):
    """Finds the Source Object from the Config List"""
    global config_json
    for sourceitem in config_json['sources']:
        if sourceitem['id'] == sourceid:
            return sourceitem
    return None


def fnGetSourceProgrammeTitle(sourceid):
    """Gets the Programme Title from NextPvr"""
    global config_json
    _Source = fnGetSource(sourceid)
    if (_Source is not None and _Source['programme'] is not None):
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
                return responseJSON[0]['channel']['listings'][0]['name']
            else:
                response = requests.get(_Source['programme'])
                responseJSON = json.loads(response.text)
                return responseJSON
        except Exception as ex:
            print("fnGetSourceProgrammeTitle(" + str(sourceid) + ") ", ex)
    return ""


def fnConvertTime(timetext):
    timetextsplit = timetext.split(':')
    return (int(timetextsplit[0])*60) + int(timetextsplit[1])

def fnConvertPlaytime(timeint):
    return int(timeint / 1000)

def fnPlayerCallback(action):
    print("fnPlayerCallback: " + action)
    global aPlayer
    global aPlayerList
    if (action == "RELOADCONFIG"):
        print('{} Reload Config Triggered'.format(time.strftime('%H:%M')))
        fnLoadConfig()
    elif (action == "STOP"):
        if aPlayer:
            if aPlayer.get_media() and aPlayer.is_playing():
                aPlayer.stop()
        if aPlayerList:
            if aPlayerList.is_playing():
                aPlayerList.stop()
    elif (action == "NEXT"):
        if aPlayerList:
            if aPlayerList.is_playing():
                aPlayerList.next()
    elif (action == "PLAY"):
        if aPlayer:
            if aPlayer.get_media() and aPlayer.is_playing():
                aPlayer.play()
        if aPlayerList:
            if aPlayerList.is_playing():
                aPlayerList.play()
    else:
        if aPlayer:
            if aPlayer.get_media() and aPlayer.is_playing():
                aPlayer.stop()
        if aPlayerList:
            if aPlayerList.is_playing():
                aPlayerList.stop()
        currentsourceid = int(action)



# ###########################
# Sub Main()
fnLoadConfig()

#Init and Start Control Web Server
oWebApp = WebServer(config_json['webapi']['port'])
time.sleep(1)
oWebApp.ActionCallback(fnPlayerCallback)
oWebApp.start()
time.sleep(1)




# Play Control loop
while currentsourceid is not None:
    #Quick info
    status_json = {}
    status_json['dt'] = int(time.time())
    status_json['currentsourceid'] = currentsourceid
    status_json['source'] = fnGetSource(currentsourceid)

    if aPlayer:
        status_json['aPlayer'] = str(aPlayer.get_state())

        status_json['playtime'] = fnConvertPlaytime(aPlayer.get_time())
        status_json['playlength'] = fnConvertPlaytime(aPlayer.get_length())
        aPlayerMedia = aPlayer.get_media()
        if aPlayerMedia:
            status_json['title'] = "{} - {}".format(aPlayerMedia.get_meta(0), aPlayerMedia.get_meta(1))
            status_json['subtitle'] = fnGetSourceProgrammeTitle(currentsourceid)
            status_json['mrl'] = aPlayerMedia.get_mrl()
            status_json['image'] = aPlayerMedia.get_meta(15)
            #for i in range(36):
            #    print("aPlayer Media     {} : {}".format(i, aPlayerMedia.get_meta(i)))

    if aPlayerList:
        status_json['aPlayerList'] = str(aPlayerList.get_state())
        if aPlayerList.is_playing():
            aPlayerListPlayer = aPlayerList.get_media_player()
            if aPlayerListPlayer:
                status_json['playtime'] = fnConvertPlaytime(aPlayerListPlayer.get_time())
                status_json['playlength'] = fnConvertPlaytime(aPlayerListPlayer.get_length())
                aPlayerListMedia = aPlayerListPlayer.get_media()
                if aPlayerListMedia:
                    status_json['title'] = "{} - {}".format(aPlayerListMedia.get_meta(0), aPlayerListMedia.get_meta(1))
                    status_json['subtitle'] = fnGetSourceProgrammeTitle(currentsourceid)
                    status_json['mrl'] = aPlayerListMedia.get_mrl()
                    status_json['image'] = aPlayerListMedia.get_meta(15)
                    #for i in range(36):
                    #    print("aPlayerListMedia Media     {} : {}".format(i, aPlayerListMedia.get_meta(i)))

    try:
        with open(_fileStatus, 'w') as fp:
            json.dump(status_json, fp)
    except Exception as ex:
        print("subMain(Status Save) ", ex)


    # Check Schedule
    newsourceid = fnGetCurrentSchedule()
    if currentsourceid != newsourceid:
        # Stop Existing Player
        if aPlayer:
            if aPlayer.get_media() and aPlayer.is_playing():
                aPlayer.stop()
        if aPlayerList:
            if aPlayerList.is_playing():
                aPlayerList.stop()

        currentsourceid = newsourceid
        newsource = fnGetSource(newsourceid)
        if newsource is not None:
            print('{} New Station: {}'.format(time.strftime('%H:%M'), newsource['name']))
            if str(newsource['url']).startswith("upnp"):
                aMedialist = aInstance.media_list_new([str(newsource['url'])])
                aPlayerList.set_media_list(aMedialist)
                aPlayerList.play()
            else:
                aMedia = aInstance.media_new(str(newsource['url']))
                aPlayer.set_media(aMedia)
                aPlayer.play()

    #Double Check is playing (if needed) (after waiting for it to start...)
    time.sleep(20)
    if currentsourceid != 0:
        if (not aPlayer.is_playing() and not aPlayerList.is_playing()):
            print('{} Not Playing'.format(time.strftime('%H:%M')))
            currentsourceid = 0
        else:
            if (aPlayerPlayTime > 0 and aPlayerPlayTime == status_json['playtime']):
                print('{} Not Playing, time sensor'.format(time.strftime('%H:%M')))
                currentsourceid = 0
                aPlayerPlayTime = 0
            else:
                aPlayerPlayTime = status_json['playlength']

    # See if need to reload config
    if (int(time.time()) - int(config_json['dt'])) > config_json['reloadtimeout']:
        print('{} Reload Config'.format(time.strftime('%H:%M')))
        fnLoadConfig()

    #Let Play and snooze
    time.sleep(20)
