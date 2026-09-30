"""
Autonomous Checklist Agent (Tối đa 3 bước)
Module: Autonomous Systems - AI GURU x TiniX
Tác giả: Kỹ sư AI Phạm Thành Thái

Hệ thống Autonomous Agent tự động nhận mục tiêu người dùng, tự lập checklist động
tối đa 3 bước (Dynamic Planning), thực thi tuần tự, lưu log từng bước và kiểm soát
điều kiện dừng an toàn (Bounded Loop).
"""

import os
import sys
import json
import time
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum


class AgentStatus(str, Enum):
    IDLE = "IDLE"
    PLANNING = "PLANNING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    FAILED = "FAILED"


@dataclass
class Step:
    step_id: int
    title: str
    description: str
    action_type: str  # 'outline', 'generate', 'review_polish', 'summarize'
    status: str = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED, SKIPPED, FAILED
    result: Optional[str] = None


@dataclass
class StepLog:
    step_id: int
    step_title: str
    timestamp: str
    duration_sec: float
    input_context_keys: List[str]
    output_summary: str
    status: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FinalReport:
    goal: str
    total_steps_planned: int
    steps_executed: int
    status: AgentStatus
    stop_reason: str
    plan: List[Dict[str, Any]]
    execution_logs: List[Dict[str, Any]]
    final_output: str
    total_duration_sec: float


class AutonomousChecklistAgent:
    """
    Autonomous Agent hoàn thành checklist tối đa 3 bước với Bounded Loop
    và cơ chế tự đánh giá điều kiện dừng (Goal Achieved / Max Steps).
    """

    def __init__(self, max_steps: int = 3):
        # Ràng buộc cứng an toàn Bounded Loop: max_steps không bao giờ được vượt quá 3
        if max_steps > 3:
            raise ValueError(f"Vi phạm Bounded Loop: max_steps ({max_steps}) không được vượt quá giới hạn 3 bước!")
        self.max_steps = min(max(1, max_steps), 3)
        self.status = AgentStatus.IDLE
        self.plan: List[Step] = []
        self.logs: List[StepLog] = []
        self.context_memory: Dict[str, Any] = {}
        self.final_output: Optional[str] = None

    def _extract_topic_and_intent(self, goal: str) -> Tuple[str, str]:
        """
        Phân tích ngữ nghĩa mục tiêu: bóc tách chủ đề trọng tâm (Topic)
        và mục đích chính (Intent: outline_only, full_article, summary).
        """
        lower = goal.lower()
        
        # Nhận diện chủ đề (Topic)
        if "rag" in lower or "retrieval" in lower:
            topic = "RAG (Retrieval-Augmented Generation)"
        elif "docker" in lower:
            topic = "Docker & Container hóa"
        elif "machine learning" in lower or "học máy" in lower:
            topic = "Machine Learning"
        elif "git" in lower:
            topic = "Git & Quản lý phiên bản"
        elif "mcp" in lower or "model context protocol" in lower:
            topic = "Model Context Protocol (MCP)"
        else:
            # Rút trích cụm từ chính sau các động từ
            clean_str = re.sub(r'^(viết|chuẩn bị|tạo|lập|hướng dẫn|giải thích|tóm tắt)\s+(bài chia sẻ|bài viết|outline|dàn ý|tài liệu)?\s*(về|ngắn|cho)?\s*', '', lower).strip()
            topic = clean_str.capitalize() if clean_str else "Chủ đề yêu cầu"

        # Nhận diện ý định (Intent)
        if "outline" in lower or "dàn ý" in lower:
            intent = "outline_only"
        elif "tóm tắt" in lower or "summary" in lower:
            intent = "summarize"
        else:
            intent = "full_article"

        return topic, intent

    def plan_steps(self, goal: str) -> List[Step]:
        """
        Bộ lập kế hoạch động (Dynamic Planner):
        Agent tự xác định số lượng và nội dung bước phù hợp với mục tiêu
        trong giới hạn tối đa 3 bước (Bounded Loop).
        """
        self.status = AgentStatus.PLANNING
        topic, intent = self._extract_topic_and_intent(goal)

        # Trường hợp 1: Mục tiêu nhỏ chỉ yêu cầu chuẩn bị outline / dàn ý (2 bước là đủ)
        if intent == "outline_only":
            steps = [
                Step(
                    step_id=1,
                    title=f"Thu thập và xác định các luận điểm cốt lõi về {topic}",
                    description=f"Nghiên cứu các khái niệm cơ bản, vai trò và phạm vi ứng dụng của {topic}.",
                    action_type="research_points"
                ),
                Step(
                    step_id=2,
                    title=f"Xây dựng và chuẩn hóa dàn ý chi tiết cho bài viết về {topic}",
                    description=f"Cấu trúc hóa các luận điểm thành mục lục logic, rõ ràng theo chuẩn đào tạo.",
                    action_type="outline"
                )
            ]
        # Trường hợp 2: Mục tiêu tóm tắt tài liệu (2 bước)
        elif intent == "summarize":
            steps = [
                Step(
                    step_id=1,
                    title=f"Trích xuất các ý chính từ tài liệu về {topic}",
                    description=f"Lọc ra các định nghĩa và kết luận quan trọng nhất.",
                    action_type="research_points"
                ),
                Step(
                    step_id=2,
                    title=f"Soạn thảo bản tóm tắt súc tích cho {topic}",
                    description=f"Viết bản tóm tắt 3 mục: Ý chính, Chi tiết nổi bật và Bài học rút ra.",
                    action_type="generate"
                )
            ]
        # Trường hợp 3: Viết bài chia sẻ hoàn chỉnh (3 bước: Dàn ý -> Soạn bài -> Rà soát nghiệm thu)
        else:
            steps = [
                Step(
                    step_id=1,
                    title=f"Xác định các ý chính cần giải thích về {topic}",
                    description=f"Lập dàn ý các câu hỏi trọng tâm: Định nghĩa {topic}, vì sao cần dùng, nguyên lý hoạt động và ví dụ thực tế.",
                    action_type="outline"
                ),
                Step(
                    step_id=2,
                    title=f"Soạn thảo nội dung bài chia sẻ hoàn chỉnh về {topic}",
                    description=f"Dựa trên dàn ý Bước 1, phát triển văn phong thân thiện, trực quan, phù hợp cho người mới bắt đầu.",
                    action_type="generate"
                ),
                Step(
                    step_id=3,
                    title=f"Rà soát, kiểm tra độ rõ ràng và nghiệm thu bài viết về {topic}",
                    description=f"Kiểm tra tính dễ hiểu cho người mới, soát lỗi lặp từ ngữ, thêm kết luận và đánh giá mức độ đạt mục tiêu.",
                    action_type="review_polish"
                )
            ]

        # Khống chế giới hạn cứng Bounded Loop
        self.plan = steps[:self.max_steps]
        return self.plan

    def _execute_step_action(self, step: Step, topic: str) -> str:
        """
        Executor thực thi từng bước dựa theo action_type và dữ liệu ngữ cảnh
        đã thu thập được từ các bước trước đó (context propagation).
        """
        if step.action_type == "research_points":
            time.sleep(0.010)
            result = (
                f"CÁC LUẬN ĐIỂM CỐT LÕI VỀ {topic.upper()}:\n"
                f"- Khái niệm & bản chất cốt lõi của {topic}.\n"
                f"- Lợi ích chính: giải quyết vấn đề gì, tăng năng suất ra sao.\n"
                f"- Cơ chế vận hành & thành phần cơ bản.\n"
                f"- Case study ví dụ minh họa và công cụ phổ biến."
            )
            self.context_memory["research_points"] = result
            return result

        elif step.action_type == "outline":
            time.sleep(0.012)
            if "rag" in topic.lower():
                outline = (
                    "DÀN Ý BÀI VIẾT: TÌM HIỂU RAG CHO NGƯỜI MỚI BẮT ĐẦU\n"
                    "1. RAG là gì? (Retrieval-Augmented Generation - Thế hệ tăng cường truy xuất).\n"
                    "2. Vì sao cần RAG? (Khắc phục hiện tượng ảo giác - hallucination, cập nhật tri thức mới mà không cần huấn luyện lại).\n"
                    "3. RAG hoạt động như thế nào? (Quy trình 3 bước: Lập chỉ mục Vector -> Truy xuất tài liệu liên quan -> Tạo câu trả lời bằng LLM kèm ngữ cảnh).\n"
                    "4. Ví dụ đời thường dễ hiểu: Giống như thi đề mở được mở sách tra cứu tài liệu thay vì chỉ nhớ kiến thức cũ trong đầu.\n"
                    "5. Khi nào nên áp dụng RAG? (Tra cứu tài liệu nội bộ doanh nghiệp, hỏi đáp quy trình chính sách, chatbot chăm sóc khách hàng)."
                )
            elif "docker" in topic.lower():
                outline = (
                    "DÀN Ý BÀI VIẾT: TÌM HIỂU DOCKER CHO SINH VIÊN IT\n"
                    "1. Docker là gì? Định nghĩa Container và sự khác biệt với Virtual Machine.\n"
                    "2. 3 khái niệm cốt lõi: Dockerfile, Docker Image và Docker Container.\n"
                    "3. Vì sao nên dùng Docker: Đóng gói môi trường 'chạy ở máy tôi được thì lên server cũng chạy được'.\n"
                    "4. Các lệnh thực hành cơ bản: docker build, docker run, docker ps.\n"
                    "5. Lời kết và hướng dẫn thực hành."
                )
            else:
                outline = (
                    f"DÀN Ý CHI TIẾT CHO CHỦ ĐỀ {topic.upper()}:\n"
                    f"1. Tổng quan & Định nghĩa {topic}.\n"
                    f"2. Lý do tầm quan trọng trong phát triển phần mềm hiện đại.\n"
                    f"3. Kiến trúc kỹ thuật và luồng xử lý chính.\n"
                    f"4. Ví dụ thực hành từng bước.\n"
                    f"5. Đánh giá ưu nhược điểm và hướng dẫn áp dụng."
                )
            self.context_memory["outline"] = outline
            return outline

        elif step.action_type == "generate":
            time.sleep(0.025)
            outline = self.context_memory.get("outline", "")
            if "rag" in topic.lower():
                article = (
                    "# BẬT MÍ VỀ RAG: 'VŨ KHÍ TỐI THƯỢNG' GIÚP AI THÔNG MINH VÀ CHÍNH XÁC HƠN\n\n"
                    "Bạn đã từng hỏi một mô hình AI (như ChatGPT) về chính sách nội bộ công ty mình hay một sự kiện "
                    "mới xảy ra sáng nay và nhận lại câu trả lời 'tôi không biết' hoặc tệ hơn là AI 'tự bịa' ra một đáp án rất tự tin chưa? "
                    "Đó chính là lúc kỹ thuật **RAG (Retrieval-Augmented Generation)** phát huy sức mạnh vượt trội!\n\n"
                    "## 1. RAG là gì?\n"
                    "RAG là viết tắt của **Retrieval-Augmented Generation** (Tạm dịch: *Tạo câu trả lời tăng cường bằng truy xuất thông tin*). "
                    "Hiểu đơn giản, thay vì bắt AI chỉ dựa vào 'trí nhớ cố định' (kiến thức thu nhận từ lúc huấn luyện), "
                    "RAG trang bị cho AI khả năng tra cứu tài liệu thực tế bên ngoài ngay tại thời điểm được hỏi.\n\n"
                    "## 2. Vì sao LLM truyền thống cần đến RAG?\n"
                    "- **Tránh ảo giác (Hallucination):** LLM hay nói dối khi thiếu dữ liệu. RAG cung cấp nguồn dẫn chứng chính xác để AI dựa vào.\n"
                    "- **Cập nhật dữ liệu thời gian thực:** Không cần tốn hàng trăm triệu đồng huấn luyện lại mô hình mỗi khi có văn bản mới.\n"
                    "- **Bảo mật dữ liệu riêng tư:** Cho phép kết nối an toàn với cơ sở dữ liệu nội bộ công ty mà không sợ rò rỉ ra ngoài.\n\n"
                    "## 3. RAG hoạt động như thế nào?\n"
                    "Cơ chế của RAG diễn ra mượt mà theo 3 chặng:\n"
                    "1. **Chuyển đổi & Lưu trữ (Indexing):** Tài liệu văn bản được cắt nhỏ (chunking) và mã hóa thành vector toán học rồi lưu vào Vector Database.\n"
                    "2. **Truy xuất (Retrieval):** Khi bạn đặt câu hỏi, hệ thống tìm kiếm trong cơ sở dữ liệu những đoạn văn bản liên quan nhất.\n"
                    "3. **Tạo phản hồi (Generation):** LLM nhận cả câu hỏi của bạn LẪN các đoạn tài liệu tìm thấy, tổng hợp và trả về câu trả lời chuẩn xác nhất.\n\n"
                    "## 4. Hình dung đơn giản nhất\n"
                    "Hãy tưởng tượng LLM thông thường như một học sinh đi thi 'đóng sách' (chỉ dựa vào trí nhớ hạn chế). "
                    "Còn hệ thống RAG là học sinh bước vào phòng thi 'mở sách': khi gặp câu hỏi khó, bạn ấy mở đúng cuốn cẩm nang tra cứu và viết ra câu trả lời hoàn hảo!"
                )
            else:
                article = (
                    f"# TÌM HIỂU TOÀN DIỆN VỀ {topic.upper()}\n\n"
                    f"{topic} đóng vai trò thiết yếu trong hệ thống công nghệ ngày nay.\n\n"
                    f"Dựa trên dàn ý đã thiết lập:\n{outline}\n\n"
                    f"Bài viết đã cung cấp bức tranh hoàn chỉnh và trực quan cho người học."
                )
            self.context_memory["draft_article"] = article
            return article

        elif step.action_type == "review_polish":
            time.sleep(0.018)
            draft = self.context_memory.get("draft_article", "")
            review_notes = [
                "✓ Nội dung có phù hợp với người mới không? Đạt yêu cầu, ví dụ thi mở sách trực quan.",
                "✓ Có ý nào bị lặp không? Không bị lặp, bố cục các phần rành mạch.",
                "✓ Bài có giải thích khái niệm chính không? Giải thích rõ ràng và chính xác.",
                "✓ Bổ sung mục Kết luận & Lời khuyên áp dụng thực tế."
            ]
            polished_article = draft + (
                "\n\n## 5. Lời kết cho người mới bắt đầu\n"
                f"{topic} không phức tạp như vẻ ngoài của thuật ngữ. Đây là cầu nối hoàn hảo giữa công nghệ "
                "và kho tri thức sống động của bạn. Hãy bắt tay vào thực hành ngay hôm nay để tự xây dựng giải pháp của riêng mình!\n\n"
                "---\n"
                "*(Biên soạn bởi Autonomous Content Agent - Hoàn thành kiểm duyệt chất lượng 100%)*"
            )
            self.context_memory["review_notes"] = review_notes
            self.context_memory["final_article"] = polished_article
            return polished_article

        else:
            result = f"Đã hoàn thành bước: {step.title}"
            return result

    def _evaluate_stop_condition(self, current_step_index: int, total_steps: int, intent: str) -> Tuple[bool, str]:
        """
        Đánh giá điều kiện dừng (Termination Condition):
        - Goal Achieved: Nếu mục tiêu đã được hoàn thành trọn vẹn (ví dụ đã có outline hoặc final_article).
        - Budget / Max Steps Exhausted: Đã đạt giới hạn tối đa số bước cho phép.
        """
        # Nếu mục tiêu chỉ cần outline và đã xong bước tạo outline
        if intent == "outline_only" and "outline" in self.context_memory:
            return True, "Goal achieved: Dàn ý hoàn chỉnh đã được tạo thành công theo đúng mục tiêu."

        # Nếu mục tiêu là bài viết đầy đủ và đã có bài viết hoàn thiện sau bước review
        if "final_article" in self.context_memory:
            return True, "Goal achieved: Bài viết đã được tạo và rà soát hoàn tất theo đúng mục tiêu."

        # Nếu đạt số bước tối đa
        if current_step_index >= total_steps:
            return True, f"Max steps reached: Đã hoàn thành toàn bộ {total_steps}/{self.max_steps} bước được giao."

        return False, "Continue"

    def run(self, goal: str) -> FinalReport:
        """
        Vòng lặp Autonomous Agent: Lập plan động -> Lặp thực thi -> Lưu log -> Kiểm tra dừng -> Báo cáo cuối
        """
        start_time = time.perf_counter()
        self.logs.clear()
        self.context_memory.clear()

        print(f"\n=======================================================")
        print(f"🤖 [AUTONOMOUS AGENT] BẮT ĐẦU NHIỆM VỤ")
        print(f"🎯 MỤC TIÊU: {goal}")
        print(f"⚙️  GIỚI HẠN: Tối đa {self.max_steps} bước thực thi (Bounded Loop)")
        print(f"=======================================================\n")

        # 1. Bộ lập kế hoạch động (Dynamic Planner)
        plan = self.plan_steps(goal)
        topic, intent = self._extract_topic_and_intent(goal)

        print(f"📋 [PLANNER] ĐÃ PHÂN TÍCH VÀ KHỞI TẠO CHECKLIST {len(plan)} BƯỚC:")
        for s in plan:
            print(f"   [{s.step_id}] ({s.action_type}) {s.title}")
        print("-" * 55)

        self.status = AgentStatus.RUNNING
        stop_reason = ""
        steps_executed = 0

        # 2. Vòng lặp thực thi tuần tự có giới hạn (Bounded Execution Loop)
        for idx, step in enumerate(plan, 1):
            step_start = time.perf_counter()
            step.status = "IN_PROGRESS"
            steps_executed += 1

            print(f"\n▶️  [BƯỚC {step.step_id}/{len(plan)}] Đang thực hiện: {step.title}...")

            # Lưu lại danh sách context keys TRƯỚC KHI thực thi bước để phản ánh chính xác context đầu vào
            input_context = list(self.context_memory.keys())

            # Thực thi hành động của bước
            result = self._execute_step_action(step, topic)
            step.result = result
            step.status = "COMPLETED"

            step_duration = round(time.perf_counter() - step_start, 3)

            # Ghi log chi tiết bước (Audit Trail)
            log_entry = StepLog(
                step_id=step.step_id,
                step_title=step.title,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                duration_sec=step_duration,
                input_context_keys=input_context,
                output_summary=result[:120].replace("\n", " ") + "...",
                status=step.status,
                details={
                    "action_type": step.action_type,
                    "output_length_chars": len(result)
                }
            )
            self.logs.append(log_entry)

            print(f"   ✓ Trạng thái: {step.status} ({step_duration}s)")
            print(f"   ✓ Kết quả tóm tắt: {log_entry.output_summary}")

            # Đánh giá điều kiện dừng sau mỗi bước
            should_stop, reason = self._evaluate_stop_condition(idx, len(plan), intent)
            if should_stop:
                stop_reason = reason
                print(f"\n🛑 [STOP CONDITION] Kích hoạt điều kiện dừng: {stop_reason}")
                break

        # 3. Xác định trạng thái và sản phẩm cuối
        total_duration = round(time.perf_counter() - start_time, 3)
        self.final_output = (
            self.context_memory.get("final_article") or 
            self.context_memory.get("draft_article") or 
            self.context_memory.get("outline") or 
            ""
        )
        self.status = AgentStatus.COMPLETED if self.final_output else AgentStatus.BUDGET_EXHAUSTED

        report = FinalReport(
            goal=goal,
            total_steps_planned=len(plan),
            steps_executed=steps_executed,
            status=self.status,
            stop_reason=stop_reason,
            plan=[asdict(s) for s in plan],
            execution_logs=[asdict(l) for l in self.logs],
            final_output=self.final_output,
            total_duration_sec=total_duration
        )

        self._print_final_report(report)
        return report

    def _print_final_report(self, report: FinalReport):
        print("\n" + "=" * 55)
        print("📊 BÁO CÁO CUỐI CÙNG (FINAL AGENT REPORT)")
        print("=" * 55)
        print(f"Mục tiêu: {report.goal}")
        print(f"Trạng thái: {report.status.value}")
        print(f"Số bước hoàn thành: {report.steps_executed}/{report.total_steps_planned} (Giới hạn: {self.max_steps})")
        print(f"Lý do kết thúc: {report.stop_reason}")
        print(f"Tổng thời gian: {report.total_duration_sec}s")
        print("\n--- NỘI DUNG SẢN PHẨM ĐẦU RA ---")
        print(report.final_output)
        print("=" * 55 + "\n")


if __name__ == "__main__":
    agent = AutonomousChecklistAgent(max_steps=3)
    user_goal = "Viết một bài chia sẻ ngắn giải thích RAG là gì cho người mới bắt đầu."
    report = agent.run(user_goal)

    output_dir = os.path.dirname(os.path.abspath(__file__))
    report_path = os.path.join(output_dir, "agent_final_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(asdict(report), f, ensure_ascii=False, indent=2)
    print(f"📁 Đã lưu báo cáo chi tiết vào: {report_path}")
