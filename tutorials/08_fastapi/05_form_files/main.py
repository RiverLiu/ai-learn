from typing import Annotated

from fastapi import FastAPI, File, Form, UploadFile as FastAPIUploadFile
from pydantic import WithJsonSchema

app = FastAPI()

# 修复 Swagger UI 将 UploadFile 显示为文本框的问题
UploadFile = Annotated[
    FastAPIUploadFile,
    WithJsonSchema(
        {
            "type": "string",
            "format": "binary",
        }
    ),
]

@app.post("/login/")
def login(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    """使用表单数据登录。"""
    return {"username": username, "message": "登录成功"}
    

@app.post("/uploadfile/")
async def upload_file(file: Annotated[UploadFile, File()]):
    """单文件上传。"""
    content = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
    }


@app.post("/uploadfiles/")
async def upload_files(files: Annotated[list[UploadFile], File()]):
    """多文件上传。"""
    result = []
    for file in files:
        content = await file.read()
        result.append(
            {
                "filename": file.filename,
                "size": len(content),
            }
        )
    return {"files": result}
