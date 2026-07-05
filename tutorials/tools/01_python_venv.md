# Python 虚拟环境 venv

## 为什么需要虚拟环境

Python 项目经常依赖不同的第三方库，不同项目可能需要同一库的不同版本。如果在全局环境中安装所有依赖，很容易出现版本冲突。

**虚拟环境** 是项目独立的 Python 运行环境：

- 每个项目有自己的依赖集合
- 不影响系统或其他项目的 Python 环境
- 便于复现和部署

## 创建虚拟环境

```bash
# 在项目目录中创建名为 .venv 的虚拟环境
python3 -m venv .venv
```

也可以指定其他名称：

```bash
python3 -m venv myenv
```

## 激活虚拟环境

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows (cmd)

```cmd
.venv\Scripts\activate.bat
```

### Windows (PowerShell)

```powershell
.venv\Scripts\Activate.ps1
```

激活后，命令行提示符前会显示虚拟环境名称：

```bash
(.venv) $
```

## 安装依赖

激活虚拟环境后，使用 `pip` 安装包：

```bash
pip install requests
```

## 导出依赖

将当前环境的依赖记录到文件：

```bash
pip freeze > requirements.txt
```

## 安装 requirements.txt

```bash
pip install -r requirements.txt
```

## 退出虚拟环境

```bash
deactivate
```

## 删除虚拟环境

虚拟环境就是项目中的一个目录，直接删除即可：

```bash
rm -rf .venv
```

## 完整流程示例

```bash
# 1. 创建
python3 -m venv .venv

# 2. 激活
source .venv/bin/activate

# 3. 安装依赖
pip install requests

# 4. 导出
pip freeze > requirements.txt

# 5. 退出
deactivate

# 6. 删除
rm -rf .venv
```

## venv 的优缺点

**优点**：
- Python 内置，无需额外安装
- 概念简单，容易理解

**缺点**：
- `pip install` 后直接修改环境，缺少 lock 文件
- 依赖解析速度较慢
- `requirements.txt` 包含所有子依赖，不够精确

## 现代替代方案

- **uv**：用 Rust 编写，极速，兼容 pip，支持 pyproject.toml
- **poetry**：依赖管理 + 打包发布
- **pdm**：PEP 582 风格的包管理器

本项目使用 `uv`，下一节介绍。
