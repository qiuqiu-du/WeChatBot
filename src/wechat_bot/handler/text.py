import logging
import openai
from src.utils.saver import save_chat_history
import time
from src.config.settings import WeChatConfig


log = logging.getLogger('text')
config = WeChatConfig.from_json()
openai.api_key = config.api_key
openai.api_base = config.api_base

def handler_text(msg , history: [], config):
    """处理文本消息并调用 OpenAI"""
    user = msg.user
    sendTime = msg.CreateTime
    content = msg.text
    messages = [{"role": "system", "content": f'{config.default_prompt}'}]
    for item in history:
        messages.append(item)
    messages.append({"role": "user", "content": content})
    history.append({"role": "user", "content": content})
    save_chat_history(user = user, time= sendTime, role="user", content= content)

    try:
        response = openai.ChatCompletion.create(
            model=config.model,
            messages=messages,
            max_tokens=config.max_tokens,
            temperature = 0.7, # 让 AI 回答更灵活
            frequency_penalty = 0.4,
            presence_penalty = 0.6  # 让 AI 更倾向于新话题
        )
    except openai.APIError as e:
        log.error(f"[openai] Error:{e}")
        history.pop()
        return 'AI接口出错,请重试\n' + str(e)

    resp = str(response.choices[0].message.content)
    resp = resp.replace('\n ', '')
    history.append({"role": "assistant", "content": resp})
    save_chat_history(user = user,time= time.time(), role="assistant", content= resp)
    return resp
