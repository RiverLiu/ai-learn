"""logging 日志示例：不同级别、格式化输出、写入文件。"""

import logging

# 配置日志：级别、格式、同时输出到控制台和文件
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),                      # 控制台
        logging.FileHandler("example.log", encoding="utf-8"),  # 文件
    ],
)

logger = logging.getLogger("demo")


def main():
    logger.debug("调试信息：变量细节，生产环境一般不输出")
    logger.info("普通信息：程序运行到了哪里")
    logger.warning("警告：不致命，但值得注意")
    logger.error("错误：某个操作失败了")

    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("异常日志：自动附带堆栈信息")


if __name__ == "__main__":
    main()
