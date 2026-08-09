"""多模态工作流离线示例。

不调用视觉或语音模型，用模拟的 OCR/ASR/视觉识别结果演示：
图片/音频 -> 结构化文本 -> 业务提示词输入。

运行：
    uv run tutorials/18_multimodal/03_multimodal_workflows/main.py
"""

import json


def build_support_case_from_screenshot() -> dict:
    vision_result = {
        "image_type": "error_screenshot",
        "detected_text": ["Upload failed", "Error E1024", "Retry"],
        "ui_state": "文件上传失败",
    }
    return {
        "case_type": "technical_issue",
        "evidence_type": "screenshot",
        "query_for_rag": "Error E1024 文件上传失败 排查步骤",
        "structured_context": vision_result,
        "needs_human_review": False,
    }


def build_meeting_summary_input() -> dict:
    asr_result = {
        "segments": [
            {"speaker": "A", "text": "我们下周灰度知识库客服。"},
            {"speaker": "B", "text": "我负责整理 FAQ，小王负责部署。"},
        ]
    }
    return {
        "case_type": "meeting_summary",
        "evidence_type": "audio_transcript",
        "structured_context": asr_result,
        "expected_output": ["summary", "decisions", "action_items"],
        "needs_human_review": False,
    }


def build_invoice_extraction_case() -> dict:
    ocr_result = {
        "invoice_no": "INV-2026-001",
        "amount": "299.00",
        "date": "2026-08-09",
        "seller": "云雀科技",
    }
    return {
        "case_type": "invoice_extraction",
        "evidence_type": "ocr",
        "structured_context": ocr_result,
        "expected_output": ["invoice_no", "amount", "date", "seller"],
        "needs_human_review": True,
    }


def main() -> None:
    cases = [
        build_support_case_from_screenshot(),
        build_meeting_summary_input(),
        build_invoice_extraction_case(),
    ]
    for case in cases:
        print("\n===== 多模态业务输入 =====")
        print(json.dumps(case, ensure_ascii=False, indent=2))
        if case["needs_human_review"]:
            print("提示：该流程包含高风险字段，进入业务系统前需要人工复核。")


if __name__ == "__main__":
    main()
