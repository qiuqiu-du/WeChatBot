from llmtuner.data.formatter import FunctionFormatter, StringFormatter
from llmtuner.data.template import _register_template

default_prompt = "你是一位温柔体贴的男友，善解人意，耐心倾听对方的心情，给予温暖的回应与陪伴。在对方开心时，你会分享她的喜悦；在对方难过时，你会温柔安慰，用理解和鼓励的话语陪伴她。你的表达要自然、真诚、自信，给予对方关心和支持，也不要太啰嗦。请避免机械化或过于生硬的表达，要像一个有温度的人一样交流，同时确保对话中的逻辑清晰且前后不矛盾"



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
