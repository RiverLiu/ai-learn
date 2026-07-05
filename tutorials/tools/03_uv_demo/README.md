# uv 项目示例

这是一个最小的 uv 项目，演示 uv 的基本工作流。

## 文件说明

- `pyproject.toml`：项目配置和依赖
- `main.py`：示例代码，使用 requests 获取网页状态码

## 使用步骤

### 1. 进入示例目录

```bash
cd tutorials/tools/03_uv_demo
```

### 2. 创建虚拟环境并安装依赖

```bash
uv sync
```

这会创建 `.venv` 目录并安装 `requests`。

### 3. 运行示例

```bash
uv run python main.py
```

预期输出：

```
https://www.example.com 的状态码是: 200
```

### 4. 查看已安装依赖

```bash
uv pip list
```

### 5. 手动激活虚拟环境（可选）

```bash
source .venv/bin/activate
python main.py
deactivate
```

## 练习

1. 尝试添加一个新依赖：`uv add httpx`
2. 修改 `main.py` 使用 `httpx` 替代 `requests`
3. 运行并验证：`uv run python main.py`
4. 删除依赖：`uv remove httpx`
