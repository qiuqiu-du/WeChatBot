# WeClone

使用微信聊天记录微调大语言模型，我使用了大概2万条整合后的有效数据，最后结果只能说差强人意，但有时候真的很搞笑。

> [!IMPORTANT]
>
> ### 最终效果很大程度取决于聊天数据的数量和质量

### 硬件要求

目前项目默认使用chatglm3-6b模型，LoRA方法对sft阶段微调，大约需要16GB显存。也可以使用[LLaMA Factory](https://github.com/hiyouga/LLaMA-Factory/blob/main/README_zh.md#%E6%A8%A1%E5%9E%8B)支持的其他模型和方法，占用显存更少，需要自行修改模板的system提示词等相关配置。

需要显存的估算值：
| 训练方法 | 精度 |   7B  |  13B  |  30B  |   65B  |   8x7B |
| ------- | ---- | ----- | ----- | ----- | ------ | ------ |
| 全参数   |  16  | 160GB | 320GB | 600GB | 1200GB |  900GB |
| 部分参数 |  16  |  20GB |  40GB | 120GB |  240GB |  200GB |
| LoRA    |  16  |  **16GB** |  32GB |  80GB |  160GB |  120GB |
| QLoRA   |   8  |  10GB |  16GB |  40GB |   80GB |   80GB |
| QLoRA   |   4  |   6GB |  12GB |  24GB |   48GB |   32GB |

### 软件要求

| 必需项       | 至少     | 推荐      |
| ------------ | ------- | --------- |
| python       | 3.8     | 3.10      |
| torch        | 1.13.1  | 2.2.1     |
| transformers | 4.37.2  | 4.38.1    |
| datasets     | 2.14.3  | 2.17.1    |
| accelerate   | 0.27.2  | 0.27.2    |
| peft         | 0.9.0   | 0.9.0     |
| trl          | 0.7.11  | 0.7.11    |

| 可选项       | 至少     | 推荐      |
| ------------ | ------- | --------- |
| CUDA         | 11.6    | 12.2      |
| deepspeed    | 0.10.0  | 0.13.4    |
| bitsandbytes | 0.39.0  | 0.41.3    |
| flash-attn   | 2.3.0   | 2.5.5     |

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
$env:PYTHONPATH = "F:\my_project\WeClone-master"
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

默认在终端显示二维码，扫码登录即可。可以私聊或者在群聊中@机器人使用。

### 截图

![alt text](img/4.jpg)
![alt text](img/1.png)
![alt text](img/2.png)
![alt text](img/3.png)

### 使用RAG补充知识

Todo

### 多模态

Todo
