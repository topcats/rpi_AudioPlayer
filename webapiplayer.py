from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
import ssl
import time
from threading import Thread
import json
from webconfigeditor import *
from urllib import parse
import autoplayerfunc


_fileConfig = autoplayerfunc.FileConfig
"""Config File filename link"""
_fileStatus = autoplayerfunc.FileStatus
"""Status File filename link"""


class WebHandler(BaseHTTPRequestHandler):
    def __init__(self, t1, *args):
        self.ActionCallback = t1
        BaseHTTPRequestHandler.__init__(self, *args)

    """Handles Web Server Requests"""
    def do_GET(self):
        selfpath = self.path.lower()
        try:
            selfpath = selfpath[:selfpath.index('?')]
        except Exception as ex:
            selfpath = self.path.lower()
        if selfpath == '/status':
            self.__Get_Status()
        elif selfpath == '/config':
            self.__Get_Config()
        elif selfpath == '/favicon.ico':
            self.__Get_Favicon()
        elif selfpath == '/jquery.js':
            self.__Get_JQuery()
        elif selfpath == '/script.js':
            self.__Get_JScript()
        elif selfpath == '/style.css':
            self.__Get_Style()
        elif selfpath == '/player/next':
            self.__Post_NextTrack()
        elif selfpath == '/player/stop':
            self.__Post_StopTrack()
        elif selfpath == '/player/play':
            self.__Post_PlayTrack()
        elif selfpath.startswith('/player/play/'):
            try:
                sid = self.path.lower()[self.path.rindex('/')+1:]
                sid = sid[:sid.index('?')]
                self.__Post_PlaySource(sid)
            except Exception as ex:
                self.__Get_Catchment()
        elif selfpath.startswith('/configeditor'):
            self.__Get_ConfigEditor()
        elif self.path.lower() == '/':
            self.__Get_Home()
        else:
            self.__Get_Catchment()

    """Handles Web Server Posts"""
    def do_POST(self):
        selfpath = self.path.lower()

        if selfpath.startswith('/configeditor'):
            self.__Post_ConfigEditor()
        elif selfpath.startswith('/control'):
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            json_data = json.loads(post_data)
            self.__Post_Control(json_data)


    def do_PUT(self):
        self.do_POST()

    def do_DELETE(self):
        self.do_POST()


    def __Get_Status(self):
        global _fileStatus
        try:
            with open(_fileStatus) as fp:
                returnjson = json.load(fp)
        except Exception as ex:
            print("WebHandler.__Get_Status(Load JSON) ", ex)
            returnjson = { "dt": int(time.time()), "currentsourceid": None, "source": None, "aPlayer": None, "aPlayerList": None}
        self.send_response(200)
        self.__WriteSharedHeaders(False)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(returnjson), "utf-8"))


    def __Get_Config(self):
        global _fileConfig
        try:
            with open(_fileConfig) as fp:
                returnjson = json.load(fp)
        except Exception as ex:
            print("WebHandler.__Get_Config(Load JSON) ", ex)
            returnjson = { "dt": int(time.time()), "sources": [], "schedules": [], "reloadtimeout": None}
        self.send_response(200)
        self.__WriteSharedHeaders(False)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(returnjson), "utf-8"))


    def __Post_NextTrack(self):
        self.send_response(200)
        self.__WriteSharedHeaders(False)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        returnjson = { "dt": int(time.time()), "action": "NEXT", "return": True}
        self.wfile.write(bytes(json.dumps(returnjson), "utf-8"))
        self.ActionCallback('NEXT')

    def __Post_StopTrack(self):
        self.send_response(200)
        self.__WriteSharedHeaders(False)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        returnjson = { "dt": int(time.time()), "action": "STOP", "return": True}
        self.wfile.write(bytes(json.dumps(returnjson), "utf-8"))
        self.ActionCallback('STOP')

    def __Post_PlayTrack(self):
        self.send_response(200)
        self.__WriteSharedHeaders(False)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        returnjson = { "dt": int(time.time()), "action": "PLAY", "return": True}
        self.wfile.write(bytes(json.dumps(returnjson), "utf-8"))
        self.ActionCallback('PLAY')

    def __Post_PlaySource(self,sid):
        self.send_response(200)
        self.__WriteSharedHeaders(False)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        returnjson = { "dt": int(time.time()), "action": sid, "return": True}
        self.wfile.write(bytes(json.dumps(returnjson), "utf-8"))
        self.ActionCallback(sid)

    def __Post_Control(self, json_post_data):
        global _fileConfig
        self.send_response(200)
        self.__WriteSharedHeaders(False)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        retValue = False
        retMessage = 'Nothing Done'

        with open(_fileConfig) as fp:
            json_config = json.load(fp)

        if not 'manual' in json_config:
            json_config['manual'] = {}
        if not 'mode' in json_config['manual']:
            json_config['manual']['mode'] = 0
        if not 'source' in json_config['manual']:
            json_config['manual']['source'] = 0
        if not 'url' in json_config['manual']:
            json_config['manual']['url'] = None
        if json_post_data['source'] == '':
            json_post_data['source'] = None

        if json_post_data['source'] is None or json_config['manual']['source'] != int(json_post_data['source']):
            if json_post_data['source'] is None:
                json_config['manual']['source'] = None
            else:
                json_config['manual']['source'] = int(json_post_data['source'])
            retMessage = 'Source Updated'
            retValue = True

        if json_post_data['url'] is None or json_config['manual']['url'] != json_post_data['url']:
            if json_post_data['url'] is None:
                json_config['manual']['url'] = None
            else:
                json_config['manual']['url'] = json_post_data['url']
            json_config['manual']['title'] = json_post_data['title']
            json_config['manual']['image'] = json_post_data['image']
            retMessage = 'Other Updated'
            retValue = True

        if json_config['manual']['mode'] != int(json_post_data['mode']):
            json_config['manual']['mode'] = int(json_post_data['mode'])
            if retValue:
                retMessage = retMessage + ', Mode Changed'
            else:
                retMessage = 'Mode Changed'
                retValue = True
        
        if retValue:
            json_config['manual']['day'] = autoplayerfunc.fnGetCurrentWeekday()
            json_config['manual']['schedule'] = autoplayerfunc.fnGetCurrentSchedule()

        with open(_fileConfig, 'w') as fp:
            json.dump(json_config, fp, indent=4)

        returnjson = { "dt": int(time.time()), "action": retValue, "message": retMessage, "return": True}
        self.wfile.write(bytes(json.dumps(returnjson), "utf-8"))

        if retValue:
            self.ActionCallback('RELOADCONFIG')

            if json_config['manual']['mode'] == 1 or json_config['manual']['mode'] == 2 or json_config['manual']['mode'] == 3:
                self.ActionCallback('STOP')
            #if json_config['manual']['mode'] == 11 or json_config['manual']['mode'] == 12 or json_config['manual']['mode'] == 13 or json_config['manual']['mode'] == 21 or json_config['manual']['mode'] == 22 or json_config['manual']['mode'] == 23:
            #    self.ActionCallback('PLAY')


    def __Get_Favicon(self):
        self.send_response(200)
        self.send_header("Cache-Control", "max-age=432000")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-type", "image/x-icon")
        self.end_headers()
        with open('web/favicon.ico', 'rb') as file:
            self.wfile.write(file.read())


    def __Get_JQuery(self):
        self.send_response(200)
        self.send_header("Cache-Control", "max-age=432000")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-type", "application/javascript")
        self.end_headers()
        with open('web/jquery-3.5.1.min.js', 'rb') as file:
            self.wfile.write(file.read())


    def __Get_Style(self):
        self.send_response(200)
        self.__WriteSharedHeaders()
        self.send_header("Content-type", "text/css")
        self.end_headers()
        with open('web/style.css', 'rb') as file:
            self.wfile.write(file.read())


    def __Get_JScript(self):
        self.send_response(200)
        self.__WriteSharedHeaders()
        self.send_header("Content-type", "application/javascript")
        self.end_headers()
        with open('web/script.js', 'rb') as file:
            self.wfile.write(file.read())


    def __Get_Home(self):
        self.send_response(200)
        self.__WriteSharedHeaders()
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.__WriteHtmlTop()
        with open('web/home.htm', 'rb') as file:
            self.wfile.write(file.read())
        self.__WriteHtmlEnd()


    def __Get_ConfigEditor(self):
        self.send_response(200)
        self.__WriteSharedHeaders()
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.__WriteHtmlTop()
        self.wfile.write(bytes("<h2>Configuration Editor</h2>", "utf-8"))

        # Bounce out to config class
        oConfigEditor = WebConfigEditor()
        oConfigEditor.do_GET(self)

        self.__WriteHtmlEnd()


    def __Post_ConfigEditor(self):
        self.send_response(200)
        self.__WriteSharedHeaders(False)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        # Bounce out to config class
        oConfigEditor = WebConfigEditor()
        retValue = oConfigEditor.do_POST(self)

        if (retValue):
            self.ActionCallback('RELOADCONFIG')



    def __Get_Catchment(self):
        self.send_response(404)
        self.__WriteSharedHeaders()
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head</head>", "utf-8"))
        self.wfile.write(bytes("<body></body></html>", "utf-8"))


    def __WriteSharedHeaders(self, cacheable = True):
        self.send_header("X-Clacks-Overhead", "GNU Terry Pratchett, Douglas Adams, Stephen Hawking, Robin Williams, John Peel, Stan Lee, Alan Rickman (TheOwls)")
        if (cacheable == False):
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")


    def __WriteHtmlTop(self):
        self.wfile.write(bytes("<html><head>", "utf-8"))
        self.wfile.write(bytes("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">", "utf-8"))
        self.wfile.write(bytes("<title>TheOwls - Radio Music Player</title>", "utf-8"))
        self.wfile.write(bytes("<link rel=\"shortcut icon\" href=\"/favicon.ico\">", "utf-8"))
        self.wfile.write(bytes("<link rel=\"stylesheet\" href=\"/style.css\" type=\"text/css\">", "utf-8"))
        self.wfile.write(bytes("<script src=\"/jquery.js\"></script>", "utf-8"))
        self.wfile.write(bytes("<script src=\"/script.js\"></script>", "utf-8"))
        self.wfile.write(bytes("</head>", "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<h1>TheOwls - Radio Music Player</h1>", "utf-8"))


    def __WriteHtmlEnd(self):
        self.wfile.write(bytes("<footer><div class=""container""><p>&copy; 2024 <a href=\"https://dev.the-owls.org\" target=\"_blank\" title=\"TheOwls Software Solutions\">TheOwls</a></p></div></footer>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))


class WebServer(Thread):
    """Host for Web server"""
    def __init__(self, port=8888, ssl=False):
        Thread.__init__(self)
        Thread.daemon = True
        def WebHandlerWrap(*args):
            WebHandler(self.callback, *args)
        self._port = port
        self._HostServer = ThreadingHTTPServer(('', port), WebHandlerWrap)
        if ssl:
            self._HostServer.socket = ssl.wrap_socket (self._HostServer.socket,
                keyfile = "webkey.pem",
                certfile = "webcert.pem",
                server_side = True)
            print ("Webserver Init (SSL):" + str(port))
        else:
            print ("Webserver Init :" + str(port))

    def run(self):
        """Starts the Web Api Server"""
        print ("Start WebServer")
        self._HostServer.serve_forever()

    def terminate(self):
        """Stops the Web Api"""
        print ("Kill WebServer")
        self._HostServer.server_close()

    def ActionCallback(self, callbackfunction):
        self.callback = callbackfunction
