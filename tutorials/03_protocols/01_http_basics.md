# HTTP/HTTPS 协议基础

## 什么是 HTTP

HTTP（HyperText Transfer Protocol，超文本传输协议）是 Web 通信的基础协议。它是一个**请求-响应**协议：客户端发送请求，服务器返回响应。

## URL 结构

```
https://www.example.com:443/path/to/resource?key=value#section
\___/   \_____________/ \__/ \_____________/ \_______/ \______/
  协议        主机名       端口      路径         查询参数    锚点
```

- **协议**：`http` 或 `https`
- **主机名**：域名或 IP 地址
- **端口**：HTTP 默认 80，HTTPS 默认 443
- **路径**：资源在服务器上的位置
- **查询参数**：`?key=value&foo=bar`

## HTTP 方法

| 方法 | 说明 | 示例 |
|------|------|------|
| GET | 获取资源 | 获取网页、查询数据 |
| POST | 创建资源 | 提交表单、注册用户 |
| PUT | 完整更新资源 | 修改用户信息 |
| PATCH | 部分更新资源 | 修改用户昵称 |
| DELETE | 删除资源 | 删除文章 |
| HEAD | 获取响应头 | 检查资源是否存在 |
| OPTIONS | 获取支持的方法 | CORS 预检请求 |

## HTTP 状态码

### 1xx 信息响应
- `100 Continue`：继续发送请求

### 2xx 成功
- `200 OK`：请求成功
- `201 Created`：资源创建成功
- `204 No Content`：成功但无返回内容

### 3xx 重定向
- `301 Moved Permanently`：永久重定向
- `302 Found`：临时重定向
- `304 Not Modified`：资源未修改，可使用缓存

### 4xx 客户端错误
- `400 Bad Request`：请求格式错误
- `401 Unauthorized`：未认证
- `403 Forbidden`：无权限
- `404 Not Found`：资源不存在
- `422 Unprocessable Entity`：参数校验失败（常见于 FastAPI）

### 5xx 服务器错误
- `500 Internal Server Error`：服务器内部错误
- `502 Bad Gateway`：网关错误
- `503 Service Unavailable`：服务不可用

## 请求报文结构

```http
POST /users HTTP/1.1
Host: api.example.com
Content-Type: application/json
Authorization: Bearer xxx
Content-Length: 56

{"username":"alice","email":"alice@example.com"}
```

- 请求行：`方法 路径 协议版本`
- 请求头：键值对，描述请求信息
- 空行
- 请求体：POST/PUT/PATCH 通常带有请求体

## 响应报文结构

```http
HTTP/1.1 201 Created
Content-Type: application/json
Content-Length: 45

{"id":1,"username":"alice","email":"alice@example.com"}
```

- 状态行：`协议版本 状态码 状态文本`
- 响应头：键值对，描述响应信息
- 空行
- 响应体：实际返回的数据

## 常见请求头

| 请求头 | 说明 |
|--------|------|
| `Host` | 目标主机 |
| `User-Agent` | 客户端标识 |
| `Accept` | 可接受的响应类型 |
| `Content-Type` | 请求体类型 |
| `Authorization` | 认证信息 |
| `Cookie` | 发送服务器之前设置的 Cookie |

## 常见响应头

| 响应头 | 说明 |
|--------|------|
| `Content-Type` | 响应体类型 |
| `Content-Length` | 响应体长度 |
| `Set-Cookie` | 设置 Cookie |
| `Location` | 重定向地址 |
| `Cache-Control` | 缓存控制 |

## HTTP 是无状态的

HTTP 协议本身不保存之前请求的状态。为了实现登录状态保持，常用：

- **Cookie**：服务器通过 `Set-Cookie` 发送，客户端后续请求自动带上
- **Session**：服务器端保存状态，通过 Cookie 中的 Session ID 关联
- **Token**：如 JWT，客户端每次请求通过 `Authorization` 头携带

## HTTPS

HTTPS = HTTP + SSL/TLS，在 HTTP 之下增加了加密层，提供：

1. **加密**：防止数据被窃听
2. **完整性**：防止数据被篡改
3. **身份认证**：通过证书验证服务器身份

### TLS 握手简化流程

1. 客户端发送支持的加密算法列表
2. 服务器返回证书和选定的加密算法
3. 客户端验证证书，生成会话密钥
4. 双方使用会话密钥加密通信

## 进一步学习

- HTTP/1.1: [RFC 9112](https://datatracker.ietf.org/doc/html/rfc9112)
- HTTP/2: [RFC 9113](https://datatracker.ietf.org/doc/html/rfc9113)
- HTTP 语义：[RFC 9110](https://datatracker.ietf.org/doc/html/rfc9110)
