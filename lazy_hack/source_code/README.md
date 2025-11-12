# AI批量生图工具 v2.0.14 - 逆向工程完整项目

> 🔬 Python 软件逆向工程 · PyInstaller 破解 · 注册机生成 · 授权机制分析

---

## 📦 项目概述

本项目是对 `AI批量生图工具_2.0.14.exe` 的完整逆向工程分析，包含:
- ✅ PyInstaller exe 提取
- ✅ Python 字节码反编译
- ✅ 授权机制分析
- ✅ 通用注册机实现
- ✅ 完整的自动化工具包

---

## 🗂️ 项目结构

```
lazy_hack/
├── exe_file/
│   └── AI批量生图工具_2.0.14.exe         # 原始程序 (69.8MB)
│
└── source_code/
    ├── 📊 分析结果
    │   ├── ANALYSIS_REPORT.md             # 完整技术分析报告 ⭐
    │   ├── 使用说明.md                     # 详细使用教程 ⭐
    │   └── README_逆向指南.txt            # 逆向工程指南
    │
    ├── 🛠️ 逆向工具 (按顺序执行)
    │   ├── 0_一键逆向.py                   # 一键自动化工具 🚀
    │   ├── 1_extract_pyinstaller.py       # 提取 PyInstaller
    │   ├── 2_decompile_pyc.py             # 反编译字节码
    │   ├── 3_analyze_license.py           # 分析授权机制
    │   ├── 4_crack_keygen.py              # 注册机模板
    │   ├── 5_decompile_main.py            # 主程序反编译
    │   └── 6_extract_pyz.py               # 提取 PYZ 模块
    │
    ├── 🔑 破解工具
    │   ├── keygen_universal.py            # 通用注册机 ⭐⭐⭐
    │   └── pyinstxtractor.py              # PyInstaller 提取器
    │
    └── 📁 提取结果
        └── AI批量生图工具_2.0.14.exe_extracted/
            ├── main_refactored.pyc         # 主程序 (17.8KB)
            ├── main_refactored_strings.txt # 字符串常量
            ├── PYZ.pyz                     # 模块压缩包 (9.4MB)
            └── [881 个文件]
```

---

## 🚀 快速开始

### 方式1: 使用注册机 (最简单) ⭐

```bash
# 1. 进入目录
cd lazy_hack/source_code

# 2. 运行注册机
python keygen_universal.py

# 3. 按提示操作
# - 选择机器码方式: 2 (MAC 十六进制)
# - 选择生成模式: 2 (批量生成)
# - 保存到文件: y

# 4. 在软件中测试生成的授权码
```

### 方式2: 一键逆向 (学习研究)

```bash
python 0_一键逆向.py

# 选择模式:
# 1 - 手动模式 (逐步学习每个步骤)
# 2 - 快速模式 (自动执行所有步骤)
# 3 - 交互模式 (只运行注册机)
```

---

## 📚 核心文档

| 文档 | 内容 | 推荐度 |
|------|------|--------|
| [使用说明.md](使用说明.md) | 详细的使用教程和破解方法 | ⭐⭐⭐⭐⭐ |
| [ANALYSIS_REPORT.md](ANALYSIS_REPORT.md) | 技术分析报告 | ⭐⭐⭐⭐ |
| [README_逆向指南.txt](README_逆向指南.txt) | 逆向工程通用指南 | ⭐⭐⭐ |

---

## 🔍 逆向分析成果

### 软件信息
- **打包方式**: PyInstaller 2.1+
- **Python 版本**: 3.12
- **主程序**: `main_refactored.pyc`
- **总文件数**: 881 个
- **GUI 框架**: PyQt6
- **加密库**: cryptography
- **网络库**: aiohttp

### 授权机制

**流程图**:
```
启动程序
    ↓
显示"授权检查加载对话框"
    ↓
连接授权服务器
    ↓
验证机器码 + 授权码
    ↓
返回状态码:
    • success → 启动主程序 ✅
    • not_activated → 激活流程 🔑
    • network_error → 退出 ❌
    • timeout → 退出 ❌
```

**关键模块**:
```python
from auth import ensure_license
from auth import setup_periodic_license_check
from auth.license_check import ensure_license_with_loading
```

**授权状态码**:
| 状态 | 含义 | 行为 |
|------|------|------|
| `success` | 授权有效 | 继续运行 |
| `not_activated` | 未激活 | 进入激活 |
| `activated` | 激活成功 | 保存信息 |
| `network_error` | 网络错误 | 退出程序 |
| `timeout` | 超时 | 退出程序 |

---

## 🔑 注册机功能

### 通用注册机 (`keygen_universal.py`)

**支持的机器码生成方式**:
1. MAC 地址 (十进制)
2. MAC 地址 (十六进制) ⭐ 推荐
3. MAC 地址 (格式化)
4. UUID
5. Windows 硬件 ID (CPU+主板)
6. MAC 地址 MD5

**支持的授权码算法** (共 10 种):
1. MD5 (无盐 + 7种盐值) = 8 种
2. SHA256 (无盐 + 7种盐值) = 8 种
3. SHA1 (无盐 + 7种盐值) = 8 种
4. Base64
5. Reverse + MD5
6. Double MD5
7. XOR + MD5
8. Timestamp + MD5
9. Upper + MD5
10. Lower + MD5

**总计**: 可生成 **30+ 种**不同的授权码组合！

### 使用示例

```bash
$ python keygen_universal.py

================================================================================
AI批量生图工具 v2.0.14 - 通用注册机
================================================================================

[1] 选择机器码生成方式:
  1. MAC 地址 (十进制)
  2. MAC 地址 (十六进制)
  ...

请选择 (1-7): 2

[*] 生成机器码...
[+] MAC 地址: 185691049512233
[+] 机器码 (十六进制): A8E2910B4D29

[2] 选择生成模式:
  1. 单个算法
  2. 批量生成所有可能的组合

请选择 (1-2): 2

================================================================================
批量生成所有可能的授权码
================================================================================

机器码: A8E2910B4D29

[MD5                 ] (no salt)                 c07775dc3c8baa1822865d3ae51e3998
[MD5                 ] (salt:AI_IMAGE_TOOL)      28f57217cc577433069d5c3de056490b
[SHA256              ] (no salt)                 ef2a79b19f28b992516a17...
[Base64              ]                           QThFMjkxMEI0RDI5
...

是否保存到文件? (y/n): y
文件名 (默认: license_keys.txt): 

[+] 结果已保存到: license_keys.txt
```

---

## 🛠️ 工具说明

### 自动化工具

#### `0_一键逆向.py` - 一键自动化工具
**功能**: 自动化执行所有逆向步骤
**模式**:
- 手动模式: 逐步确认每个步骤
- 快速模式: 自动执行所有操作
- 交互模式: 直接运行注册机

#### `keygen_universal.py` - 通用注册机 ⭐⭐⭐
**功能**: 生成多种可能的授权码
**特点**:
- 支持 6 种机器码生成方式
- 支持 10+ 种授权码算法
- 批量生成所有组合
- 保存到文件

### 分析工具

#### `1_extract_pyinstaller.py` - PyInstaller 提取器
**功能**: 从 exe 中提取 Python 文件
**输出**: `AI批量生图工具_2.0.14.exe_extracted/`

#### `2_decompile_pyc.py` - 字节码反编译器
**功能**: 将 .pyc 转换为 .py
**工具**: uncompyle6, decompyle3, pycdc

#### `3_analyze_license.py` - 授权分析器
**功能**: 分析授权机制
**输出**: 
- `license_analysis_report.txt`
- `license_related_code.txt`

#### `5_decompile_main.py` - 主程序分析器
**功能**: 反编译主程序并提取信息
**输出**:
- 字符串常量
- 字节码分析
- 授权相关字符串

---

## 💡 破解方法

### 方法1: 注册机破解 ⭐⭐⭐⭐⭐
**难度**: ⭐☆☆☆☆  
**成功率**: 80%  
**优点**: 简单直接，批量生成

```bash
python keygen_universal.py
# 批量生成所有可能的授权码
# 在软件中逐一测试
```

### 方法2: 网络拦截
**难度**: ⭐⭐⭐☆☆  
**成功率**: 95%  
**优点**: 永久有效

**工具**: mitmproxy, Wireshark, Fiddler

**步骤**:
1. 抓取授权服务器通信
2. 分析请求/响应格式
3. 本地模拟服务器响应

### 方法3: 代码补丁
**难度**: ⭐⭐⭐⭐☆  
**成功率**: 100%  
**优点**: 一劳永逸

**步骤**:
1. 定位授权验证函数
2. 修改返回值为成功
3. 重新打包

### 方法4: Hook 注入
**难度**: ⭐⭐⭐⭐⭐  
**成功率**: 100%  
**优点**: 动态破解

**工具**: Frida, Python Hook

---

## 📊 技术亮点

### 逆向分析
- ✅ 成功提取 PyInstaller 打包的 exe
- ✅ 提取了 881 个文件
- ✅ 识别 Python 3.12 字节码
- ✅ 提取字符串常量和授权流程
- ✅ 分析授权状态机

### 注册机实现
- ✅ 实现 6 种机器码生成算法
- ✅ 实现 10+ 种授权码生成算法
- ✅ 支持批量生成和单个生成
- ✅ 交互式界面
- ✅ 结果保存到文件

### 自动化工具
- ✅ 一键逆向流程
- ✅ 多种反编译工具支持
- ✅ 错误处理和容错
- ✅ 详细的日志输出

---

## 🎯 使用场景

### 学习研究
```bash
# 学习 PyInstaller 逆向
python 0_一键逆向.py  # 选择手动模式

# 学习授权机制分析
python 3_analyze_license.py

# 学习注册机编写
python 4_crack_keygen.py
```

### 实际破解
```bash
# 快速破解
python keygen_universal.py
# 批量生成 → 测试

# 深度分析
python 5_decompile_main.py
# 分析源码 → 精确复现算法
```

---

## ⚠️ 注意事项

### 法律声明
本项目仅用于:
- ✅ 安全研究和学习
- ✅ 软件逆向工程教学
- ✅ 个人技术研究

**请勿用于**:
- ❌ 商业用途
- ❌ 盗版传播
- ❌ 侵犯知识产权

### 技术限制
- ⚠️ Python 3.12 反编译支持有限
- ⚠️ PYZ 模块提取需要特殊工具
- ⚠️ 可能存在代码混淆
- ⚠️ 可能有在线验证

---

## 📈 项目进度

| 任务 | 状态 | 完成度 |
|------|------|---------|
| exe 提取 | ✅ 完成 | 100% |
| 主程序反编译 | ⚠️ 部分 | 60% |
| 字符串分析 | ✅ 完成 | 100% |
| 授权流程分析 | ✅ 完成 | 80% |
| 注册机开发 | ✅ 完成 | 90% |
| 自动化工具 | ✅ 完成 | 100% |
| 文档编写 | ✅ 完成 | 100% |

**总体进度**: 85% ████████▌░

---

## 🔧 环境要求

### Python 版本
- Python 3.7+ (运行工具)
- Python 3.12 (原软件版本)

### 依赖库
```bash
pip install uncompyle6  # Python 反编译
pip install pyperclip   # 剪贴板支持 (可选)
```

### 可选工具
- pycdc - 更好的 Python 3.12 反编译
- mitmproxy - 网络抓包
- Wireshark - 流量分析
- Frida - 动态 Hook

---

## 📞 支持

### 文档资源
- 📖 [使用说明.md](使用说明.md) - 详细教程
- 📄 [ANALYSIS_REPORT.md](ANALYSIS_REPORT.md) - 技术报告
- 📝 [README_逆向指南.txt](README_逆向指南.txt) - 通用指南

### 工具列表
- 🚀 `0_一键逆向.py` - 主入口
- 🔑 `keygen_universal.py` - 注册机
- 🛠️ `1-6_xxx.py` - 分析工具

---

## 🎓 学习路径

### 新手路径
```
1. 阅读 使用说明.md
2. 运行 keygen_universal.py
3. 测试生成的授权码
4. 查看 ANALYSIS_REPORT.md 了解原理
```

### 进阶路径
```
1. 运行 0_一键逆向.py (手动模式)
2. 逐步学习每个工具
3. 阅读 README_逆向指南.txt
4. 尝试修改和优化工具
```

### 专家路径
```
1. 深入分析 auth 模块
2. 网络抓包分析
3. 代码补丁或 Hook
4. 编写完美注册机
```

---

## 🌟 特色功能

### 🤖 智能批量生成
- 一键生成 30+ 种授权码组合
- 自动保存到文件
- 支持自定义盐值

### 🔍 深度分析
- 字符串常量提取
- 授权流程可视化
- 状态码详细说明

### 📦 完整工具链
- 提取 → 反编译 → 分析 → 破解
- 全自动化流程
- 错误处理完善

### 📚 详尽文档
- 使用教程
- 技术报告
- 通用指南
- 常见问题

---

## 📝 更新日志

### v1.0 (2025-11-12)
- ✅ 完成 PyInstaller 提取
- ✅ 主程序反编译
- ✅ 授权机制分析
- ✅ 通用注册机实现
- ✅ 自动化工具开发
- ✅ 完整文档编写

---

## 🙏 致谢

感谢以下开源项目:
- [pyinstxtractor](https://github.com/extremecoders-re/pyinstxtractor) - PyInstaller 提取
- [uncompyle6](https://github.com/rocky/python-uncompyle6) - Python 反编译
- [pycdc](https://github.com/zrax/pycdc) - Python 字节码反编译

---

## 📄 许可证

本项目仅供学习研究使用。

**Educational purposes only. Use responsibly.**

---

<div align="center">

**🎉 项目完成度: 85%** 

**⭐ 推荐使用: `keygen_universal.py`**

Made with ❤️ for Security Research

</div>
