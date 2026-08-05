# 01 图像理解：让模型"看图说话"

前面的章节里，`messages` 中的 `content` 一直是纯字符串。本章把它升级成**数组**，
在同一条 user 消息里同时放下文字和图片，发给视觉模型，让模型描述图片内容。
测试图不需要任何第三方库——脚本用纯标准库（`zlib` + `struct`）手写 PNG 编码现场生成一张。

## 本章要点

- **多模态消息结构**：`content` 从字符串变成数组，每个元素是 `{"type": "text", ...}`
  或 `{"type": "image_url", ...}`，其余调用方式与纯文本完全一致。
- **图片两种给法**：公网 URL（模型服务自己去拉取）或 base64 data URL（图片随请求体上传，
  适合本地/私有图片）。本章用后者，图片不出本机。
- **图片按 token 计费**：图片会被折算成 token 计入输入用量，分辨率越高折算越多，
  一张图通常比一段文字贵一个量级。
- **模型名以官网为准**：视觉模型名走 `VISION_MODEL` 环境变量，缺省 `kimi-k2.6`
  （据 [Kimi 开放平台模型列表](https://platform.kimi.com/docs/models)，kimi-k2.6 / kimi-k3
  原生支持视觉输入；`moonshot-v1-8k/32k/128k-vision-preview` 系列仍在列表中但正逐步下线）。
- 脚本对 **400/403/404** 错误做了捕获：账号或服务商不支持视觉模型时打印切换指引，
  正常退出（退出码 0），不会甩一堆裸堆栈。

## 运行

```bash
uv run tutorials/multimodal/01_image_understanding/main.py
```

脚本有两种结局，都算成功：

- **真实识别成功**：模型描述图片（4 种颜色、三条彩条 + 黄色矩形）并打印 token 用量；
- **优雅降级**：当前账号/服务不支持视觉模型（400/403/404）时，打印核对模型名、
  更换 OpenAI 兼容视觉服务的分步指引，退出码仍为 0。

本章实测（2026-08，`OPENAI_BASE_URL=https://api.moonshot.cn`，缺省模型 `kimi-k2.6`）
走的是**真实识别成功**分支，实际输出节选：

```text
已生成测试图：.../tmp/multimodal_test_image.png
使用视觉模型：kimi-k2.6（可用 VISION_MODEL 环境变量覆盖）

【提问】请描述这张图片：图里有几种颜色？分别是什么形状、在什么位置？
【模型回答】这张图中有 **4种颜色**，分别是 **红色、绿色、蓝色和黄色**。
……红色长方形在最上方，绿色在中间，蓝色在最下方，
黄色矩形位于画面正中央，叠加在绿色横条上面……

token 用量：输入 73（含图片折算） + 输出 1184 = 共 1257 token
```

模型正确说出了 4 种颜色、三条水平彩条和居中的黄色矩形。打开 `tmp/multimodal_test_image.png`
可以对照验证。

## 核心概念

### 多模态消息：content 从字符串变成数组

纯文本消息的 `content` 是一个字符串；要发图片，就把它改成**内容块数组**，
文字和图片各占一块，顺序随意：

```python
messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "图里有几种颜色？"},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64,iVBOR..."}},
        ],
    }
]
```

`model`、`response.choices[0].message.content` 等其他一切用法与纯文本调用完全相同——
多模态只是"消息里能装的东西变多了"，不是一套新 API。同一条消息里也可以放多张图。

### 图片的两种给法：base64 data URL vs 公网 URL

| 方式 | `image_url.url` 的形式 | 适用场景 |
| --- | --- | --- |
| 公网 URL | `https://example.com/pic.jpg` | 图片已在公网/对象存储上，模型服务自己去拉取，请求体小 |
| base64 data URL | `data:image/png;base64,<编码>` | 本地图片、私有图片：随请求体上传，不需要图床 |

data URL 的格式是 `data:<MIME 类型>;base64,<base64 编码>`。base64 会把字节体积放大约 1/3，
图片别太大（本章的测试图只有几百字节）；几 MB 以上的大图建议先压缩或改用公网 URL。

### 图片 token 计费

图片不是"免费附带"的：服务商会按图片尺寸把图片折算成 token，计入 `usage.prompt_tokens`。
分辨率越高、图片越多，折算的 token 越多，一张普通截图通常值几百到上千 token——
比同样信息量的一段文字贵得多。批量处理图片前先算一笔账，必要时先降分辨率再发送。
响应里的 `usage` 对象（本章脚本会打印）是核对实际计费的入口。

### 视觉模型名：以官网为准

各平台的视觉模型 ID 变动很快（新模型上线、旧模型下线）。本章缺省用 `kimi-k2.6`，
以 [Kimi 开放平台模型列表](https://platform.kimi.com/docs/models) 的实时信息为准；
该列表中另有 `moonshot-v1-8k/32k/128k-vision-preview` 系列（正逐步停止开放）。
用 `VISION_MODEL` 环境变量覆盖即可换模型，代码不用动：

```bash
# 项目根目录 .env 中追加一行
VISION_MODEL=kimi-k2.6
```

### 纯标准库生成 PNG（附）

PNG 文件 = 8 字节签名 + 若干"块"（IHDR 图像头 / IDAT 图像数据 / IEND 结束），
每块带 CRC32 校验；图像数据是逐行扫描线（每行前缀 1 字节过滤器类型）经 `zlib` 压缩。
了解这个结构对学习"字节流、二进制协议"很有帮助，但生产中请直接用 PIL/Pillow。

## 常见错误

1. **HTTP 404 `model not found` / 403 无权限**：模型名错了，或账号没开通该视觉模型。
   脚本会打印指引；核对官网模型列表后用 `VISION_MODEL` 指定正确的名字。
2. **HTTP 400 `invalid messages` 之类**：content 数组结构写错——每项必须有 `type` 字段，
   图片项是 `{"type": "image_url", "image_url": {"url": ...}}`（注意 `url` 包在子对象里），
   不是 `{"type": "image_url", "url": ...}`。
3. **把 data URL 的 MIME 类型写错**：`data:image/png;base64,...` 的前缀要和实际格式一致，
   JPEG 就写 `image/jpeg`，否则部分服务会直接拒绝。
4. **图片太大导致请求体超限或费用爆炸**：base64 后体积约放大 1/3，几 MB 的原图先压缩、
   降分辨率再发；批量任务务必先看 `usage` 再放量。
5. **OPENAI_BASE_URL 带路径后缀**：只到 `/v1` 为止，与根目录 `.env.example` 的注释一致；
   换服务商时 `MODEL_NAME` / `VISION_MODEL` 也要一起换成对方有的模型。

## 练习建议

1. 改 `make_test_png()`：换成竖条、加更多颜色或画一个圆形，看模型描述是否仍然准确；
   再试试故意问"图里有紫色吗"，观察模型会不会顺着你说（幻觉）。
2. 把 `image_url` 换成一个公网图片 URL（如任意可公开访问的照片），对比两种给法的效果。
3. 用 PIL 之外的方式准备一张真实照片（手机拍一张转 PNG/JPEG），base64 后让模型做 OCR
   或内容理解，打印 `usage` 对比真实图片与本章小测试图的 token 折算差异。
4. 在 `.env` 里把 `VISION_MODEL` 指向另一家兼容服务的视觉模型（如阿里百炼
   `qwen-vl-plus`），验证"只换环境变量、不换代码"的可移植性。
