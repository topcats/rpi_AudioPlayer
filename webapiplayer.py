from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
import ssl
import time
from threading import Thread
import json


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
        elif self.path.lower() == '/':
            self.__Get_Home()
        else:
            self.__Get_Catchment()


    def __Get_Status(self):
        try:
            with open('autoplayer_status.json') as fp:
                returnjson = json.load(fp)
        except Exception as ex:
            print("WebHandler.__Get_Status(Load JSON) ", ex)
            returnjson = { "dt": int(time.time()), "currentsourceid": None, "source": None, "aPlayer": None, "aPlayerList": None}
        self.send_response(200)
        self.__WriteSharedHeaders()
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(returnjson), "utf-8"))


    def __Get_Config(self):
        try:
            with open('autoplayer_config.json') as fp:
                returnjson = json.load(fp)
        except Exception as ex:
            print("WebHandler.__Get_Config(Load JSON) ", ex)
            returnjson = { "dt": int(time.time()), "sources": [], "schedules": [], "reloadtimeout": None}
        self.send_response(200)
        self.__WriteSharedHeaders()
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(returnjson), "utf-8"))


    def __Post_NextTrack(self):
        self.send_response(200)
        self.__WriteSharedHeaders()
        self.send_header("Content-type", "application/json")
        self.end_headers()
        returnjson = { "dt": int(time.time()), "action": "NEXT", "return": True}
        self.wfile.write(bytes(json.dumps(returnjson), "utf-8"))
        self.ActionCallback('NEXT')

    def __Post_StopTrack(self):
        self.send_response(200)
        self.__WriteSharedHeaders()
        self.send_header("Content-type", "application/json")
        self.end_headers()
        returnjson = { "dt": int(time.time()), "action": "STOP", "return": True}
        self.wfile.write(bytes(json.dumps(returnjson), "utf-8"))
        self.ActionCallback('STOP')

    def __Post_PlayTrack(self):
        self.send_response(200)
        self.__WriteSharedHeaders()
        self.send_header("Content-type", "application/json")
        self.end_headers()
        returnjson = { "dt": int(time.time()), "action": "PLAY", "return": True}
        self.wfile.write(bytes(json.dumps(returnjson), "utf-8"))
        self.ActionCallback('PLAY')

    def __Post_PlaySource(self,sid):
        self.send_response(200)
        self.__WriteSharedHeaders()
        self.send_header("Content-type", "application/json")
        self.end_headers()
        returnjson = { "dt": int(time.time()), "action": sid, "return": True}
        self.wfile.write(bytes(json.dumps(returnjson), "utf-8"))
        self.ActionCallback(sid)


    def __Get_Favicon(self):
        self.send_response(200)
        self.send_header("Cache-Control", "max-age=432,000")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-type", "image/x-icon")
        self.end_headers()
        with open('favicon.ico', 'rb') as file:
            self.wfile.write(file.read())


    def __Get_JQuery(self):
        self.send_response(200)
        self.send_header("Cache-Control", "max-age=432,000")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-type", "application/javascript")
        self.end_headers()
        with open('jquery-3.5.1.min.js', 'rb') as file:
            self.wfile.write(file.read())


    def __Get_Style(self):
        self.send_response(200)
        self.__WriteSharedHeaders()
        self.send_header("Content-type", "text/css")
        self.end_headers()
        with open('style.css', 'rb') as file:
            self.wfile.write(file.read())


    def __Get_JScript(self):
        self.send_response(200)
        self.__WriteSharedHeaders()
        self.send_header("Content-type", "application/javascript")
        self.end_headers()
        with open('script.js', 'rb') as file:
            self.wfile.write(file.read())

    def __Get_Home(self):
        self.send_response(200)
        self.__WriteSharedHeaders()
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.__WriteHtmlTop()
        self.wfile.write(bytes("<div class=\"body-container\"><div>", "utf-8"))

        self.wfile.write(bytes("<div id=\"pStatus\"><div><table>", "utf-8"))
        self.wfile.write(bytes("<thead><tr><th colspan=2>Player Status</th></tr></thead><tbody>", "utf-8"))
        self.wfile.write(bytes("<tr><th>Status</th><td id=\"sStatus\"></td></tr>", "utf-8"))
        self.wfile.write(bytes("<tr><th>Source</th><td id=\"sSource\"></td></tr>", "utf-8"))
        self.wfile.write(bytes("<tr><th>Title</th><td id=\"sTitle\"></td></tr>", "utf-8"))
        self.wfile.write(bytes("<tr><th>Programme</th><td id=\"sProgramme\"></td></tr>", "utf-8"))
        self.wfile.write(bytes("<tr><th>Image</th><td id=\"sImage\"></td></tr>", "utf-8"))
        self.wfile.write(bytes("<tr><th>Time</th><td id=\"sPlayTime\"></td></tr>", "utf-8"))
        self.wfile.write(bytes("</tbody>", "utf-8"))
        self.wfile.write(bytes("<tfoot><tr><td colspan=2 id=\"sControls\" class=\"playbackControls\" style=\"display: none;\"><span id=\"pStatus-Play\" data-action=\"statusplay\" title=\"Play\"></span><span id=\"pStatus-Stop\" data-action=\"statusstop\" title=\"Stop\"></span><span id=\"pStatus-Next\" data-action=\"statusnext\" title=\"Next Track\"></span></td></tr></tfoot>", "utf-8"))
        self.wfile.write(bytes("</table></div></div>", "utf-8"))

        self.wfile.write(bytes("<div id=\"pSources\"><div><table>", "utf-8"))
        self.wfile.write(bytes("<thead><tr><th colspan=3>Sources</th></tr></thead><tbody>", "utf-8"))
        self.wfile.write(bytes("</table></div></div>", "utf-8"))

        self.wfile.write(bytes("</div></div>", "utf-8"))
        self.wfile.write(bytes("<script>$(document).ready(function() {timStatus_getData = window.setInterval(function(){ status_getData(); }, 10000);timConfig_getData = window.setTimeout(function(){ config_getData(); }, 5000);$(\"span[data-action]\").click(musicplayer_setAction);});</script>", "utf-8"))
        self.__WriteHtmlEnd()


    def __Get_Catchment(self):
        self.send_response(404)
        self.__WriteSharedHeaders()
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))


    def __WriteSharedHeaders(self):
        self.send_header("X-Clacks-Overhead", "GNU Terry Pratchett, Douglas Adams, Stephen Hawking, Robin Williams, John Peel, Stan Lee, Alan Rickman (TheOwls)")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")


    def __WriteHtmlTop(self):
        self.wfile.write(bytes("<html><head>", "utf-8"))
        self.wfile.write(bytes("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">", "utf-8"))
        self.wfile.write(bytes("<title>TheOwls - Radio Music Player</title>", "utf-8"))
        self.wfile.write(bytes("<link rel=\"shortcut icon\" href=\"favicon.ico\">", "utf-8"))
        self.wfile.write(bytes("<link rel=\"stylesheet\" href=\"style.css\" type=\"text/css\">", "utf-8"))
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
