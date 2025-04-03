# WeChatBot - 基于个人聊天记录的智能微信机器人

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Model](https://img.shields.io/badge/model-ChatGLM3-ff69b4)

本项目以[WeClone](https://github.com/xming521/WeClone)为基础，是一个基于ChatGLM3模型的智能微信机器人，能够使用您的个人微信聊天记录进行微调，并通过Gewechat接入微信实现自动回复功能。支持本地模型和第三方API两种接入方式。

## ✨ 核心功能

- **个性化回复**：使用您的真实微信聊天记录微调模型
- **双模式支持**：本地模型和第三方API自由切换
- **隐私保护**：自动过滤敏感信息（手机号、身份证等）
- **多场景适配**：支持私聊、群聊等多种聊天场景
- **灵活部署**：提供单卡/多卡训练方案

## 🚀 快速开始

### 环境配置

```bash
git clone https://github.com/qiuqiu-du/WeChatBot.git
conda create -n wechatbot python=3.10
conda activate wechatbot
cd WeChatBot
pip install -r requirements.txt
```

### 数据准备

1. 使用[PyWxDump](https://github.com/xaoyaoo/PyWxDump)导出微信聊天记录
2. 将导出的CSV文件放入`./data/csv`目录，参考格式如下：

```plaintext
data/
└── csv/
    ├── wxid_1/               # 微信ID1的聊天记录
    │   ├── 聊天记录1.csv      # 与某个联系人或群的聊天记录
    │   ├── 聊天记录2.csv
    │   └── ...
    ├── wxid_2/               # 微信ID2的聊天记录
    │   ├── 群聊A.csv
    │   ├── 私聊B.csv
    │   └── ...
    └── ...                   # 其他微信账号数据
```


3. 运行预处理脚本：

```bash
python make_dataset/csv_to_json.py
```

> 💡 示例数据见：[data/example_chat.csv](data/example_chat.csv)

## 🛠 模型训练

### 模型下载

```bash
# 通过Hugging Face下载
git lfs install
git clone https://huggingface.co/THUDM/chatglm3-6b

# 或使用魔搭社区（国内推荐）
export USE_MODELSCOPE_HUB=1
git clone https://www.modelscope.cn/ZhipuAI/chatglm3-6b.git
```

### 训练配置

根据电脑性能和具体需求修改[settings.json](settings.json)配置：

```json
{
  "model_name": "chatglm3-6b",
  "per_device_train_batch_size": 4,
  "gradient_accumulation_steps": 8,
  "num_train_epochs": 3,
  "lora_rank": 8,
  "lora_dropout": 0.1
}
```

### 开始训练

```bash
# 单卡训练
python src/train_sft.py

# 多卡训练（需安装deepspeed）
deepspeed --num_gpus=2 src/train_sft.py
```

> ❕ 也可以先对pt阶段进行微调，仓库也提供了pt阶段数据集预处理和训练的代码。

## 🤖 微信机器人部署

> ⚠️ 重要提示：机器人有封号风险，建议使用微信小号。绑定银行卡后后才能使用

### 本地模型模式

```bash
# 启动API服务
python src/api_service.py

# 启动微信机器人
python src/wechat_bot/demo.py
```

### 第三方API模式

```bash
# 修改config.py中的API配置后直接运行
python src/wechat_bot/demo.py
```

## 🌐 其他功能

### Web演示界面

```bash
python src/web_demo.py
```

### API测试

```bash
# 启动API服务
python src/api_service.py

# 运行测试脚本
python src/test_model.py
```

## 📚 进阶指南

- **数据处理**：支持三种对话处理模式（见`make_dataset/`目录）
- **模型微调**：提供PT和SFT两阶段训练代码
- **安全过滤**：可自定义敏感词库（`make_dataset/blocked_words.json`）

## 📜 声明

使用微信机器人功能请注意遵守微信用户协议,本项目仅用于学习科研用途。

## 💬 问题反馈

如有任何问题，请提交Issue或联系作者邮箱：[qiuqiudu@protonmail.com](mailto:qiuqiudu@protonmail.com)