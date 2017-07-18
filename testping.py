#!/root/src/anaconda2/bin/python
# -*- coding: utf-8 -*-

from wechatbot import WechatBot

class MyBot(WechatBot):
    #def textReply(self, msg):
    #    return msg
    pass

if __name__ == '__main__':
    bot = MyBot()
    bot.run()

