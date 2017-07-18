# -*- coding: utf-8 -*-
from enum import Enum

class BotErrorCode(Enum):
    MissingParameter = 0
    UnknownCommand = 1
    ReservedCommand = 2
    DuplicatedCommand = 3
    SendMsgError = 4
    LoginError = 5
    GetUuidError = 6
    SyncError = 7
    SyncCheckError = 8
    SyncHostCheckError = 9
    BotInitError = 10
    SnapshotExpired = 11

Translations = {
    BotErrorCode.MissingParameter: "The parameters is missing.",
    BotErrorCode.UnknownCommand: "The command is not expected.",
    BotErrorCode.ReservedCommand: "The command is reserved.",
    BotErrorCode.DuplicatedCommand: "The command was already registered.",
    BotErrorCode.SendMsgError: "The message send fails.",
    BotErrorCode.LoginError: "Login error",
    BotErrorCode.GetUuidError: "Get UUID error.",
    BotErrorCode.SyncCheckError: "Sync check fails",
    BotErrorCode.SnapshotExpired: "Session is out expired, need relogin.",
}

class BotException(Exception):
    def __init__(self, errCode, errMsg = None):
        self.err_code = errCode
        self.err_msg = errMsg

    def __str__(self):
        return repr(self.err_msg if self.err_msg else Translations[self.err_code])

class BotUserException(BotException):
    pass

class BotSystemException(BotException):
    pass

class BotServerException(BotException):
    pass

