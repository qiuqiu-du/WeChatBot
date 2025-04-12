import os
from dataclasses import dataclass
import json
import sys

@dataclass
class WeChatConfig:
    base_url: str = os.getenv("BASE_URL", "http://127.0.0.1:2531/v2/api")
    token: str = os.getenv("GEWECHAT_TOKE", "00c8891659874d859aacf21a4785abcc")
    app_id: str = os.getenv("APP_ID", "wx_WD2Sqy6ZoFSXHsiD7fOto")
    callback_url: str = os.getenv("CALL_BACK", "http://192.168.20.41:9919/v2/api/callback/collect")

    model: str = "deepseek-chat"
    api_key: str = "sk-7c60055a0c96485f8314bdd290e8ebd9"
    api_base: str = "https://api.deepseek.com"
    # openai.api_key = '''sk-test'''
    # openai.api_base = "http://127.0.0.1:8000/v1"
    max_tokens: int = 70
    history_len: int = 30
    reply_with_at: bool = True
    reply_in_a_sentence: bool = True

    default_prompt: str = "你是一个人类，不要说自己是机器人，自然地和我在微信上对话(符合人们回复微信的习惯，不发大段的文字，简短直接，语句停顿只用逗号)"


    @classmethod
    def from_json(cls, path: str = "config.json"):
        # 获取可执行文件所在目录
        if getattr(sys, 'frozen', False):
            # 打包后的情况（如PyInstaller）
            exe_dir = os.path.dirname(sys.executable)
        else:
            # 源码运行的情况
            exe_dir = os.path.dirname(__file__)

        # 构建完整路径
        full_path = os.path.join(exe_dir, path)

        with open(full_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)