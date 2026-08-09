# 05 表单与文件

处理表单提交和文件上传。

## 运行

```bash
cd tutorials/08_fastapi/05_form_files
uv run uvicorn main:app --reload
```

## 测试接口

```bash
# 表单登录
curl -X POST "http://127.0.0.1:8000/login/" \
  -d "username=alice&password=secret"

# 单文件上传
curl -X POST "http://127.0.0.1:8000/uploadfile/" \
  -F "file=@README.md"

# 多文件上传
curl -X POST "http://127.0.0.1:8000/uploadfiles/" \
  -F "files=@README.md" \
  -F "files=@main.py"
```

## 知识点

- `Form()`：接收 `application/x-www-form-urlencoded` 表单数据
- `UploadFile`：上传文件对象，支持异步读取
- `File()`：声明文件类型参数
- 文件上传使用 `multipart/form-data`
- `UploadFile` 比 `bytes` 更省内存，适合大文件
