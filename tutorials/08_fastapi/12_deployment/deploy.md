# 12 部署

了解生产环境部署要点。

## 环境变量

复制 `.env.example` 为 `.env` 并填写真实值：

```bash
cp .env.example .env
```

## 使用 Uvicorn 运行

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

如果已激活虚拟环境，可省略 `uv run`。生产环境建议关闭 `--reload`。

## 使用 Gunicorn + Uvicorn Worker

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Docker 示例

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 部署检查清单

- [ ] 使用强随机 `SECRET_KEY`
- [ ] 关闭调试模式 `DEBUG=false`
- [ ] 配置 HTTPS
- [ ] 使用反向代理（Nginx / Caddy）
- [ ] 配置日志收集
- [ ] 数据库迁移（如 Alembic）
- [ ] 监控与告警
