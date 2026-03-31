# Document Translator - 文档翻译工具

一款简洁高效的Windows桌面应用程序，用于将Word文档(.docx)和Excel文件(.xlsx)进行全文翻译。

## 功能特点

- 支持 Word 文档(.docx)和 Excel 文件(.xlsx)全文翻译
- 支持4种翻译引擎：
  - **Google Translate** (免费，无需配置)
  - **Google Translate API** (需要API密钥)
  - **DeepL API** (需要API密钥)
  - **百度翻译 API** (需要App ID和API密钥)
- 支持20+种语言互译
- 批量文件处理
- 保留原文档格式

## 快速开始

### 方法一：下载预编译版本

从 [Releases](https://github.com/your-repo/DocumentTranslator/releases) 页面下载 `DocumentTranslator.exe`

### 方法二：从源码构建

#### 构建步骤

1. **下载源码**
   ```
   下载或克隆本仓库到本地
   ```

2. **安装Python**
   - 访问 https://www.python.org/downloads/
   - 下载并安装 Python 3.8 或更高版本
   - **重要**：安装时勾选 "Add Python to PATH"

3. **构建可执行文件**

   双击运行 `build.bat`

   或者在命令行中执行：
   ```cmd
   build.bat
   ```

4. **获取exe文件**
   构建完成后，在 `dist` 文件夹中找到 `DocumentTranslator.exe`

### 方法三：GitHub Actions自动构建

1. Fork 本仓库
2. 进入 Actions 页面
3. 点击 "Build Windows Executable" workflow
4. 点击 "Run workflow"
5. 等待构建完成后，在 Artifacts 中下载 exe

## 使用说明

### 基本翻译流程

1. **启动程序**：双击 `DocumentTranslator.exe`
2. **添加文件**：点击"添加文件"按钮，选择要翻译的文档
3. **选择语言**：
   - 源语言：选择原文语言（或选择"自动检测"）
   - 目标语言：选择要翻译成的语言
4. **开始翻译**：点击"开始翻译"按钮
5. **获取结果**：翻译完成后，在输出目录中找到翻译后的文件

### 配置翻译API（可选）

#### Google Translate API

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建项目并启用 Cloud Translation API
3. 创建API密钥
4. 在程序中点击"配置API密钥"
5. 粘贴API密钥并保存

#### DeepL API

1. 访问 [DeepL API](https://www.deepl.com/pro-api)
2. 注册并订阅API服务
3. 复制API密钥
4. 在程序中点击"配置API密钥"
5. 粘贴API密钥并保存

#### 百度翻译 API

1. 访问 [百度翻译开放平台](https://fanyi-api.baidu.com/)
2. 注册开发者账号
3. 创建应用获取 App ID 和 API Key
4. 在程序中点击"配置API密钥"
5. 填写 App ID 和 API Key 并保存

## 项目结构

```
translation_app/
├── main.py                 # 入口文件
├── requirements.txt        # Python依赖
├── build.bat              # 一键构建脚本
├── translation_app/
│   ├── __init__.py
│   ├── config.py          # 配置管理
│   ├── translator.py      # 翻译引擎
│   ├── word_processor.py  # Word文档处理
│   ├── excel_processor.py # Excel文件处理
│   └── ui.py              # 用户界面
└── docs/
    └── 使用说明.md        # 使用文档
```

## 技术栈

- Python 3.8+
- Tkinter (GUI)
- python-docx (Word处理)
- openpyxl (Excel处理)
- requests (HTTP请求)
- deep-translator (翻译接口)
- PyInstaller (打包)

## 许可证

MIT License

## 问题反馈

如有问题或建议，请提交 Issue。
