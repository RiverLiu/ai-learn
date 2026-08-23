# 12 部署

了解生产环境部署要点。

本章示例展示三种运行方式：

- 本机开发运行：`uvicorn --reload`
- 本机生产形式运行：`uvicorn --host 0.0.0.0 --port 8000`
- 容器运行：`Dockerfile` / `docker-compose.yml`

## 运行

```bash
cd tutorials/08_fastapi/12_deployment
uv run uvicorn main:app --reload
```

## 测试

```bash
curl "http://127.0.0.1:8000/"
curl "http://127.0.0.1:8000/health"
```

## Dockerfile

[Dockerfile](./Dockerfile) 把本章的 FastAPI 应用打包成一个可运行镜像：

```bash
cd tutorials/08_fastapi/12_deployment
docker build -t fastapi-deployment-demo .
docker run --rm -p 8000:8000 \
  -e SECRET_KEY="change-me" \
  -e DATABASE_URL="sqlite:////app/data/production.db" \
  -e DEBUG="false" \
  fastapi-deployment-demo
```

打开另一个终端测试：

```bash
curl "http://127.0.0.1:8000/health"
```

这个 Dockerfile 做了几件事：

- 使用 `python:3.12-slim` 作为基础镜像。
- 只安装本章运行需要的依赖：`fastapi`、`uvicorn[standard]`、`pydantic-settings`。
- 复制 `main.py` 和 `.env.example` 到镜像中。
- 创建非 root 用户 `appuser` 运行服务。
- 暴露 `8000` 端口。
- 用 `uvicorn main:app --host 0.0.0.0 --port 8000` 启动应用。

## Docker Compose

[docker-compose.yml](./docker-compose.yml) 适合本地模拟部署环境：

```bash
cd tutorials/08_fastapi/12_deployment
docker compose up --build
```

测试：

```bash
curl "http://127.0.0.1:8000/"
curl "http://127.0.0.1:8000/health"
```

停止并清理容器：

```bash
docker compose down
```

如果也要删除示例数据卷：

```bash
docker compose down -v
```

Compose 文件里包含：

- `api` 服务：从当前目录的 `Dockerfile` 构建镜像。
- `ports`：把宿主机 `8000` 映射到容器 `8000`。
- `environment`：注入 `SECRET_KEY`、`DATABASE_URL`、`DEBUG`。
- `volumes`：用 `deployment-data` 保存 SQLite 示例数据。
- `healthcheck`：定期请求 `/health` 判断容器是否健康。

## Dockerfile 和 Compose 的区别

| 文件 | 作用 | 典型命令 |
| --- | --- | --- |
| `Dockerfile` | 定义如何构建一个应用镜像 | `docker build`、`docker run` |
| `docker-compose.yml` | 定义一个或多个服务如何一起运行 | `docker compose up` |

单服务应用可以只用 Dockerfile。只要开始涉及数据库、缓存、后台 worker、反向代理，就更适合用 Compose 在本地组织多个服务。

## 知识点

- 使用 `pydantic_settings` 从环境变量读取配置
- `.env.example` 作为配置模板，不提交真实密钥
- 生产环境关闭 `reload` 和 `debug`
- Uvicorn 与 Gunicorn 部署方式
- Docker 基础镜像选择
- 容器中使用 `0.0.0.0` 监听，否则宿主机无法访问服务
- 用 healthcheck 暴露应用健康状态
