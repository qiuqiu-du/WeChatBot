from src.config.settings import WeChatConfig
from gewechat_client import GewechatClient
from .text import handler_text
import time




class MessageHandler:
    """执行消息处理"""
    def __init__(self, config:WeChatConfig=WeChatConfig):
        self.config = config
        self.app_id= self.config.app_id
        self.base_url=self.config.base_url
        self.token=self.config.token

        self.client = GewechatClient(self.base_url, self.token)


        self.history = {}
        self.prompts = {}


    def handler_history(self, msg):
        # 管理历史对话长度
        self.history.setdefault(msg.user, [])
        history = self.history[msg.user]
        need_remove_len = len(history) - self.config.history_len
        if need_remove_len > 0:
            for i in range(need_remove_len):
                # 必须出一对
                history.pop(0)
                history.pop(0)
        return history

    def reply(self, msg):

        try:
            if msg.text == "clear":
                self.history[msg.user] = []
                self.client.post_text(self.app_id, msg.user, "记忆已清除")
                print("\033[31m记忆已清除\033[0m")
                return

            if time.time() - msg.CreateTime > 5:
                return None
            res = handler_text(msg, history=self.handler_history(msg), config=self.config)

            # 将回复整理为一行
            res = res.replace('\n', '。')
            print(f"[Reply] ({msg.user}) {res}" if msg.wxid_in_chatroom is None else f"[Reply] ({msg.user}: {msg.wxid_in_chatroom}) {res}")
            res = res.replace('。', '，')
            res = res.split('，')
            if res[0] == '':
                res[0] = '机器人他无语了'

            if msg.wxid_in_chatroom is not None:
                if self.config.reply_with_at:
                    res[0] = f'@{msg.nick_name} {res[0]}'
                    self.client.post_text(self.app_id, to_wxid = msg.user, content = res[0], ats = msg.wxid_in_chatroom)
                    for r in res[1:]:
                        self.client.post_text(self.app_id, msg.user, r)
                        time.sleep(2.2)
                else:
                    for r in res:
                        self.client.post_text(self.app_id, msg.user, r)
                        time.sleep(2.2)
            else:
                for r in res:
                    self.client.post_text(self.app_id, msg.user, r)
                    time.sleep(2.2)
        except Exception as e:
            log.error(f"[Reply] Error: {str(e)}")
            return

    def add_friends(self, data_section):

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
        self.client.add_contacts(self.app_id, scene, 3, v3, v4, "你好呀，我们已经是朋友了")
