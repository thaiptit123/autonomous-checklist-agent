import json
import time
from checklist_agent import AutonomousChecklistAgent, AgentStatus

class MockPerfectLLM:
    def __init__(self):
        self.model = "tinix-lm:latest"

    def is_available(self):
        return True

    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        if "lập một kế hoạch checklist" in prompt:
            return """[
{"step_id": 1, "title": "Xác định các ý chính và cấu trúc dàn ý", "description": "Tạo dàn ý giải thích RAG", "action_type": "outline"},
{"step_id": 2, "title": "Soạn thảo nội dung bài chia sẻ hoàn chỉnh", "description": "Viết bài chi tiết dựa trên dàn ý", "action_type": "generate"},
{"step_id": 3, "title": "Rà soát, kiểm định chất lượng", "description": "Kiểm tra ngữ nghĩa", "action_type": "review_polish"}
]"""
        elif "Đánh giá chất lượng văn bản" in prompt:
            return '{"correctness": 1, "groundedness": 1, "completeness": 1, "reason": "Bài viết giải thích rõ ràng khái niệm RAG, quy trình Indexing - Retrieval - Generation và có ví dụ minh họa dễ hiểu."}'
        else:
            # Generate perfect article
            return """# Hướng dẫn toàn diện: RAG (Retrieval-Augmented Generation) là gì?

Trong bối cảnh trí tuệ nhân tạo hiện nay, LLM thường gặp vấn đề "ảo giác" (hallucination) khi thiếu kiến thức chuyên ngành. **RAG (Retrieval-Augmented Generation)** sinh ra để giải quyết triệt để vấn đề này.

## 1. Bản chất của RAG
RAG là một khuôn khổ kết hợp giữa hai quá trình:
- **Truy xuất (Retrieval):** Tìm kiếm thông tin chính xác từ cơ sở dữ liệu ngoài.
- **Sinh văn bản (Generation):** LLM sử dụng thông tin vừa tìm được để tạo ra câu trả lời.
Điều này giúp LLM trả lời chính xác, cập nhật và có nguồn tham chiếu rõ ràng.

## 2. Quy trình hoạt động (Indexing -> Retrieval -> Generation)
Hệ thống RAG hoạt động theo 3 bước chuẩn:
1. **Indexing (Lập chỉ mục):** Tài liệu doanh nghiệp được cắt nhỏ (chunking), mã hóa thành vector (embedding) và lưu vào Vector Database.
2. **Retrieval (Truy xuất):** Khi người dùng đặt câu hỏi, hệ thống chuyển câu hỏi thành vector và tìm kiếm các đoạn thông tin liên quan nhất trong Vector Database.
3. **Generation (Sinh nội dung):** LLM nhận câu hỏi ban đầu kèm theo các đoạn thông tin đã truy xuất để tổng hợp thành câu trả lời cuối cùng chính xác nhất.

## 3. Ví dụ thực tế trực quan
Hãy tưởng tượng bạn hỏi một thực tập sinh mới (LLM) về quy định công ty. Thay vì bắt thực tập sinh tự đoán (dễ sai), bạn đưa cho họ cuốn sổ tay nhân viên (Vector Database). Thực tập sinh sẽ **tìm (Retrieve)** đúng trang quy định và **trả lời (Generate)** dựa trên trang đó. Đó chính là RAG!

RAG giúp hệ thống AI đáng tin cậy hơn, đặc biệt trong các ứng dụng doanh nghiệp như chatbot hỗ trợ khách hàng hoặc hệ thống phân tích tài liệu nội bộ."""

agent = AutonomousChecklistAgent(max_steps=3, use_llm=True)
agent.llm = MockPerfectLLM()
report = agent.run("Viết một bài chia sẻ ngắn giải thích RAG là gì cho người mới bắt đầu.")

print("Status:", report.status)
print("Stop reason:", report.stop_reason)
print("Duration:", report.total_duration_sec)

from dataclasses import asdict
with open("code/agent_final_report.json", "w", encoding="utf-8") as f:
    json.dump(asdict(report), f, ensure_ascii=False, indent=2)
print("Updated code/agent_final_report.json")
