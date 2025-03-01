from http.server import BaseHTTPRequestHandler
import time
import json
from urllib import parse

_fileConfig = 'autoplayer_config.json'

class WebConfigEditor():
    #def __init__(self, *args):
    #    BaseHTTPRequestHandler.__init__(self, *args)

    _sourceTemplateUrlNextPvr = "http://{hostip}/live?channel={channel}&client={clientid}"
    _sourceTemplateImageNextPvr = "http://{hostip}/service?method=channel.icon&channel_id={programme}"

    def __GetPath(self, webself):
        selfpath = webself.path.lower()
        try:
            selfpath = selfpath[:selfpath.index('?')]
        except Exception as ex:
            selfpath = webself.path.lower()

        if selfpath.startswith('/configeditor'):
            selfpath = selfpath[13:]

        if selfpath.startswith('/'):
            selfpath = selfpath[1:]

        return selfpath


    def do_GET(self, webself: BaseHTTPRequestHandler):
        """Handles Web Server Requests"""
        selfpath = self.__GetPath(webself)

        if selfpath == '':
            self.__Get_Menu(webself)


    def do_POST(self, webself: BaseHTTPRequestHandler):
        """Handles Web Server Posts"""
        selfpath = self.__GetPath(webself)

        content_length = int(webself.headers["Content-Length"])
        post_data = webself.rfile.read(content_length)
        json_data = json.loads(post_data)

        retValue = False
        retMessage = 'Nothing Done'

        # Do Action
        if selfpath.startswith('schedule'):
            retValue, retMessage = self.__ProcessSchedule(webself.command.upper(), json_data)
        elif selfpath.startswith('source'):
            retValue, retMessage = self.__ProcessSource(webself.command.upper(), json_data)

        # Return to browser
        returnjson = { "dt": int(time.time()), "action": retValue, "message": retMessage, "return": True}
        webself.wfile.write(bytes(json.dumps(returnjson), "utf-8"))

        # Return to caller
        return retValue



    def __Get_Menu(self, webself: BaseHTTPRequestHandler):
        with open('web/config-home.htm', 'rb') as file:
            webself.wfile.write(file.read())


    def __ProcessSchedule(self, post_command, json_post_data):
        # print("WebHandler.__ProcessSchedule() ", post_command, json_post_data)
        if (post_command == 'PUT'):
            return self.__Schedules_Save(json_post_data)
        elif (post_command == 'PATCH'):
            return self.__Schedules_Move(json_post_data)
        elif (post_command == 'DELETE'):
            return self.__Schedules_Dele(json_post_data)
        else:
            return False, "Schedule Not coded"


    def __Schedules_Save(self, json_post_data):
        """ Schedules - Save (Add or Edit)"""
        global _fileConfig
        retMessage = "Issue"
        with open(_fileConfig) as fp:
            json_config = json.load(fp)

        json_post_data_sid = int(json_post_data['sid'])
        if (json_post_data_sid == 0):
            #Add
            newItemDays = self.__Schedules_ProcessDay(json_post_data)
            newItem = {
                "day": newItemDays,
                "start": json_post_data['Start'],
                "stop": json_post_data['Stop'],
                "source": int(json_post_data['Source'])
                }
            json_config['schedules'].append(newItem)
            retMessage = "Schedule Added"
        else:
            #Edit
            newItemDays = self.__Schedules_ProcessDay(json_post_data)
            json_post_data_sid = json_post_data_sid - 1
            json_config['schedules'][json_post_data_sid]['day'] = newItemDays
            json_config['schedules'][json_post_data_sid]['start'] = json_post_data['Start']
            json_config['schedules'][json_post_data_sid]['stop'] = json_post_data['Stop']
            json_config['schedules'][json_post_data_sid]['source'] = int(json_post_data['Source'])
            retMessage = "Schedule Item Updated"

        with open(_fileConfig, 'w') as fp:
            json.dump(json_config, fp)

        return True, retMessage


    def __Schedules_Move(self, json_post_data):
        """ Schedules - Move (Up or Down)"""
        global _fileConfig
        retMessage = "Issue"
        with open(_fileConfig) as fp:
            json_config = json.load(fp)

        json_post_data_sid = int(json_post_data['sid'])
        if (json_post_data_sid > 0):
            # Move
            olditem = json_config['schedules'][json_post_data_sid]
            json_config['schedules'][json_post_data_sid] = json_config['schedules'][json_post_data_sid-1]
            json_config['schedules'][json_post_data_sid-1] = olditem
            retMessage = "Schedule Moved"

        with open(_fileConfig, 'w') as fp:
            json.dump(json_config, fp)

        return True, retMessage


    def __Schedules_Dele(self, json_post_data):
        """ Schedules - Delete"""
        global _fileConfig
        retMessage = "Issue"
        with open(_fileConfig) as fp:
            json_config = json.load(fp)

        json_post_data_sid = int(json_post_data['sid'])
        if (json_post_data_sid > 0):
            #delete
            json_post_data_sid = json_post_data_sid - 1
            json_config['schedules'].pop(json_post_data_sid)
            retMessage = "Schedule Item Removed"

        with open(_fileConfig, 'w') as fp:
            json.dump(json_config, fp)

        return True, retMessage


    def __Schedules_ProcessDay(self, json_post_data):
        """ Schedules - Process Posted days into output"""
        newItemDays = []
        if (json_post_data['Days']['0']):
            newItemDays.append(0)
        if (json_post_data['Days']['1']):
            newItemDays.append(1)
        if (json_post_data['Days']['2']):
            newItemDays.append(2)
        if (json_post_data['Days']['3']):
            newItemDays.append(3)
        if (json_post_data['Days']['4']):
            newItemDays.append(4)
        if (json_post_data['Days']['5']):
            newItemDays.append(5)
        if (json_post_data['Days']['6']):
            newItemDays.append(6)
        return newItemDays



    def __ProcessSource(self, post_command, json_post_data):
        # print("WebHandler.__ProcessSource() ", post_command, json_post_data)
        if (post_command == 'PUT'):
            return self.__Source_Save(json_post_data)
        elif (post_command == 'DELETE'):
            return self.__Source_Dele(json_post_data)
        else:
            return False, "Source Not coded"


    def __Source_Save(self, json_post_data):
        """ Source - Save (Add or Edit)"""
        global _fileConfig
        retMessage = "Issue"
        with open(_fileConfig) as fp:
            json_config = json.load(fp)

        if (json_post_data['Name'] == ""):
            return False, "Name not set"

        json_post_data_sid = int(json_post_data['sid'])
        if (json_post_data_sid == 0):
            #Add
            newItem = {
                "name": json_post_data['Name'],
                "url": None,
                "image": None,
                "programme": None
                }
            if (json_post_data['Type'] == 'nextpvr'):
                if (json_post_data['ChannelID'] == ""):
                    return False, "Channel ID not set"
                if (json_post_data['ProgrammeID'] == ""):
                    return False, "Programme ID not set"

                newItem['url'] = self._sourceTemplateUrlNextPvr.format(hostip=json_config['template-nextpvr']['hostip'],
                                                                       channel=json_post_data['ChannelID'],
                                                                       clientid=json_config['template-nextpvr']['clientid'])
                newItem['image'] = self._sourceTemplateImageNextPvr.format(hostip=json_config['template-nextpvr']['hostip'],
                                                                           programme=json_post_data['ProgrammeID'])
                newItem['programme'] = {
                        "nextpvr": {
                            "hostip": json_config['template-nextpvr']['hostip'],
                            "hostport": json_config['template-nextpvr']['hostport'],
                            "pin": json_config['template-nextpvr']['pin'],
                            "channel_id": json_post_data['ProgrammeID']
                        }
                    }
            else:
                if (json_post_data['Url'] == ""):
                    return False, "Url not set"
                if (json_post_data['Image'] != ""):
                    newItem['image'] = json_post_data['Image']
                newItem['url'] = json_post_data['Url']

            # Get new ID
            newItemId = 1
            for sourceitem in json_config['sources']:
                if int(sourceitem['id']) > newItemId:
                    newItemId = int(sourceitem['id'])
            newItem['id'] = newItemId + 1

            json_config['sources'].append(newItem)
            retMessage = "Source Added"
        else:
            #Edit
            for sourceitem in json_config['sources']:
                if int(sourceitem['id']) == json_post_data_sid:
                    sourceitem['name'] = json_post_data['Name']
                    if (json_post_data['Type'] == 'nextpvr'):
                        if (json_post_data['ChannelID'] == ""):
                            return False, "Channel ID not set"
                        if (json_post_data['ProgrammeID'] == ""):
                            return False, "Programme ID not set"

                        sourceitem['url'] = self._sourceTemplateUrlNextPvr.format(hostip=json_config['template-nextpvr']['hostip'],
                                                                            channel=json_post_data['ChannelID'],
                                                                            clientid=json_config['template-nextpvr']['clientid'])
                        sourceitem['image'] = self._sourceTemplateImageNextPvr.format(hostip=json_config['template-nextpvr']['hostip'],
                                                                                programme=json_post_data['ProgrammeID'])
                        sourceitem['programme'] = {
                                "nextpvr": {
                                    "hostip": json_config['template-nextpvr']['hostip'],
                                    "hostport": json_config['template-nextpvr']['hostport'],
                                    "pin": json_config['template-nextpvr']['pin'],
                                    "channel_id": json_post_data['ProgrammeID']
                                }
                            }
                    else:
                        sourceitem['image'] = None
                        sourceitem['programme'] = None
                        if (json_post_data['Url'] == ""):
                            return False, "Url not set"
                        if (json_post_data['Image'] != ""):
                            sourceitem['image'] = json_post_data['Image']
                        sourceitem['url'] = json_post_data['Url']

            retMessage = "Source Item Updated"

        with open(_fileConfig, 'w') as fp:
            json.dump(json_config, fp)

        return True, retMessage


    def __Source_Dele(self, json_post_data):
        """ Source - Delete"""
        global _fileConfig
        retMessage = "Issue"
        with open(_fileConfig) as fp:
            json_config = json.load(fp)

        json_post_data_sid = int(json_post_data['sid'])
        if (json_post_data_sid > 0):
            #delete
            for sourceitem in json_config['sources']:
                if int(sourceitem['id']) == json_post_data_sid:
                    json_config['sources'].remove(sourceitem)
                    break
            retMessage = "Source Item Removed"

        with open(_fileConfig, 'w') as fp:
            json.dump(json_config, fp)

        return True, retMessage
