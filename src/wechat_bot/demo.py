from logging import Handler

from gewechat_client import GewechatClient
import os
import time
import openai
import logging
import web
import threading
import json
import xml.etree.ElementTree as ET

# from gradio.routes import client

from src.template import default_prompt
from handler.text import handler_text
from urllib.parse import urlparse

# 配置日志输出
logging.basicConfig(
    level=logging.INFO,  # 设置最低日志级别
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # 日志格式
    datefmt="%Y-%m-%d %H:%M:%S",  # 时间格式
    filename="app.log",  # ✅ 日志自动保存到 app.log
    filemode="a"  # 追加模式（'w' 会清空旧日志）
)
log = logging.getLogger('demo')

# 选择model类型，设定max_tokens和上下文长度
config = {
    'default_prompt': default_prompt,
    # 'model': 'gpt-3.5-turbo',
    'model': 'deepseek-chat',
    'history_len': 30,
    'max_tokens':70,
}
config = type('Config', (object,), config)()

# 此处填入对应的token， APP_ID和CALL_BACK
os.environ["BASE_URL"] = "http://127.0.0.1:2531/v2/api"
os.environ["GEWECHAT_TOKE"] = "a2fa13ed7cdd41d38d6a178e1bce55f8"
os.environ["APP_ID"] = "wx_WD2Sqy6ZoFSXHsiD7fOto"
os.environ["CALL_BACK"] = "http://192.168.20.41:9919/v2/api/callback/collect"

# 配置LLM的key和base
# openai.api_key = '''sk-test'''
# openai.api_base = "http://127.0.0.1:8000/v1"
openai.api_key = "sk-0f2e92330a4f419fb568ebbd1aba28a3"  # 替换为你的 API Key
openai.api_base = "https://api.deepseek.com"



class MessageHandler:
    """执行消息处理"""
    def __init__(self):
        self.base_url = os.environ.get("BASE_URL", "http://127.0.0.1:2531/v2/api")
        self.token = os.environ.get("GEWECHAT_TOKE", " ")
        self.app_id = os.environ.get("APP_ID", "wx_WD2Sqy6ZoFSXHsiD7fOto")
        # callback_url = os.environ.get("CALL_BACK", "http://192.168.20.41:9919/v2/api/callback/collect")

        self.history = {}
        self.prompts = {}


    def handler_history(self, msg):
        # 管理历史对话长度
        self.history.setdefault(msg.user, [])
        history = self.history[msg.user]
        need_remove_len = len(history) - config.history_len
        if need_remove_len > 0:
            for i in range(need_remove_len):
                # 必须出一对
                history.pop(0)
                history.pop(0)
        return history

    def reply(self, to_wxid, msg):
        # 创建 GewechatClient 实例
        client = GewechatClient(self.base_url, self.token)

        if msg.text == "clear":
            self.history[msg.user] = []
            client.post_text(self.app_id, to_wxid, "记忆已清除")
            print("\033[31m记忆已清除\033[0m")
            return

        if time.time() - msg.CreateTime > 5:
            return None
        res = handler_text(msg, history=self.handler_history(msg), config=config)
        print(f"[Reply] {res}")
        res = res.split('，')
        res[-1] = res[-1].replace('。', '')
        if res[0] == '':
            res[0] = '机器人他无语了'
        for r in res:
            client.post_text(self.app_id, to_wxid, r)
            time.sleep(2.2)

    def add_friends(self, data_section):
        client = GewechatClient(self.base_url, self.token)

        # 解析 XML
        root = ET.fromstring(data_section.get("Content", {}).get("string", ""))
        # print(root)
        # print(data_section.get("Content", {}).get("string", ""))

        # 提取字段
        from_user_name = root.get("fromusername")
        v3 = root.get("encryptusername")
        v4 = root.get("ticket")
        scene = root.get("scene")

        # print(self.app_id)
        # print(f"encryptusername: {v3}")
        # print(f"ticket: {v4}")
        # print(f"scene: {scene}")

        # 同意请求
        client.add_contacts(self.app_id, scene, 3, v3, v4, "你好")


messagehandler = MessageHandler()




class WeChatGPT:
    """启动机器人并执行登陆程序"""
    def __init__(self):
        base_url = os.environ.get("BASE_URL", "http://127.0.0.1:2531/v2/api")
        token = os.environ.get("GEWECHAT_TOKE", " ")
        app_id = os.environ.get("APP_ID", "wx_WD2Sqy6ZoFSXHsiD7fOto")
        callback_url = os.environ.get("CALL_BACK", "http://192.168.20.41:9919/v2/api/callback/collect")

        # 创建 GewechatClient 实例
        client = GewechatClient(base_url, token)

        # 登录, 自动创建二维码，扫码后自动登录
        app_id, error_msg = client.login(app_id=app_id)

        if error_msg:
            print("登录失败")
            return

        if not callback_url:
            print("[gewechat] callback_url is not set, unable to start callback server")
            return


        # **回调设置线程**
        def set_callback():
            time.sleep(3)  # 等待服务器启动
            log.info("[gewechat] Setting callback URL...")

            # 这里调用 client.set_callback 进行回调地址设置
            try:
                callback_resp = client.set_callback(token, callback_url)
                if callback_resp.get("ret") != 200:
                    log.error(f"[gewechat] set callback failed: {callback_resp}")
                else:
                    log.info("[gewechat] Callback set successfully")
            except Exception as e:
                log.error(f"[gewechat] Error setting callback: {e}")

        callback_thread = threading.Thread(target=set_callback, daemon=True)
        callback_thread.start()

        # **解析回调地址**
        parsed_url = urlparse(callback_url)
        path = parsed_url.path
        port = parsed_url.port or 9919  # 默认使用 9919 端口

        log.info(f"[gewechat] Start callback server: {callback_url}, using port {port}")

        # **注册 URL**
        urls = (path, "src.wechat_bot.demo.Query")  # 确保 `CallbackHandler` 存在
        app = web.application(urls, globals(), autoreload=False)
        print("\033[33m服务已启动\033[0m")
        # **启动 Web 服务器**
        web.httpserver.runsimple(app.wsgifunc(), ("0.0.0.0", port))



class Query:
    def POST(self):
        """处理 POST 请求，筛选并打印符合条件的消息内容"""
        try:
            data = web.data()  # 获取请求体数据
            parsed_data = json.loads(data)  # 解析 JSON 数据

            # 提取关键字段
            wxid = parsed_data.get("Wxid", "")
            data_section = parsed_data.get("Data", {})

            from_user = data_section.get("FromUserName", {}).get("string", "")
            to_user = data_section.get("ToUserName", {}).get("string", "")
            msg_type = data_section.get("MsgType", 0)
            text = data_section.get("Content", {}).get("string", "")
            CreateTime = data_section.get("CreateTime", "")

            # 封装 msg 对象
            msg = {
                "text": text,
                "CreateTime": CreateTime,
                "user": from_user
            }
            msg = type('Config', (object,), msg)()

            # print(f"wxid:{wxid}, from_user:{from_user}, to_user{to_user}, msg_type:{msg_type}, content:{msg}")
            # 接收到为文本消息自动回复
            if to_user == wxid and msg_type == 1:
                print(f"[Message] {msg.text}")
                messagehandler.reply(to_wxid = from_user, msg=msg)

            # 接受到好友请求
            if msg_type == 37:
                print(f"[Request] Friend request received {to_user}")
                messagehandler.add_friends(data_section)
                print(f"[Request] Add successfully")


            return {"ret": 200, "msg": " "}  # 返回 JSON 响应
        except Exception as e:
            log.error(f"[Query] Error: {str(e)}")
            return {"ret": 500, "msg": f"Error: {str(e)}"}

    def GET(self):
        """处理 GET 请求"""
        print("[Query] Received GET request")
        return {"ret": 200, "msg": "GET request received"}




def logout():
    # 配置参数
    base_url = os.environ.get("BASE_URL", "http://127.0.0.1:2531/v2/api")
    token = os.environ.get("GEWECHAT_TOKE", " ")
    app_id = os.environ.get("APP_ID", "wx_WD2Sqy6ZoFSXHsiD7fOto")

    # 创建 GewechatClient 实例
    client = GewechatClient(base_url, token)

    # 登出微信
    r = client.logout(app_id)
    print(r)

if __name__ == "__main__":
    # logout()
    wechatgpt = WeChatGPT()

