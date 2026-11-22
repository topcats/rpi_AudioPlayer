#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
TheOwls Radio Audio Player
Source: https://github.com/topcats/rpi_AudioPlayer
"""
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
    """ Player Control - Callback from Web Server """
    print("fnPlayerCallback: " + action)
    global aPlayer
    global aPlayerList
    try:
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
    except Exception as ex:
        print("fnPlayerCallback Exception: " + str(ex))


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
    """ Player Control - Action play source id """
    global currentsourceid
    global aPlayer
    global aPlayerList
    if currentsourceid != newsourceid:
        # Stop Existing Player
        fnPlayerActionStop()

        currentsourceid = newsourceid
        newsource = autoplayerfunc.fnGetSource(newsourceid)
        if newsource is not None:
            print('{} New Source Station: {}'.format(time.strftime('%H:%M'), newsource['name']))
            if str(newsource['url']).startswith("upnp") or str(newsource['url']).endswith("m3u") or str(newsource['url']).endswith("m3u8"):
                aMedialist = aInstance.media_list_new([str(newsource['url'])])
                aPlayerList.set_media_list(aMedialist)
                aPlayerList.play()
            else:
                aMedia = aInstance.media_new(str(newsource['url']))
                aPlayer.set_media(aMedia)
                aPlayer.play()


def fnPlayerActionPlayOther(newsourceurl):
    """ Player Control - Action play other source """
    global currentotherurl
    global aPlayer
    global aPlayerList
    if currentotherurl != newsourceurl:
        # Stop Existing Player
        fnPlayerActionStop()

        currentotherurl = newsourceurl
        if currentotherurl != '':
            print('{} New Other Station: {}'.format(time.strftime('%H:%M'), currentotherurl))
            if str(currentotherurl).startswith("upnp") or str(currentotherurl).endswith("m3u") or str(currentotherurl).endswith("m3u8"):
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
    
    # Get Config Mode
    configmode = autoplayerfunc.Config_json['manual']['mode']

    # Save Status to File
    configmode, status_playtime, status_playlength = autoplayerfunc.fnSaveStatus(configmode, currentsourceid, currentotherurl, aPlayer, aPlayerList)

    # Check Action
    if configmode == 1:
        # Full stop; play nothing, schedule paused
        fnPlayerActionStop()
        currentsourceid = 0
        currentotherurl = ''

    elif configmode == 2:
        # Stop; play nothing, resume at next schedule change
        fnPlayerActionStop()
        currentsourceid = 0
        currentotherurl = ''
        if autoplayerfunc.Config_json['manual']['schedule'] != autoplayerfunc.fnGetCurrentSchedule():
            autoplayerfunc.fnSaveConfigSetMode(0)

    elif configmode == 3:
        # Stop; play nothing, resume at next day
        fnPlayerActionStop()
        currentsourceid = 0
        currentotherurl = ''
        if autoplayerfunc.Config_json['manual']['day'] != autoplayerfunc.fnGetCurrentWeekday():
            autoplayerfunc.fnSaveConfigSetMode(0)

    elif configmode == 11:
        # Play Source; schedule paused
        currentotherurl = ''
        manualsourceid = autoplayerfunc.Config_json['manual']['source']
        fnPlayerActionPlaySource(manualsourceid)

    elif configmode == 12:
        # Play Source; resume at next schedule change
        currentotherurl = ''
        manualsourceid = autoplayerfunc.Config_json['manual']['source']
        fnPlayerActionPlaySource(manualsourceid)
        if autoplayerfunc.Config_json['manual']['schedule'] != autoplayerfunc.fnGetCurrentSchedule():
            autoplayerfunc.fnSaveConfigSetMode(0)

    elif configmode == 13:
        # Play Source; resume at next day
        currentotherurl = ''
        manualsourceid = autoplayerfunc.Config_json['manual']['source']
        fnPlayerActionPlaySource(manualsourceid)
        if autoplayerfunc.Config_json['manual']['day'] != autoplayerfunc.fnGetCurrentWeekday():
            autoplayerfunc.fnSaveConfigSetMode(0)

    elif configmode == 21:
        # Play Url; schedule paused
        currentsourceid = 0
        manualsourceurl = autoplayerfunc.Config_json['manual']['url']
        fnPlayerActionPlayOther(manualsourceurl)

    elif configmode == 22:
        # Play Url; resume at next schedule change
        currentsourceid = 0
        manualsourceurl = autoplayerfunc.Config_json['manual']['url']
        fnPlayerActionPlayOther(manualsourceurl)
        if autoplayerfunc.Config_json['manual']['schedule'] != autoplayerfunc.fnGetCurrentSchedule():
            autoplayerfunc.fnSaveConfigSetMode(0)

    elif configmode == 23:
        # Play Url; resume at next day
        currentsourceid = 0
        manualsourceurl = autoplayerfunc.Config_json['manual']['url']
        fnPlayerActionPlayOther(manualsourceurl)
        if autoplayerfunc.Config_json['manual']['day'] != autoplayerfunc.fnGetCurrentWeekday():
            autoplayerfunc.fnSaveConfigSetMode(0)

    else:
        # (Default) Normal running as per schedule
        currentotherurl = ''
        newsourceid = autoplayerfunc.fnGetCurrentSchedule()
        fnPlayerActionPlaySource(newsourceid)

        # Double Check is playing (if needed) (after waiting for it to start...)
        time.sleep(10)
        if currentsourceid != 0:
            if (not aPlayer.is_playing() and not aPlayerList.is_playing()):
                print('{} Not Playing'.format(time.strftime('%H:%M')))
                currentsourceid = 0
            else:
                if (aPlayerPlayTime > 0 and aPlayerPlayTime == status_playtime):
                    print('{} Not Playing, time sensor'.format(time.strftime('%H:%M')))
                    currentsourceid = 0
                    aPlayerPlayTime = 0
                else:
                    aPlayerPlayTime = status_playlength
        else:
            fnPlayerActionStop()


    # Let Play and snooze
    time.sleep(10)

    # See if need to reload config
    if (int(time.time()) - int(autoplayerfunc.Config_json['dt'])) > autoplayerfunc.Config_json['reloadtimeout']:
        print('{} Reload Config'.format(time.strftime('%H:%M')))
        autoplayerfunc.fnLoadConfig()
