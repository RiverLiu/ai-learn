# 06 依赖注入

掌握 FastAPI 强大的依赖注入系统。

## 运行

```bash
cd tutorials/08_fastapi/06_dependencies
uv run uvicorn main:app --reload
```

## 测试接口

```bash
# 类依赖 + 通用查询参数
curl "http://127.0.0.1:8000/items/?q=phone&skip=0&limit=5"

# 函数依赖 + 数据库会话
curl "http://127.0.0.1:8000/users/?skip=10&limit=20"
```

## 知识点

- `Depends()`：声明依赖
- 依赖可以是函数、类或两者的组合
- 子依赖：依赖函数内部可以继续使用 `Depends`
- 依赖结果可以被缓存（同一请求内多次使用只执行一次）
- 适合抽取通用逻辑：分页、认证、数据库会话
