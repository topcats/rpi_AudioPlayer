#!/usr/bin/python3
import sys
if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

import os
import json
import time
import vlc
import autoplayerfunc
from webapiplayer import *

# Swap to working folder
os.chdir('/home/pi/AudioPlayer')

_fileConfig = autoplayerfunc.FileConfig
"""Config File filename link"""
_fileStatus = autoplayerfunc.FileStatus
"""Status File filename link"""

# VLC player Init
args = []
aPlayer = vlc.MediaPlayer()
aInstance = vlc.Instance()
aPlayer = aInstance.media_player_new()
aPlayerList = aInstance.media_list_player_new()
aPlayerPlayTime = 0
currentsourceid = 0
currentotherurl = ''
#currentothertitle = ''
#currentotherimage = ''



def fnPlayerCallback(action):
    print("fnPlayerCallback: " + action)
    global aPlayer
    global aPlayerList
    if (action == "RELOADCONFIG"):
        print('{} Reload Config Triggered'.format(time.strftime('%H:%M')))
        autoplayerfunc.fnLoadConfig()
    elif (action == "STOP"):
        fnPlayerActionStop()
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
        fnPlayerActionStop()
        currentsourceid = int(action)


def fnPlayerActionStop():
    """ Player Control - Action Stop """
    global aPlayer
    global aPlayerList
    if aPlayer:
        if aPlayer.get_media() and aPlayer.is_playing():
            aPlayer.stop()
    if aPlayerList:
        if aPlayerList.is_playing():
            aPlayerList.stop()


def fnPlayerActionPlaySource(newsourceid):
    """ Player Control - Action play source id"""
    global currentsourceid
    global aPlayer
    global aPlayerList
    if currentsourceid != newsourceid:
        # Stop Existing Player
        fnPlayerActionStop()

        currentsourceid = newsourceid
        newsource = autoplayerfunc.fnGetSource(newsourceid)
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


def fnPlayerActionPlayOther(newsourceurl):
    """ Player Control - Action play other source"""
    global currentotherurl
    global aPlayer
    global aPlayerList
    if currentotherurl != newsourceurl:
        # Stop Existing Player
        fnPlayerActionStop()

        currentotherurl = newsourceurl
        if currentotherurl != '':
            print('{} New Station: {}'.format(time.strftime('%H:%M'), currentotherurl))
            if str(currentotherurl).startswith("upnp"):
                aMedialist = aInstance.media_list_new([str(currentotherurl)])
                aPlayerList.set_media_list(aMedialist)
                aPlayerList.play()
            else:
                aMedia = aInstance.media_new(str(currentotherurl))
                aPlayer.set_media(aMedia)
                aPlayer.play()



# ###########################
# Sub Main()
autoplayerfunc.fnLoadConfig()

#Init and Start Control Web Server
oWebApp = WebServer(autoplayerfunc.Config_json['webapi']['port'])
time.sleep(1)
oWebApp.ActionCallback(fnPlayerCallback)
oWebApp.start()
time.sleep(1)



# Play Control loop
while currentsourceid is not None:
    #Quick info
    status_json = {}
    status_json['dt'] = int(time.time())
    status_json['mode'] = autoplayerfunc.Config_json['manual']['mode']
    status_json['currentsourceid'] = currentsourceid
    status_json['source'] = autoplayerfunc.fnGetSource(currentsourceid)

    if aPlayer:
        status_json['aPlayer'] = str(aPlayer.get_state())

        status_json['playtime'] = autoplayerfunc.fnConvertPlaytime(aPlayer.get_time())
        status_json['playlength'] = autoplayerfunc.fnConvertPlaytime(aPlayer.get_length())
        aPlayerMedia = aPlayer.get_media()
        if aPlayerMedia:
            status_json['title'] = "{} - {}".format(aPlayerMedia.get_meta(0), aPlayerMedia.get_meta(1))
            status_json['subtitle'] = autoplayerfunc.fnGetSourceProgrammeTitle(currentsourceid)
            status_json['mrl'] = aPlayerMedia.get_mrl()
            status_json['image'] = aPlayerMedia.get_meta(15)
            #for i in range(36):
            #    print("aPlayer Media     {} : {}".format(i, aPlayerMedia.get_meta(i)))

    if aPlayerList:
        status_json['aPlayerList'] = str(aPlayerList.get_state())
        if aPlayerList.is_playing():
            aPlayerListPlayer = aPlayerList.get_media_player()
            if aPlayerListPlayer:
                status_json['playtime'] = autoplayerfunc.fnConvertPlaytime(aPlayerListPlayer.get_time())
                status_json['playlength'] = autoplayerfunc.fnConvertPlaytime(aPlayerListPlayer.get_length())
                aPlayerListMedia = aPlayerListPlayer.get_media()
                if aPlayerListMedia:
                    status_json['title'] = "{} - {}".format(aPlayerListMedia.get_meta(0), aPlayerListMedia.get_meta(1))
                    status_json['subtitle'] = autoplayerfunc.fnGetSourceProgrammeTitle(currentsourceid)
                    status_json['mrl'] = aPlayerListMedia.get_mrl()
                    status_json['image'] = aPlayerListMedia.get_meta(15)
                    #for i in range(36):
                    #    print("aPlayerListMedia Media     {} : {}".format(i, aPlayerListMedia.get_meta(i)))

    try:
        with open(_fileStatus, 'w') as fp:
            json.dump(status_json, fp)
    except Exception as ex:
        print("subMain(Status Save) ", ex)


    # Check Action
    if status_json['mode'] == 1:
        # Full stop; play nothing, schedule paused
        fnPlayerActionStop()

    elif status_json['mode'] == 2:
        # Stop; play nothing, resume at next schedule change
        fnPlayerActionStop()
        if autoplayerfunc.Config_json['manual']['schedule'] != autoplayerfunc.fnGetCurrentSchedule():
            autoplayerfunc.fnSaveConfigSetMode(0)

    elif status_json['mode'] == 3:
        # Stop; play nothing, resume at next day
        fnPlayerActionStop()
        if autoplayerfunc.Config_json['manual']['day'] != autoplayerfunc.fnGetCurrentWeekday():
            autoplayerfunc.fnSaveConfigSetMode(0)

    elif status_json['mode'] == 11:
        # Play Source; schedule paused
        manualsourceid = autoplayerfunc.Config_json['manual']['source']
        fnPlayerActionPlaySource(manualsourceid)

    elif status_json['mode'] == 12:
        # Play Source; resume at next schedule change
        manualsourceid = autoplayerfunc.Config_json['manual']['source']
        fnPlayerActionPlaySource(manualsourceid)
        if autoplayerfunc.Config_json['manual']['schedule'] != autoplayerfunc.fnGetCurrentSchedule():
            autoplayerfunc.fnSaveConfigSetMode(0)

    elif status_json['mode'] == 13:
        # Play Source; resume at next day
        manualsourceid = autoplayerfunc.Config_json['manual']['source']
        fnPlayerActionPlaySource(manualsourceid)
        if autoplayerfunc.Config_json['manual']['day'] != autoplayerfunc.fnGetCurrentWeekday():
            autoplayerfunc.fnSaveConfigSetMode(0)

    elif status_json['mode'] == 21:
        # Play Url; schedule paused
        manualsourceurl = autoplayerfunc.Config_json['manual']['url']
        fnPlayerActionPlayOther(manualsourceurl)

    elif status_json['mode'] == 22:
        # Play Url; resume at next schedule change
        manualsourceurl = autoplayerfunc.Config_json['manual']['url']
        fnPlayerActionPlayOther(manualsourceurl)
        if autoplayerfunc.Config_json['manual']['schedule'] != autoplayerfunc.fnGetCurrentSchedule():
            autoplayerfunc.fnSaveConfigSetMode(0)

    elif status_json['mode'] == 23:
        # Play Url; resume at next day
        manualsourceurl = autoplayerfunc.Config_json['manual']['url']
        fnPlayerActionPlayOther(manualsourceurl)
        if autoplayerfunc.Config_json['manual']['day'] != autoplayerfunc.fnGetCurrentWeekday():
            autoplayerfunc.fnSaveConfigSetMode(0)

    else:
        # (Default) Normal running as per schedule
        newsourceid = autoplayerfunc.fnGetCurrentSchedule()
        fnPlayerActionPlaySource(newsourceid)

        #Double Check is playing (if needed) (after waiting for it to start...)
        time.sleep(10)
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
        else:
            fnPlayerActionStop()


    #Let Play and snooze
    time.sleep(20)

    # See if need to reload config
    if (int(time.time()) - int(autoplayerfunc.Config_json['dt'])) > autoplayerfunc.Config_json['reloadtimeout']:
        print('{} Reload Config'.format(time.strftime('%H:%M')))
        autoplayerfunc.fnLoadConfig()

