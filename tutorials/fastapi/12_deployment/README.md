# 12 部署

了解生产环境部署要点。

## 运行

```bash
cd tutorials/fastapi/12_deployment
uv run uvicorn main:app --reload
```

## 测试

```bash
curl "http://127.0.0.1:8000/"
curl "http://127.0.0.1:8000/health"
```

## 知识点

- 使用 `pydantic_settings` 从环境变量读取配置
- `.env.example` 作为配置模板，不提交真实密钥
- 生产环境关闭 `reload` 和 `debug`
- Uvicorn 与 Gunicorn 部署方式
- Docker 基础镜像选择
