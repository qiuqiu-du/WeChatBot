import json
import os
from .time_converter import stamp_to_utc

def save_chat_history(user, time, role, content, base_dir="chat_logs"):
    """保存聊天记录，每个用户单独一个 JSON 文件，并增加 role 字段"""
    os.makedirs(base_dir, exist_ok=True)  # 确保目录存在
    file_path = os.path.join(base_dir, f"{user}.json")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            chat_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        chat_data = []  # 如果文件不存在，创建空列表

    chat_data.append({"time": stamp_to_utc(time), "role": role, "content": content})  # 追加新记录

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(chat_data, f, ensure_ascii=False, indent=4)  # 保存到 JSON 文件

if __name__ == "__main__":
    print(stamp_to_utc(1741911064))