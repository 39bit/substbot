import json, urllib.error, urllib.parse, urllib.request, socket
SENT = False
class TelegramBot():
    class attribute_dict():
        def __init__(self, data):
            self.__data__ = data
        def __getattr__(self, index):
            if index == "__data__": return object.__getattr__(self, "__data__")
            try:
                return self.__getitem__(index)
            except KeyError:
                raise AttributeError
        def __getitem__(self, index):
            return self.__data__[index]
        def __setattr__(self, index, value):
            if index == "__data__": return object.__setattr__(self, "__data__", value)
            self.__setitem__(index)
        def __setitem__(self, index, value):
            self.__data__[index] = value
        def __delattr__(self, index, value):
            if index == "__data__": return object.__delattr__(self, "__data__", value)
            self.__delitem__(index)
        def __delitem__(self, index, value):
            del self.__data__[index]
        def __repr__(self):
            return repr(self.__data__)
        def __iter__(self):
            return iter(self.__data__)
        def __len__(self):
            return len(self.__data__)
        def keys(self):
            return self.__data__.keys()
        def has(self, key):
            return key in self.__data__.keys() and self.__data__[key] != None
    def __init__(self, token):
        self.token = token
        self.retry = 0
    def __getattr__(self, attr):
        return self.func_wrapper(attr)
    def func_wrapper(self, fname):
        def func(self, unsafe, **kw):
            url_par={}
            for key in kw.keys():
                if kw[key] != None:
                    url_par[key] = urllib.parse.quote_plus(TelegramBot.escape(kw[key]))
            url = ("https://api.telegram.org/bot" + self.token + "/" + (fname.replace("__UNSAFE","") if fname.endswith("__UNSAFE") else fname) + "?" +
                    "&".join(map(lambda x:x+"="+url_par[x],url_par.keys())))
            RETRY = True
            while RETRY:
                try:
                    with urllib.request.urlopen(url, timeout=10) as f:
                        raw = f.read().decode('utf-8')
                    RETRY = False
                except socket.timeout:
                    raise ValueError("timeout")
                except BaseException as e:
                    print(str(e))
                    time.sleep(0.5)
                    if "too many requests" in str(e).lower():
                        self.retry += 1
                        time.sleep(self.retry * 5)
                    elif "unreachable" in str(e).lower() or "bad gateway" in str(e).lower() or "name or service not known" in str(e).lower() or  "network" in str(e).lower() or "handshake operation timed out" in str(e).lower():
                        time.sleep(3)
                    elif "bad request" in str(e).lower() and not unsafe:
                        print(fname)
                        print(json.dumps(url_par))
                        traceback.print_exc()
                        return
                    elif "forbidden" in str(e).lower() and not unsafe:
                        print(fname)
                        print(json.dumps(url_par))
                        traceback.print_exc()
                        return
                    else:
                        raise e
            self.retry = 0
            return TelegramBot.attributify(json.loads(raw))
        return lambda **kw:func(self,fname.endswith("__UNSAFE"),**kw)
    @staticmethod
    def escape(obj):
        if type(obj) == str:
            return obj
        else:
            return json.dumps(obj).encode('utf-8')
    @staticmethod
    def attributify(obj):
        if type(obj)==list:
            return list(map(TelegramBot.attributify,obj))
        elif type(obj)==dict:
            d = obj
            for k in d.keys():
                d[k] = TelegramBot.attributify(d[k])
            return TelegramBot.attribute_dict(d)
        else:
            return obj

bot = TelegramBot("BOT_TOKEN_GOES_HERE")

import time, pickle, os.path, traceback, random, threading
ME = bot.getMe().result
ID = ME.id
UN = ME.username

def html_escape(x):
    return x.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
import os, sys, re
tried_to = 0
saferes = True
OFF = 0
Restart = False

try:
    # automatic restart system
    def autoreset():
        time.sleep(600)
        while not saferes:
            time.sleep(0.5)
            tried_to = 10000
        time.sleep(30)
        os.execl(sys.executable, sys.executable, *sys.argv)      
    if Restart:
        threading.Thread(target=autoreset, daemon=True).start()
    while True:
        tried_to += 1
        if tried_to >= 1000 and Restart:
            os.execl(sys.executable, sys.executable, *sys.argv)
        print("poll " + str(time.time()))
        saferes = False
        try:
            updates = bot.getUpdates__UNSAFE(offset=OFF, timeout=10).result
        except KeyboardInterrupt as e:
            raise e
        except BaseException as e:
            print("poll failed: ", e)
            continue            
        for update in updates:
            now = time.time()
            OFF = update.update_id + 1
            if update.has("message"):
                if update.message.has("text") and update.message.has("reply_to_message"):
                    rm = update.message.reply_to_message
                    umt = update.message.text
                    chat_id = update.message.chat.id
                    I = ""
                    if umt[0:3].lower() != "/s/" and umt[0:2].lower() != "s/":
                        continue
                    splitmsg = []
                    ptr = 0
                    bs = False
                    counter = 0
                    informative = chat_id == update.message["from"].id
                    for p in range(len(umt)):
                        if bs:
                            bs = False
                            continue
                        c = umt[p]
                        if c == "\\":
                            bs = True
                        elif c == "/":
                            counter += 1
                        elif c == ";":
                            splitmsg.append(umt[ptr:p])
                            ptr = p + 1
                        elif c == "\n" and (counter < 1 or counter > 2):
                            splitmsg.append(umt[ptr:p])
                            ptr = p + 1
                    splitmsg.append(umt[ptr:])
                    stext = ""
                    if rm.has("text"):
                        stext = rm.text
                    elif rm.has("caption"):
                        stext = rm.caption
                    elif rm.has("pinned_message"):
                        rm = rm.pinned_message
                        if rm.has("text"):
                            stext = rm.text
                        elif rm.has("caption"):
                            stext = rm.caption
                        else:
                            continue
                    else:
                        continue
                    dtext = stext
                    errored = False
                    for umt in splitmsg:
                        if errored:
                            break
                        I = ""
                        if umt[0:3].lower() == "/s/":
                            I = umt[3:]
                        elif umt[0:2].lower() == "s/":
                            I = umt[2:]
                        if len(I) < 1:
                            continue
                        bs = False
                        ls = ""
                        tok = []
                        for c in I:
                            if bs:
                                ls += "\\" + c
                                bs = False
                            elif c == "\\": bs = True
                            elif c == "/":
                                tok.append(ls)
                                ls = ""
                            else: ls += c
                        tok.append(ls)
                        if len(tok) < 1 or len(tok) > 3:
                            bot.sendMessage(chat_id=chat_id,
                                            text="Malformed pattern" if not informative else "Malformed pattern\n(too many / split tokens)",
                                            reply_to_message_id=update.message.message_id)
                            errored = True
                            continue
                        flags = 0
                        if len(tok) > 2:
                            tok[-1] = tok[-1].lower()
                            if "a" in tok[-1]:flags|=re.A 
                            if "i" in tok[-1]:flags|=re.I 
                            if "l" in tok[-1]:flags|=re.L 
                            if "m" in tok[-1]:flags|=re.M 
                            if "s" in tok[-1]:flags|=re.S 
                            if "x" in tok[-1]:flags|=re.X
                        try:
                            tu = ""
                            bs = False
                            for c in tok[1]:
                                if bs:
                                    if c == "n": tu += "\\n"
                                    elif c == "r": tu += "\\r"
                                    elif c == "t": tu += "\\t"
                                    elif c == "/": tu += "/"
                                    elif c == ";": tu += ";"
                                    elif c == "0": tu += "\\g<0>"
                                    elif c == "\\": tu += "\\\\"
                                    else: tu += "\\" + c
                                    bs = False
                                else:
                                    if c == "\\": bs = True
                                    else: tu += c 
                            if bs: tu += "\\\\"
                            
                            # this is what causes the fun error message in private messages when illegal regex is encountered
                            RaisePointlessError = re.sub
                            GenerateRandomErrorMessage = lambda:tok[0]
                            ERR_CRITICAL = tu
                            TRACEBACK_FULL = dtext
                            NULL = flags
                            YOU_DONE_SCREWED_UP, Please_Break_Now_Program = RaisePointlessError(GenerateRandomErrorMessage(), ERR_CRITICAL, TRACEBACK_FULL, 0, NULL), "lrn2sed"
                            dtext = YOU_DONE_SCREWED_UP[:4096]
                        except BaseException as e:
                            traceback.print_exc()
                            errored = True
                            bot.sendMessage(chat_id=chat_id,
                                            text="Malformed pattern" if not informative else ("Malformed pattern\n==================\n" + traceback.format_exc())[:4096],
                                            reply_to_message_id=update.message.message_id)
                    if not errored:
                        if len(dtext) < 1:
                            bot.sendMessage(chat_id=chat_id,
                                        text="_(empty message)_",
                                        parse_mode="Markdown",
                                        reply_to_message_id=rm.message_id)
                        else:
                            bot.sendMessage(chat_id=chat_id,
                                        text=dtext,
                                        reply_to_message_id=rm.message_id)
        saferes = True
        time.sleep(0.1)
except KeyboardInterrupt as e:
    pass
except BaseException as e:
    traceback.print_exc()
