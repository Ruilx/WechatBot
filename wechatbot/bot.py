# -*- coding: utf-8 -*-

import os, io, json, random, re, thread, time, urllib, pickle
import xml.dom.minidom
import HTMLParser

import qrcode
import requests

from wechatbot.exceptions import BotServerException, BotErrorCode
from wechatbot.tools import now
from wechatbot.consts import (
    WechatAppId,
    WechatFirstLoginUrl,
    WechatQrCodeString,
    WechatSecondLoginUrl,
    WechatBotRunning,
    WechatBotSyncCheckUrl,
    WechatBotSyncUrl,
    WechatInitUrl,
    WechatHeaders,
    WechatSendMsgHeader,
    WechatBrowserHeader,
)

directory = os.path.dirname(os.path.abspath(__file__))
PklFile = "{directory}/wechat.pkl" . format(directory = directory)

class WechatBot(object):
    def __init__(self):
        self.session = requests.Session()
        self.params = {
            'uuid': None,
            'skey': None,
            'sid': None,
            'uin': None,
            'pass_ticket': None,
            'device_id': 'e' + repr(random.random())[2:17],
            'base_uri': None,
            'base_host': None,
            'base_request': None,
            'sync_host': None,
            'sync_key': None,
            'sync_key_str': None,
        }
        self.func = None
        self.htmlParser = HTMLParser.HTMLParser()

    def readSnapshot(self):
        print "[DEBUG] Read snapshot."
        with open(PklFile, 'r') as fp:
            self.params = pickle.load(fp)

    def saveSnapshot(self):
        print "[DEBUG] Save snapshot."
        with open(PklFile, 'w') as fp:
            pickle.dump(self.params, fp, protocol=2)

    def _getQrCode(self):
        print "[DEBUG] Create QRcode."
        params = {
            'appid': WechatAppId,
            'fun': "new",
            'lang': "zh_CN",
            '_': int(time.time()) * 1000 + random.randint(1, 999),
        }
        r = self.session.get(WechatFirstLoginUrl, params=params)
        self.printCookie()

        r.encoding = 'utf-8'
        data = r.text
        print "[DEBUG] WechatFirstLoginUrl: response: " + data
        regex = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"'
        pm = re.search(regex, data)
        if pm:
            code = pm.group(1)
            self.params['uuid'] = pm.group(2)
            print "[DEBUG] User's UUID: " + self.params['uuid']
            assert code == '200'
        else:
            raise BotServerException(BotErrorCode.GetUuidError)

        #img = qrcode.make(WechatQrCodeString.format(self.params['uuid']))
        #img_in_memory = io.BytesIO()
        #img.save(img_in_memory, 'png')
        #img_in_memory.seek(0)
        # files = {
        #     'smfile': img_in_memory
        # }
        # resp = requests.post(UploadImgUrl, files=files)
        # qrCodeUrl = json.loads(resp.content)['data']['url']

        #filename = 'Wechat' + '_' + self.params['uuid'] + ('_%d.png' % time.time())
        #file = open('/root/www/r/Public/upload/' + filename, 'wb')
        #file.truncate()
        #file.write(img_in_memory.getvalue())
        #file.close()
        qr = qrcode.QRCode()
        qr.add_data(WechatQrCodeString.format(self.params['uuid']))
        qr.print_tty()
        del qr
        print "Scan QRCode above. " + self.params['uuid']

        #print "Scan QRCode: " + 'http://r.ncf/Public/upload/' + filename
        #img_in_memory.truncate()

    def init(self):
        print "[DEBUG] Initializte login and save sync key."
        url = WechatInitUrl.format(base_uri=self.params['base_uri'],
                                   r=int(time.time()),
                                   pass_ticket=self.params['pass_ticket'])
        params = {
            'BaseRequest': self.params['base_request']
        }
        r = self.session.post(url, data=json.dumps(params))
        self.printCookie()

        r.encoding = 'utf-8'
        dic = json.loads(r.text)
        self.params['sync_key'] = dic['SyncKey']
        print "[DEBUG] User's sync_key: "
        print self.params['sync_key']
        self.params['sync_key_str'] = '|'.join([str(keyVal['Key']) + '_' + str(keyVal['Val']) for keyVal in self.params['sync_key']['List']])
        print "[DEBUG] User's sync_key_str: " + self.params['sync_key_str']
        return dic['BaseResponse']['Ret'] == 0

    def login(self, usingSnapShot=True):
        print "[DEBUG] Login."
        self._getQrCode() if not usingSnapShot else self.readSnapshot()

        redirectUrl = None
        tip = 1

        while not redirectUrl:
            url = WechatSecondLoginUrl.format(tip=tip, uuid=self.params['uuid'], now=now())
            resp = self.session.get(url, headers=WechatHeaders)
            self.printCookie()

            param = re.search(r'window.code=(\d+);', resp.text)
            code = param.group(1)

            if code == '201':
                tip = 0
            elif code == '200':
                redirect_urls = re.search(r'\"(?P<redirect_url>.*)\"', resp.content)
                if redirect_urls:
                    redirectUrl = redirect_urls.group('redirect_url') + '&fun=new'
                    self.params['base_uri'] = redirectUrl[:redirectUrl.rfind('/')]
                    print "[DEBUG] User's base_uri: " + self.params['base_uri']
                    temp_host = self.params['base_uri'][8:]
                    self.params['base_host'] = temp_host[:temp_host.find("/")]
                    print "[DEBUG] User's base_host: " + self.params['base_host']
            elif code == '400':
                raise BotServerException(BotErrorCode.SnapshotExpired)
            else:
                tip = 1

        resp = self.session.get(redirectUrl)
        self.printCookie()

        doc = xml.dom.minidom.parseString(resp.text.encode('utf-8'))
        root = doc.documentElement

        for node in root.childNodes:
            if node.nodeName == 'skey':
                self.params['skey'] = node.childNodes[0].data
                print "[DEBUG] User's skey: " + self.params['skey']
            elif node.nodeName == 'wxsid':
                self.params['sid'] = node.childNodes[0].data
                print "[DEBUG] User's sid: " + self.params['sid']
            elif node.nodeName == 'wxuin':
                self.params['uin'] = node.childNodes[0].data
                print "[DEBUG] User's uin: " + self.params['uin']
            elif node.nodeName == 'pass_ticket':
                self.params['pass_ticket'] = node.childNodes[0].data
                print "[DEBUG] User's pass_ticket: " + self.params['pass_ticket']
        if all([self.params['skey'], self.params['sid'], self.params['uin'], self.params['pass_ticket']]):
            self.params['base_request'] = {
                'DeviceID': self.params['device_id'],
                'Sid': self.params['sid'],
                'Skey': self.params['skey'],
                'Uin': self.params['uin'],
            }
            self.init()
            self.saveSnapshot()
            return True
        raise BotServerException(BotErrorCode.LoginError)

    def syncCheck(self):
        print "[DEBUG] Sync check."
        params = {
            'r': now(),
            'skey': self.params['skey'],
            'sid': self.params['sid'],
            'uin': self.params['uin'],
            'deviceid': self.params['device_id'],
            'synckey': self.params['sync_key_str'],
            '_': now()
        }

        url = WechatBotSyncCheckUrl.format(sync_host=self.params['sync_host'], params=urllib.urlencode(params))

        while True:
            try:
                r = self.session.get(url, timeout=30)
                self.printCookie()
                r.encoding = 'utf-8'
                data = r.text
                print "[DEBUG] SyncCheck Response: " + data
                pm = re.search(r'window.synccheck=\{retcode:"(\d+)",selector:"(\d+)"\}', data)
                retcode = pm.group(1)
                selector = pm.group(2)
                return [retcode, selector]
            except requests.exceptions.ReadTimeout:
                # This is a normal response. Just ignore this exception.
                print "[INFO] SyncCheck is a long connection, if timeout, the program auto retry."
                pass
            except:
                raise BotServerException(BotErrorCode.SyncCheckError)

    def syncHostCheck(self):
        print "[DEBUG] Sync host check."
        for host1 in ['webpush.', 'webpush2.']:
            self.params['sync_host'] = host1 + self.params['base_host']
            print "[DEBUG] User's sync_host: " + self.params['sync_host']
            try:
                code, selector = self.syncCheck()
                if code == '0':
                    return True
            except Exception as e:
                print e
        raise BotServerException(BotErrorCode.SyncHostCheckError)

    def sync(self):
        print "[DEBUG] Sync."
        url = WechatBotSyncUrl.format(base_uri=self.params['base_uri'],
                                      sid=self.params['sid'],
                                      skey=self.params['skey'],
                                      pass_ticket=self.params['pass_ticket'])
        params = {
            'BaseRequest': self.params['base_request'],
            'SyncKey': self.params['sync_key'],
            'rr': ~int(time.time())
        }
        try:
            r = self.session.post(url, data=json.dumps(params), timeout=60)
            self.printCookie()

            r.encoding = 'utf-8'
            dic = json.loads(r.text)
            if dic['BaseResponse']['Ret'] == 0:
                self.params['sync_key'] = dic['SyncKey']
                print "[DEBUG] User's sync_key: "
                print self.params['sync_key']
                self.params['sync_key_str'] = '|'.join(str(data['Key']) + '_' + str(data['Val']) for data in self.params['sync_key']['List'])
                print "[DEBUG] User's sync_key_str: " + self.params['sync_key_str']
            return dic
        except Exception:
            raise BotServerException(BotErrorCode.SyncError)

    def procMsg(self):
        print "[DEBUG] Processing message."
        self.syncHostCheck()
        while True:
            check_time = now()
            print "[DEBUG] Message request cycle"
            self.syncCheck()
            msg = self.sync()
            self.handleMsg(msg)
            check_time = now() - check_time
            if check_time < 1:
                time.sleep(1 - check_time)
            self.saveSnapshot()

    def handleMsg(self, msgs):
        print "[DEBUG] Handle message:"
        print "[INFO] Message:"
        print msgs
        #for msg in msgs['AddMsgList']:
        #    if ':<br/>!' in msg['Content']:
        #        _, msg['Content'] = msg['Content'].split('<br/>', 1)
        #    try:
        #        response = self.textReply(msg['Content'])
        #    except Exception as e:
        #        response = e.message
        #    if not msg['Content'] or not response:
        #        continue

        #    reply = {
        #        'BaseRequest' : self.params['base_request'],
        #        'Msg' : {
        #            'Type' : 1,
        #            'Content' : self.htmlParser.unescape(response), #.decode('utf-8'),
        #            'FromUserName' : msg['ToUserName'],
        #            'ToUserName' : msg['FromUserName'],
        #        },
        #        'Scene' : msg['RecommendInfo']['Scene']
        #    }
        #    try:
        #        self.sendMsg(reply)
        #    except Exception as e:
        #        reply['Msg']['Content'] = 'Error occurs: {}'.format(e)
        #        self.sendMsg(reply)
        pass

    def textReply(self, msg):
        msg = self.htmlParser.unescape(msg);
        print "[DEBUG] [DEBUG] Message pass to textReply: \033[0;31m" + msg + "\033[0m"
        if msg.startswith('<msg>') and msg.endswith('</msg>'):
            msgDom = xml.dom.minidom.parseString(msg.encode('utf-8'))
            root = msgDom.documentElement
            appmsg = root.getElementsByTagName("appmsg")[0]
            url = appmsg.getElementsByTagName("url")[0].childNodes[0].data
            print 'URL = ' + url
            if url.startswith("http"):
                r = self.session.get(url, headers=WechatBrowserHeader)
                self.printCookie()

                r.encoding('utf-8')
                print r.text
                return

    def call(self, msg):
        print "[DEBUG] Call:"
        print "[INFO] Message: "
        print msg
        return self.func(msg)

    def sendMsg(self, reply):
        print "[DEBUG] Send message."
        print "[INFO] Reply: "
        print reply
        url = self.params['base_uri'] + '/webwxsendmsg'
        msgId = str(now() * 1000) + str(random.random())[:5].replace('.', '')
        reply['Msg'].update({'LocalId': msgId, 'ClientMsgId': msgId})
        data = json.dumps(reply, ensure_ascii=False).encode('utf-8')
        for i in range(5):
            try:
                r = self.session.post(url, data=data, headers=WechatSendMsgHeader)
                self.printCookie()

            except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
                pass
            if r.status_code == 200:
                return
        raise BotServerException(BotErrorCode.SendMsgError)

    @property
    def logger(self):
        print "[DEBUG] Logger."
        with thread.allocate_lock():
            #return create_logger(self.__class__.__name__)
            print self.__class__.__name__
            return self.__class__.__name__

    def run(self):
        print "[DEBUG] Run."
        try:
            self.login(usingSnapShot=True)
        except:
            self.login(usingSnapShot=False)
        #self.logger.info(WechatBotRunning)
        print WechatBotRunning
        self.procMsg()

    def printCookie(self):
        print requests.utils.dict_from_cookiejar(requests.cookies)

