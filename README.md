# WeChatBot

本项目是基于WeClone开发的聊天机器人，使用自己的聊天记录对模型微调，并使用Gewechat接入微信

### 环境搭建

```bash
git clone https://github.com/xming521/WeClone.git
conda create -n weclone python=3.10
conda activate weclone
cd WeClone
pip install -r requirements.txt
```

训练以及推理相关配置统一在文件[settings.json](settings.json)

### 数据准备

请使用[PyWxDump](https://github.com/xaoyaoo/PyWxDump)提取微信聊天记录。下载软件并解密数据库后，点击聊天备份，导出类型为CSV，可以导出多个联系人或群聊，然后将导出的位于`wxdump_tmp/export` 的 `csv` 文件夹放在`./data`目录即可，也就是不同人聊天记录的文件夹一起放在 `./data/csv`。 示例数据位于[data/example_chat.csv](data/example_chat.csv)。

### 数据预处理

项目默认去除了数据中的手机号、身份证号、邮箱、网址。还提供了一个禁用词词库[blocked_words](make_dataset/blocked_words.json)，可以自行添加需要过滤的词句（会默认去掉包括禁用词的整句）。
执行 `./make_dataset/csv_to_json.py` 脚本对数据进行处理。

在同一人连续回答多句的情况下，有三种处理方式：
| 文件 | 处理方式 |
| --- | --- |
| csv_to_json.py | 用逗号连接 |
| csv_to_json-单句回答.py(已废弃) | 只选择最长的回答作为最终数据 |
| csv_to_json-单句多轮.py | 放在了提示词的'history'中 |


### 模型下载

首选在Hugging Face下载[ChatGLM3](https://huggingface.co/THUDM/chatglm3-6b) 模型。如果您在 Hugging Face 模型的下载中遇到了问题，可以通过下述方法使用魔搭社区，后续训练推理都需要先执行`export USE_MODELSCOPE_HUB=1`来使用魔搭社区的模型。  
由于模型较大，下载过程比较漫长请耐心等待。

```bash
set USE_MODELSCOPE_HUB=1 # Windows 使用 `set USE_MODELSCOPE_HUB=1`
git lfs install
git clone https://www.modelscope.cn/ZhipuAI/chatglm3-6b.git
```

### 配置参数并微调模型

- (可选)修改 [settings.json](settings.json)选择本地下载好的其他模型。  

- 修改`per_device_train_batch_size`以及`gradient_accumulation_steps`来调整显存占用。  
- 可以根据自己数据集的数量和质量修改`num_train_epochs`、`lora_rank`、`lora_dropout`等参数。

#### 单卡训练

运行 `src/train_sft.py` 进行sft阶段微调，本人loss只降到了3.5左右，降低过多可能会过拟合。

```bash
python src/train_sft.py
```

#### 多卡训练

```bash
pip install deepspeed
deepspeed --num_gpus=使用显卡数量 src/train_sft.py
```

> [!NOTE]
> 也可以先对pt阶段进行微调，似乎提升效果不明显，仓库也提供了pt阶段数据集预处理和训练的代码。

### 使用浏览器demo简单推理

```bash
python ./src/web_demo.py 
```

### 使用接口进行推理

```bash
python ./src/api_service.py
```
### 启用gewechat

```bash
python ./src/wechat_bot/demo.py
```


### 使用常见聊天问题测试

```bash
python ./src/api_service.py
python ./src/test_model.py
```

### 部署微信聊天机器人

> [!IMPORTANT]
>
> 微信有封号风险，建议使用小号，并且必须绑定银行卡才能使用

```bash
python ./src/api_service.py # 先启动api服务
python ./src/wechat_bot/main.py 
```


