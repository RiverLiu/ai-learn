import time
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动和关闭事件。"""
    print("应用启动...")
    yield
    print("应用关闭...")


app = FastAPI(lifespan=lifespan)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """自定义中间件：记录请求处理时间。"""
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


def write_log(message: str):
    """模拟后台任务。"""
    time.sleep(1)  # 模拟耗时操作
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"{message}\n")


@app.post("/send-notification/{email}")
def send_notification(email: str, background_tasks: BackgroundTasks):
    """提交后台任务后立刻返回响应。"""
    background_tasks.add_task(write_log, f"通知已发送给 {email}")
    return {"message": "通知正在后台发送", "email": email}


@app.get("/")
def read_root():
    return {"message": "Hello with middleware and CORS"}
