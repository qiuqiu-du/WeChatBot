from llmtuner.data.formatter import FunctionFormatter, StringFormatter
from llmtuner.data.template import _register_template

# 训练用
default_prompt = "你是一个人类，不要说自己是机器人，自然地和我在微信上对话(符合人们回复微信的习惯，不发大段的文字，简短直接，语句停顿只用逗号)"


def template_register():
    _register_template(
        name="chatglm3-weclone",
        default_system=(
            default_prompt
        ),
        format_user=StringFormatter(slots=[{"token": "<|user|>"}, "\n", "{{content}}", {"token": "<|assistant|>"}]),
        format_assistant=StringFormatter(slots=["\n", "{{content}}"]),
        format_system=StringFormatter(slots=[{"token": "[gMASK]"}, {"token": "sop"}, {"token": "<|system|>"}, "\n", "{{content}}"]),
        format_function=FunctionFormatter(slots=["{{name}}\n{{arguments}}"]),
        format_observation=StringFormatter(slots=[{"token": "<|observation|>"}, "\n", "{{content}}"]),
        stop_words=["<|user|>", "<|observation|>"],
        efficient_eos=True,
        force_system=True
    )
