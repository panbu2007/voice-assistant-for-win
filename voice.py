import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import threading
import time
import pyaudio


STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识


class Voice(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, channels=1, rate=16000):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        #self.Text = "这是一个语音合成示例"
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = channels
        self.RATE = rate

        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"aue": "raw", "auf": "audio/L16;rate=16000", "vcn": "xiaoyan", "tte": "utf8"}
        #使用小语种须使用以下方式，此处的unicode指的是 utf16小端的编码方式，即"UTF-16LE"”
        self.Data = {"status": 2, "text": str(base64.b64encode(''.encode('utf-8')), "UTF8")}
        #self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-16')), "UTF8")}
        websocket.enableTrace(False)
        return

    def get_text(self, text):
        self.Data = {"status": 2, "text": str(base64.b64encode(text.encode('utf-8')), "UTF8")}
        self.run_voice()
        return

    def connect(self):
        wsUrl = self.create_url()
        self.ws = websocket.WebSocketApp(wsUrl, on_open=self.on_open, on_message=self.on_message, on_error=on_error, on_close=on_close)
        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    def run_voice(self):
        t = threading.Thread(target=self.connect)
        t.setDaemon(True)
        t.start()

    # 生成url
    def create_url(self):
        url = 'wss://tts-api.xfyun.cn/v2/tts'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        # print("date: ",date)
        # print("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # print('websocket url :', url)
        return url
   
    def play(self, frame):
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(2), channels=1, rate=16000, output=True)

        # 将 pcm 数据直接写入 PyAudio 的数据流
        stream.write(frame)
        stream.start_stream()
        stream.stop_stream()
        stream.close()
        p.terminate()
        return

    def on_message(self, message):
        try:
            message = json.loads(message)
            code = message["code"]
            sid = message["sid"]
            audio = message["data"]["audio"]
            audio = base64.b64decode(audio)
            status = message["data"]["status"]
            if status == 2:
                print("ws is closed")
                self.ws.close()
            if code != 0:
                errMsg = message["message"]
                print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
            else:
                self.play(audio)

        except Exception as e:
            print("receive msg,but parse exception:", e)

    # 收到websocket连接建立的处理
    def on_open(self):
        def run(*args):
            d = {"common": self.CommonArgs,
                 "business": self.BusinessArgs,
                 "data": self.Data,
                 }
            d = json.dumps(d)
            print("------>开始发送文本数据")
            self.ws.send(d)

        t = threading.Thread(target=run)
        t.setDaemon(True)
        t.start()

# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws):
    print("### closed ###")