import os
import time
import logging
import web
import threading
import json


from src.wechat_bot.handler.MessageHandler import MessageHandler
from urllib.parse import urlparse
from gewechat_client import GewechatClient
from src.config.settings import WeChatConfig

# 配置日志输出
logging.basicConfig(
    level=logging.INFO,  # 设置最低日志级别
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # 日志格式
    datefmt="%Y-%m-%d %H:%M:%S",  # 时间格式
    filename="app.log",  # ✅ 日志自动保存到 app.log
    filemode="a"  # 追加模式（'w' 会清空旧日志）
)
log = logging.getLogger('demo')

messagehandler = MessageHandler()

class WeChatGPT:
    """启动机器人并执行登陆程序"""
    def __init__(self, config:WeChatConfig=WeChatConfig.from_json()):
        self.config = config
        app_id= self.config.app_id
        base_url=self.config.base_url
        token=self.config.token
        callback_url=self.config.callback_url

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
        urls = (path, f"{__name__}.Query")  # 确保 `CallbackHandler` 存在
        app = web.application(urls, globals(), autoreload=False)
        print("\033[33m服务已启动\033[0m")
        # **启动 Web 服务器**
        web.httpserver.runsimple(app.wsgifunc(), ("0.0.0.0", port))



class Query:
    def __init__(self, config:WeChatConfig=WeChatConfig):
        self.config = config
        self.app_id= self.config.app_id
        self.base_url=self.config.base_url
        self.token=self.config.token

        # 创建 GewechatClient 实例
        self.client = GewechatClient(self.base_url, self.token)

    def POST(self):
        """处理 POST 请求，筛选并打印符合条件的消息内容"""
        try:
            data = web.data()  # 获取请求体数据
            parsed_data = json.loads(data)  # 解析 JSON 数据

            # print('收到消息：\n',json.dumps(parsed_data, indent=4, ensure_ascii=False))

            # 提取关键字段
            wxid = parsed_data.get("Wxid", "")
            data_section = parsed_data.get("Data", {})

            from_user = data_section.get("FromUserName", {}).get("string", "")
            to_user = data_section.get("ToUserName", {}).get("string", "")
            msg_type = data_section.get("MsgType", 0)
            text = data_section.get("Content", {}).get("string", "")
            create_time = data_section.get("CreateTime", "")
            msg_id = data_section.get("NewMsgId", "")

            # 封装 msg 对象
            msg = {
                "text": text,
                "CreateTime": create_time,
                "user": from_user,
                "wxid_in_chatroom" : None,
                "nick_name" : None
            }
            msg = type('Config', (object,), msg)()

            # print(f"wxid:{wxid}, from_user:{from_user}, to_user{to_user}, msg_type:{msg_type}, content:{msg}")
            # 接收到联系人的文本消息自动回复
            if to_user == wxid and msg_type == 1 and '@chatroom' not in msg.user:
                print(f"[Message] ({msg.user}) {msg.text}")
                messagehandler.reply(msg)

            # 接收到群聊的文本消息自动回复
            elif to_user == wxid and msg_type == 1 and '@chatroom' in msg.user:
                my_nickname = self.client.get_profile(self.app_id).get("data",{}).get("nickName","")
                if f'@{my_nickname}' in msg.text:
                    # 分割消息，保存wxid和实际内容
                    msg.wxid_in_chatroom, msg.text = msg.text.split(':\n', 1)
                    # 去除@字段
                    msg.text = msg.text.replace(f'@{my_nickname}', "").strip()
                    member_detail = self.client.get_chatroom_member_detail(app_id = self.app_id,chatroom_id = msg.user,member_wxids = [msg.wxid_in_chatroom])
                    # member_detail2 = self.client.get_brief_info(app_id = self.app_id, wxids=[msg.wxid_in_chatroom])
                    msg.nick_name = member_detail.get("data", [])[0].get("nickName","")
                    # nick_name2 = member_detail2.get("data", [])[0].get("nickName","")

                    # msg.user 为群聊名称：52180927825@chatroom
                    # msg.id_in_chatroom 为发言人名称：wxid_4mw40s2inlib22
                    print(f"[Message] ({msg.user}: {msg.wxid_in_chatroom}) {msg.text}")
                    messagehandler.reply(msg)



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




def logout(config:WeChatConfig=WeChatConfig):

    app_id = config.app_id
    base_url = config.base_url
    token = config.token

    client = GewechatClient(base_url, token)

    online_state = client.check_online(app_id).get("data", False)
    if not online_state:
        client.logout(app_id)
        print('已退出登录')

if __name__ == "__main__":
    logout()
    wechatgpt = WeChatGPT()

