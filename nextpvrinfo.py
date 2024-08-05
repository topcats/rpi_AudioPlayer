from urllib.request import urlopen,Request
import json
import os


class NextpvrInfo():
    """Get Information From NextPvr"""

    def __init__(self, hostip=None, hostport=None, pin=None, sid=None):
        """ Nextpvr Info Grabber

        :param hostip: NextPvr Host IP or hostname
        :param hostport: NextPvr Host port number
        :param pin: NextPvr Pin Number
        """
        self._hostip = hostip
        self._hostport = hostport
        self._pin = pin
        self._sid = sid


    @property
    def sid(self):
        """ Grab back sid

        :rtype: string
        """
        return self._sid


    def __hashMe (self, thedata):
        import hashlib
        h = hashlib.md5()
        h.update(thedata.encode('utf-8'))
        return h.hexdigest()


    def __doRequest5(self, method=None):
        """ Do Main Request

        :param method: Service Method Command and any extra params
        """
        retval = False
        getResult = None
        url = "http://" + self._hostip + ":" + str(self._hostport) + '/service?method=' + method
        if (not 'session.initiate' in method and self._sid != None):
            url += '&sid=' + self._sid
        try:
            request = Request(url, headers={"Accept" : "application/json"})#, 'User-Agent': 'getsid', 'host': 'localhost'})
            json_file = urlopen(request)
            getResult = json.load(json_file)
            json_file.close()
            retval = True
        except Exception as e:
            if (str(e).startswith("HTTP Error 500")):
                getResult = "500"
            else:
                print('NextpvrInfo.__doRequest5', str(e))

        return retval, getResult


    def __sidLogin5(self):
        method = 'session.initiate&ver=1.0&device=getsid'
        ret, keys = self.__doRequest5(method)
        if ret == True:
            self._sid =  keys['sid']
            salt = keys['salt']
            hm = self.__hashMe(str(str(self._pin).zfill(4)))
            method = 'session.login&md5=' + self.__hashMe(':' + hm + ':' + salt)
            ret, login = self.__doRequest5(method)
            if ret and login['stat'] == 'ok':
                self._sid = login['sid']
            else:
                self._sid = None
                print ('NextpvrInfo.__sidLogin5', "Fail 2")
        else:
            self._sid = None
            print ('NextpvrInfo.__sidLogin5', "Fail")


    def GetChannelCurrent(self, channel_id=None):
        """ Get Current Information for Channel

        :param channel_id: Channel ID (not number)
        """

        # Get Login SID
        if (self._sid == None):
            self.__sidLogin5()

        # Do Lookup
        method = 'channel.listings.current&format=json&channel_id=' + str(channel_id)
        ret, answer = self.__doRequest5(method)

        # Hmm if sid failed
        if (ret == False and answer == "500"):
            self.__sidLogin5()
            ret, answer = self.__doRequest5(method)

        # Return results if good
        if (ret == True):
            return answer
        else:
            return None



class NextpvrSid():
    """ Save and Load SIDs for NextPvr servers """

    _fileNextPvr = 'nextpvrsid.json'

    def __init__(self, hostip=None, hostport=None):
        """ Nextpvr SID Save and load

        :param hostip: NextPvr Host IP or hostname
        :param hostport: NextPvr Host port number
        """
        self._hostip = hostip
        self._hostport = hostport


    def __getIdentifier(self):
        """ Create a server Identifier

        :return: String of the host URI and port number
        """
        return str(self._hostip) + ':' + str(self._hostport)


    def GetSid(self):
        """ Get SID for Host

        :return: SID if found else None
        """
        if (os.path.exists(self._fileNextPvr)):
            try:
                with open(self._fileNextPvr) as fp:
                    nextpvr_json = json.load(fp)

                if (nextpvr_json is not None and nextpvr_json[self.__getIdentifier()] is not None):
                    return nextpvr_json[self.__getIdentifier()]
                else:
                    return None

            except Exception as ex:
                print("NextpvrSid.GetSid()", ex)
                return None
        else:
            return None


    def SaveSid(self, sid=None):
        """ Save SID for Host in central file

        :return: True if all good
        """
        # Load Existing
        nextpvr_json = {}
        if (os.path.exists(self._fileNextPvr)):
            try:
                with open(self._fileNextPvr) as fp:
                    nextpvr_json = json.load(fp)

            except Exception as ex:
                print("NextpvrSid.SaveSid(load)", ex)

        if (nextpvr_json is None):
            nextpvr_json = {}

        # Update Config
        nextpvr_json[self.__getIdentifier()] = sid

        # Save SID
        try:
            with open(self._fileNextPvr, 'w') as fp:
                json.dump(nextpvr_json, fp)
            return True
        except Exception as ex:
            print("NextpvrSid.SaveSid(save)", ex)
            return False

