# -*- coding: utf-8 -*-

ALL_KEYWORDS = 'WX_BOT_KEYWORDS'

RESERVED_COMMAND_LIST = [
    'help',
]

UPLOAD_IMG_URL = "https://localhost/api/upload"

WechatAppId = "wx782c26e4c19acffb"
WechatFirstLoginUrl = "https://login.weixin.qq.com/jslogin"
WechatQrCodeString = "https://login.weixin.qq.com/l/{}"
WechatSecondLoginUrl = "https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?tip={tip}&uuid={uuid}&_={now}"
WechatBotRunning = "Running..."
WechatBotSyncCheckUrl = "https://{sync_host}/cgi-bin/mmwebwx-bin/synccheck?{params}"
WechatBotSyncUrl = "{base_uri}/webwxsync?sid={sid}&skey={skey}&lang=en_US&pass_ticket={pass_ticket}"
WechatInitUrl = "{base_uri}/webwxinit?r={r}i&lang=en_US&pass_ticket={pass_ticket}"

WechatHeaders = {
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    'accept-encoding': "gzip, deflate, br",
    'accept-language': "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
    'cache-control': "max-age=0",
    'host': "login.wx.qq.com",
    'content-type': "application/json; charset=UTF-8",
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
}

WechatSendMsgHeader = {
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    'accept-encoding': "gzip, deflate, br",
    'accept-language': "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
    'cache-control': "max-age=0",
    'content-type': "application/json; charset=UTF-8",
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
}

WechatBrowserHeader = {
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    'accept-encoding': "gzip, deflate, br",
    'accept-language': "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
    'cache-control': "max-age=0",
    'host': "wx.qq.com",
    'user-agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_2 like Mac OS X) AppleWebKit/603.2.4 (KHTML, like Gecko) Mobile/14F89 MicroMessenger/6.5.10 NetType/WIFI Language/zh_CN"
}

