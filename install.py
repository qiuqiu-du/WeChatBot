from transformers import AutoModel, AutoTokenizer

model_name = "THUDM/chatglm-6b"

# 需要加载自定义的模型类
model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained(model_name)

input_text = "你好，ChatGLM-6B！"
inputs = tokenizer(input_text, return_tensors="pt")
outputs = model.generate(**inputs)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
