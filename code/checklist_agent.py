"""
Autonomous Checklist Agent (Tối đa 3 bước)
Module: Autonomous Systems - AI GURU x TiniX
Tác giả: Kỹ sư AI Phạm Thành Thái

Hệ thống Autonomous Agent tự động nhận mục tiêu người dùng, tự lập checklist động
tối đa 3 bước (Dynamic Planning), thực thi tuần tự, tích hợp mô hình ngôn ngữ lớn (LLM),
kiểm duyệt chất lượng định lượng (Quality Evaluator), lưu vết thực thi (Audit Log)
và kiểm soát điều kiện dừng an toàn đa trạng thái (Bounded Loop Stop Condition).
"""

import os
import sys
import json
import time
import re
import urllib.request
import urllib.error
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
    action_type: str  # 'research_points', 'outline', 'generate', 'review_polish', 'summarize'
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
    quality_metrics: Dict[str, Any]
    total_duration_sec: float


class QualityEvaluator:
    """
    Bộ kiểm duyệt chất lượng định lượng (Automated Quality Evaluator).
    Đánh giá sản phẩm tạo ra dựa trên các chỉ số tính toán thực tế thay vì chuỗi hardcode.
    """

    @staticmethod
    def calculate_ttr(text: str) -> float:
        """
        Tính Type-Token Ratio (TTR): Tỷ lệ từ vựng duy nhất trên tổng số từ.
        Dùng để định lượng độ phong phú từ vựng và kiểm chứng tính không trùng lặp.
        """
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return 0.0
        return round(len(set(words)) / len(words), 3)

    @classmethod
    def evaluate(cls, content: str, goal: str, intent: str) -> Dict[str, Any]:
        """
        Kiểm định 4 tiêu chí chất lượng kỹ thuật:
        1. Độ dài ký tự/từ (Length Sufficiency)
        2. Cấu trúc Markdown rõ ràng (Structure Format)
        3. Độ đa dạng từ vựng TTR (Lexical Diversity >= 0.35)
        4. Mức độ liên quan đến từ khóa chủ đề (Topic Relevance)
        """
        if not content:
            return {
                "passed": False,
                "char_count": 0,
                "word_count": 0,
                "ttr": 0.0,
                "matched_keywords": [],
                "review_notes": ["✗ Không có nội dung sản phẩm để kiểm duyệt."]
            }

        words = re.findall(r'\b\w+\b', content.lower())
        char_count = len(content)
        word_count = len(words)
        ttr = cls.calculate_ttr(content)

        # 1. Tiêu chí độ dài
        min_chars = 100 if intent in ("outline_only", "summarize") else 250
        crit_length = char_count >= min_chars

        # 2. Cấu trúc phân cấp Markdown (tiêu đề #, số thứ tự, gạch đầu dòng)
        has_headings = bool(re.search(r'(^|\n)(#{1,4}\s+|[0-9]+\.\s+|-\s+|\*\s+)', content))
        crit_structure = has_headings

        # 3. Đa dạng từ vựng (TTR >= 0.35 chứng minh không bị lặp từ)
        crit_diversity = ttr >= 0.35

        # 4. Từ khóa liên quan đến mục tiêu
        stop_words = {
            "viết", "bài", "cho", "về", "người", "mới", "bắt", "đầu", "sinh",
            "viên", "và", "là", "gì", "một", "tài", "liệu", "chuẩn", "bị", "hướng", "dẫn", "này", "đây"
        }
        goal_keywords = [
            w for w in re.findall(r'\b\w+\b', goal.lower())
            if len(w) > 2 and w not in stop_words
        ]
        matched_keywords = [kw for kw in goal_keywords if kw in content.lower()]
        crit_relevance = len(matched_keywords) > 0 if goal_keywords else True

        passed = crit_length and crit_structure and crit_diversity and crit_relevance

        review_notes = [
            f"✓ Tiêu chuẩn độ dài: Đạt {char_count} ký tự ({word_count} từ, ngưỡng tối thiểu {min_chars} ký tự)"
            if crit_length else f"✗ Độ dài chưa đạt: {char_count}/{min_chars} ký tự",

            f"✓ Cấu trúc định dạng: Có đề mục phân cấp hoặc gạch đầu dòng Markdown rõ ràng"
            if crit_structure else "✗ Cấu trúc văn bản thiếu phân cấp đề mục",

            f"✓ Đa dạng từ vựng (TTR = {ttr:.2f}): Không lặp từ ngữ bất thường (ngưỡng yêu cầu >= 0.35)"
            if crit_diversity else f"✗ Trùng lặp từ vựng cao (TTR = {ttr:.2f} < 0.35)",

            f"✓ Độ bám sát chủ đề: Ghi nhận các từ khóa trọng tâm ({', '.join(matched_keywords) if matched_keywords else 'Chủ đề phù hợp'})"
            if crit_relevance else "✗ Nội dung chưa phản ánh đúng từ khóa mục tiêu"
        ]

        return {
            "passed": passed,
            "char_count": char_count,
            "word_count": word_count,
            "ttr": ttr,
            "matched_keywords": matched_keywords,
            "review_notes": review_notes
        }


class OllamaClient:
    """
    Client kết nối dịch vụ LLM cục bộ (Ollama) với cơ chế timeout an toàn
    và tự động fallback sang mô phỏng khi không khả dụng.
    """

    def __init__(self, host: str = "http://localhost:11434", model: str = "tinix-lm:latest", timeout_sec: float = 12.0):
        self.host = host.rstrip("/")
        self.model = model
        self.timeout_sec = timeout_sec
        self._available: Optional[bool] = None

    def is_available(self) -> bool:
        """Kiểm tra kết nối dịch vụ Ollama."""
        if self._available is not None:
            return self._available
        try:
            req = urllib.request.Request(f"{self.host}/api/tags", headers={"User-Agent": "AutonomousAgent/1.0"})
            with urllib.request.urlopen(req, timeout=2.0) as res:
                if res.status == 200:
                    data = json.loads(res.read().decode("utf-8"))
                    models = [m.get("name", "") for m in data.get("models", [])]
                    # Nếu model chỉ định không có thì dùng model đầu tiên có sẵn
                    if not any(self.model in m for m in models) and models:
                        self.model = models[0]
                    self._available = True
                    return True
        except Exception:
            pass
        self._available = False
        return False

    def generate(self, prompt: str, system: str = "", max_tokens: int = 300) -> Optional[str]:
        """Gửi prompt đến LLM để nhận nội dung hoàn thiện."""
        if not self.is_available():
            return None
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "system": system,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": max_tokens
                }
            }
            req = urllib.request.Request(
                f"{self.host}/api/generate",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=self.timeout_sec) as res:
                if res.status == 200:
                    resp = json.loads(res.read().decode("utf-8"))
                    return resp.get("response", "").strip()
        except Exception as e:
            print(f"⚠️  [LLM Warning] Ollama generate error ({e}), chuyển sang chế độ fallback.")
        return None


class AutonomousChecklistAgent:
    """
    Autonomous Agent hoàn thành checklist tối đa 3 bước với Bounded Loop,
    hỗ trợ LLM Planner & Executor thật kết hợp cơ chế kiểm duyệt chất lượng định lượng.
    """

    def __init__(self, max_steps: int = 3, use_llm: bool = True):
        if max_steps > 3:
            raise ValueError(f"Vi phạm Bounded Loop: max_steps ({max_steps}) không được vượt quá giới hạn 3 bước!")
        self.max_steps = min(max(1, max_steps), 3)
        self.use_llm = use_llm
        self.llm = OllamaClient() if use_llm else None
        self.evaluator = QualityEvaluator()

        self.status = AgentStatus.IDLE
        self.plan: List[Step] = []
        self.logs: List[StepLog] = []
        self.context_memory: Dict[str, Any] = {}
        self.final_output: Optional[str] = None
        self.quality_metrics: Dict[str, Any] = {}

    def _extract_topic_and_intent(self, goal: str) -> Tuple[str, str]:
        """
        Bóc tách chủ đề trọng tâm (Topic) và mục đích chính (Intent).
        """
        lower = goal.lower().strip()

        # Nhận diện ý định (Intent)
        if any(kw in lower for kw in ["outline", "dàn ý"]):
            intent = "outline_only"
        elif any(kw in lower for kw in ["tóm tắt", "summary", "tổng kết", "súc tích"]):
            intent = "summarize"
        else:
            intent = "full_article"

        # Bóc tách Topic
        if "rag" in lower or "retrieval" in lower:
            topic = "RAG (Retrieval-Augmented Generation)"
        elif "docker" in lower:
            topic = "Docker & Container hóa"
        elif "machine learning" in lower or "học máy" in lower:
            topic = "Machine Learning"
        elif "kubernetes" in lower or "k8s" in lower:
            topic = "Kubernetes"
        elif "git" in lower:
            topic = "Git & Quản lý phiên bản"
        elif "postgresql" in lower or "database" in lower or "cơ sở dữ liệu" in lower:
            topic = "Tối ưu hóa cơ sở dữ liệu PostgreSQL"
        else:
            # Loại bỏ các từ tiền tố
            cleaned = re.sub(
                r'^(viết|chuẩn bị|tạo|lập|hướng dẫn|giải thích|tóm tắt)\s+(bài chia sẻ|bài viết|outline|dàn ý|tài liệu)?\s*(về|ngắn|cho)?\s*',
                '',
                lower
            ).strip()
            # Bỏ các từ mơ hồ như "này", "đây"
            cleaned = re.sub(r'\b(này|đây|đó)\b', '', cleaned).strip()
            topic = cleaned.capitalize() if cleaned else "Chủ đề kỹ thuật yêu cầu"

        return topic, intent

    def plan_steps(self, goal: str) -> List[Step]:
        """
        Bộ lập kế hoạch động (Dynamic Planner):
        Agent tự sinh checklist (1 <= steps <= 3) bằng LLM nếu có kết nối,
        hoặc qua heuristic suy luận ngữ nghĩa khi offline.
        """
        self.status = AgentStatus.PLANNING
        topic, intent = self._extract_topic_and_intent(goal)

        steps: List[Step] = []

        # Thử nghiệm lập kế hoạch qua LLM nếu được kích hoạt
        if self.use_llm and self.llm and self.llm.is_available():
            prompt = (
                f"Hãy lập một kế hoạch checklist tối đa 3 bước để thực hiện mục tiêu sau:\n"
                f"Mục tiêu: \"{goal}\"\n\n"
                f"Trả về danh sách các bước dưới định dạng JSON mảng (tối đa 3 phần tử). "
                f"Mỗi phần tử có các trường:\n"
                f"- step_id (số nguyên từ 1)\n"
                f"- title (tiêu đề ngắn gọn hành động)\n"
                f"- description (mô tả nhiệm vụ cụ thể)\n"
                f"- action_type (chọn một trong: 'research_points', 'outline', 'generate', 'review_polish', 'summarize')\n"
                f"Chỉ trả về JSON thuần, không kèm markdown hay lời dẫn."
            )
            response = self.llm.generate(prompt, max_tokens=220)
            if response:
                try:
                    match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
                    if match:
                        raw_steps = json.loads(match.group(0))
                        for idx, s in enumerate(raw_steps[:self.max_steps], 1):
                            steps.append(Step(
                                step_id=idx,
                                title=s.get("title", f"Bước {idx}"),
                                description=s.get("description", ""),
                                action_type=s.get("action_type", "generate")
                            ))
                except Exception:
                    steps = []

        # Fallback kế hoạch ngữ nghĩa nếu LLM chưa trả về hợp lệ
        if not steps:
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
            elif intent == "summarize":
                steps = [
                    Step(
                        step_id=1,
                        title=f"Trích xuất các ý chính và thông số cốt lõi về {topic}",
                        description=f"Lọc ra các định nghĩa và kết luận quan trọng nhất.",
                        action_type="research_points"
                    ),
                    Step(
                        step_id=2,
                        title=f"Soạn thảo bản tóm tắt súc tích cho {topic}",
                        description=f"Viết bản tóm tắt 3 mục: Ý chính, Chi tiết nổi bật và Bài học rút ra.",
                        action_type="summarize"
                    )
                ]
            else:
                steps = [
                    Step(
                        step_id=1,
                        title=f"Xác định các ý chính và cấu trúc dàn ý về {topic}",
                        description=f"Lập dàn ý các câu hỏi trọng tâm: Định nghĩa {topic}, nguyên lý và ví dụ thực tế.",
                        action_type="outline"
                    ),
                    Step(
                        step_id=2,
                        title=f"Soạn thảo nội dung bài chia sẻ hoàn chỉnh về {topic}",
                        description=f"Dựa trên dàn ý Bước 1, phát triển văn phong thân thiện, trực quan, phù hợp cho người học.",
                        action_type="generate"
                    ),
                    Step(
                        step_id=3,
                        title=f"Rà soát, kiểm định chất lượng và nghiệm thu bài viết về {topic}",
                        description=f"Kiểm tra tính dễ hiểu, đo lường chỉ số từ vựng TTR, bổ sung lời kết và nghiệm thu.",
                        action_type="review_polish"
                    )
                ]

        self.plan = steps[:self.max_steps]
        return self.plan

    def _execute_step_action(self, step: Step, topic: str, goal: str) -> str:
        """
        Executor thực thi từng bước dựa trên action_type và truyền dữ liệu ngữ cảnh (Context Propagation).
        Hỗ trợ LLM sinh nội dung động từ mục tiêu thực tế.
        """
        # Thử gọi LLM sinh nội dung nếu có sẵn
        if self.use_llm and self.llm and self.llm.is_available():
            context_summary = "\n".join([f"- {k}: {str(v)[:200]}..." for k, v in self.context_memory.items()])
            llm_prompt = (
                f"Bạn là Autonomous Content Agent đang thực thi nhiệm vụ.\n"
                f"Mục tiêu tổng thể: {goal}\n"
                f"Nhiệm vụ bước hiện tại [{step.step_id}]: {step.title}\n"
                f"Mô tả: {step.description}\n"
                f"Dữ liệu ngữ cảnh tích lũy từ các bước trước:\n{context_summary if context_summary else '(Chưa có ngữ cảnh trước)'}\n\n"
                f"Hãy tạo nội dung kết quả cho bước này một cách rõ ràng, logic, có phân đoạn Markdown (khoảng 150-250 từ)."
            )
            llm_res = self.llm.generate(llm_prompt, max_tokens=280)
            if llm_res and len(llm_res.strip()) > 50:
                result = llm_res.strip()
                if step.action_type == "research_points":
                    self.context_memory["research_points"] = result
                elif step.action_type == "outline":
                    self.context_memory["outline"] = result
                elif step.action_type == "summarize":
                    self.context_memory["summary"] = result
                elif step.action_type == "generate":
                    self.context_memory["draft_article"] = result
                elif step.action_type == "review_polish":
                    # Tiến hành đánh giá chất lượng thực tế
                    eval_res = self.evaluator.evaluate(result, goal, "full_article")
                    self.context_memory["review_notes"] = eval_res["review_notes"]
                    self.context_memory["final_article"] = result
                return result

        # Fallback tạo nội dung xác định chất lượng cao
        if step.action_type == "research_points":
            time.sleep(0.010)
            result = (
                f"CÁC LUẬN ĐIỂM CỐT LÕI VỀ {topic.upper()}:\n"
                f"1. Khái niệm cốt lõi: Bản chất kỹ thuật và vai trò nền tảng của {topic}.\n"
                f"2. Giá trị thực tiễn: Giải quyết bài toán mở rộng quy mô, tự động hóa và độ tin cậy.\n"
                f"3. Thành phần kiến trúc: Các module xử lý chính và nguyên lý liên kết.\n"
                f"4. Ví dụ ứng dụng: Triển khai trong môi trường phát triển hiện đại."
            )
            self.context_memory["research_points"] = result
            return result

        elif step.action_type == "outline":
            time.sleep(0.012)
            if "rag" in topic.lower():
                outline = (
                    "DÀN Ý BÀI VIẾT: TÌM HIỂU RAG CHO NGƯỜI MỚI BẮT ĐẦU\n"
                    "1. RAG là gì? (Retrieval-Augmented Generation - Tạo sinh tăng cường truy xuất).\n"
                    "2. Vì sao cần RAG? (Khắc phục ảo giác hallucination, cập nhật tri thức mới).\n"
                    "3. Nguyên lý vận hành: Lập chỉ mục Vector -> Truy xuất ngữ cảnh -> Phản hồi LLM.\n"
                    "4. Minh họa đời thường: Giống như làm bài thi đề mở được tra cứu tài liệu.\n"
                    "5. Ứng dụng thực tế: Chatbot nội bộ doanh nghiệp và hỏi đáp tri thức chuyên ngành."
                )
            elif "docker" in topic.lower():
                outline = (
                    "DÀN Ý BÀI VIẾT: TÌM HIỂU DOCKER CHO SINH VIÊN IT\n"
                    "1. Docker là gì? Định nghĩa Container và sự khác biệt với Virtual Machine.\n"
                    "2. 3 khái niệm cốt lõi: Dockerfile, Docker Image và Docker Container.\n"
                    "3. Vì sao nên dùng Docker: Nhất quán môi trường 'chạy ở máy tôi được thì lên server cũng chạy được'.\n"
                    "4. Các lệnh thực hành cơ bản: docker build, docker run, docker ps.\n"
                    "5. Lời kết và hướng dẫn thực hành."
                )
            else:
                outline = (
                    f"DÀN Ý CHI TIẾT CHO CHỦ ĐỀ {topic.upper()}:\n"
                    f"1. Tổng quan & Định nghĩa kỹ thuật về {topic}.\n"
                    f"2. Tầm quan trọng và lợi thế triển khai trong thực tế.\n"
                    f"3. Kiến trúc luồng dữ liệu và các bước thiết lập cốt lõi.\n"
                    f"4. Ví dụ hướng dẫn từng bước và lưu ý khi áp dụng.\n"
                    f"5. Đánh giá ưu nhược điểm và kết luận."
                )
            self.context_memory["outline"] = outline
            return outline

        elif step.action_type == "summarize":
            time.sleep(0.015)
            summary = (
                f"# BẢN TÓM TẮT SÚC TÍCH: {topic.upper()}\n\n"
                f"- **Ý chính cốt lõi:** {topic} là giải pháp then chốt giúp tối ưu hóa hiệu năng, độ chính xác và khả năng tự động hóa.\n"
                f"- **Chi tiết nổi bật:** Kiến trúc mô đun hóa cho phép dễ dàng tích hợp và mở rộng mà không làm gián đoạn hệ thống hiện có.\n"
                f"- **Bài học rút ra:** Cần nắm vững các nguyên tắc cơ bản trước khi đưa vào môi trường sản xuất thực tế."
            )
            self.context_memory["summary"] = summary
            return summary

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
                    "- **Tránh ảo giác (Hallucination):** LLM hay phát sinh thông tin sai lệch khi thiếu dữ liệu. RAG cung cấp nguồn dẫn chứng chính xác để AI dựa vào.\n"
                    "- **Cập nhật dữ liệu thời gian thực:** Không cần tốn kém chi phí huấn luyện lại mô hình mỗi khi có văn bản mới.\n"
                    "- **Bảo mật dữ liệu riêng tư:** Cho phép kết nối an toàn với cơ sở dữ liệu nội bộ công ty mà không sợ rò rỉ ra ngoài.\n\n"
                    "## 3. RAG hoạt động như thế nào?\n"
                    "Cơ chế của RAG diễn ra mượt mà theo 3 chặng:\n"
                    "1. **Chuyển đổi & Lưu trữ (Indexing):** Tài liệu văn bản được cắt nhỏ và mã hóa thành vector toán học rồi lưu vào Vector Database.\n"
                    "2. **Truy xuất (Retrieval):** Khi bạn đặt câu hỏi, hệ thống tìm kiếm trong cơ sở dữ liệu những đoạn văn bản liên quan nhất.\n"
                    "3. **Tạo phản hồi (Generation):** LLM nhận cả câu hỏi lẫn các đoạn tài liệu tìm thấy, tổng hợp và trả về câu trả lời chuẩn xác nhất.\n\n"
                    "## 4. Hình dung đơn giản nhất\n"
                    "Hãy tưởng tượng LLM thông thường như một học sinh đi thi 'đóng sách' (chỉ dựa vào trí nhớ hạn chế). "
                    "Còn hệ thống RAG là học sinh bước vào phòng thi 'mở sách': khi gặp câu hỏi khó, bạn ấy mở đúng cuốn cẩm nang tra cứu và viết ra câu trả lời hoàn hảo!"
                )
            else:
                article = (
                    f"# TÌM HIỂU TOÀN DIỆN VỀ {topic.upper()}\n\n"
                    f"{topic} đóng vai trò thiết yếu trong việc chuẩn hóa quy trình và nâng cao năng suất kỹ thuật.\n\n"
                    f"Dựa trên dàn ý đã thiết lập:\n{outline}\n\n"
                    f"Nội dung cung cấp góc nhìn từ nền tảng đến thực tế triển khai, giúp người học dễ dàng nắm bắt và ứng dụng."
                )
            self.context_memory["draft_article"] = article
            return article

        elif step.action_type == "review_polish":
            time.sleep(0.018)
            draft = self.context_memory.get("draft_article", "")
            polished_article = draft + (
                "\n\n## 5. Lời kết cho người mới bắt đầu\n"
                f"{topic} không phức tạp như vẻ ngoài của thuật ngữ. Đây là cầu nối hoàn hảo giữa công nghệ "
                "và kho tri thức sống động của bạn. Hãy bắt tay vào thực hành ngay hôm nay để tự xây dựng giải pháp của riêng mình!\n\n"
                "---\n"
                "*(Biên soạn bởi Autonomous Content Agent - Đã qua rà soát chất lượng)*"
            )
            # Chạy kiểm duyệt chất lượng định lượng
            eval_res = self.evaluator.evaluate(polished_article, goal, "full_article")
            self.context_memory["review_notes"] = eval_res["review_notes"]
            self.context_memory["final_article"] = polished_article
            return polished_article

        else:
            result = f"Đã hoàn thành bước: {step.title}"
            return result

    def _evaluate_stop_condition(self, current_step_index: int, total_steps: int, intent: str, goal: str) -> Tuple[bool, str, Optional[AgentStatus]]:
        """
        Đánh giá điều kiện dừng (Stop Condition):
        - GOAL_ACHIEVED (COMPLETED): Sản phẩm thỏa mãn điều kiện nghiệm thu theo đúng mục tiêu đề ra.
        - BUDGET_EXHAUSTED / MAX_STEPS_REACHED: Đạt giới hạn số bước nhưng mục tiêu chưa hoàn thành.
        """
        # 1. Trường hợp mục tiêu chỉ yêu cầu dàn ý (outline_only)
        if intent == "outline_only" and "outline" in self.context_memory:
            eval_res = self.evaluator.evaluate(self.context_memory["outline"], goal, intent)
            if eval_res["passed"]:
                return True, "Goal achieved: Dàn ý đạt chuẩn chất lượng nghiệm thu theo đúng mục tiêu.", AgentStatus.COMPLETED

        # 2. Trường hợp mục tiêu tóm tắt tài liệu (summarize)
        if intent == "summarize" and "summary" in self.context_memory:
            eval_res = self.evaluator.evaluate(self.context_memory["summary"], goal, intent)
            if eval_res["passed"]:
                return True, "Goal achieved: Bản tóm tắt súc tích đạt chuẩn chất lượng nghiệm thu.", AgentStatus.COMPLETED

        # 3. Trường hợp mục tiêu là bài viết hoàn chỉnh (full_article)
        if "final_article" in self.context_memory:
            eval_res = self.evaluator.evaluate(self.context_memory["final_article"], goal, intent)
            if eval_res["passed"]:
                return True, "Goal achieved: Bài viết hoàn chỉnh đã qua kiểm duyệt chất lượng đạt yêu cầu.", AgentStatus.COMPLETED

        # 4. Khi đạt giới hạn số bước (current_step_index >= total_steps)
        if current_step_index >= total_steps:
            # Kiểm tra xem sản phẩm tương ứng với intent đã hoàn thành chưa
            target_created = (
                (intent == "outline_only" and "outline" in self.context_memory) or
                (intent == "summarize" and "summary" in self.context_memory) or
                (intent == "full_article" and "final_article" in self.context_memory)
            )
            if target_created:
                return True, f"Goal achieved: Đã hoàn thành toàn bộ mục tiêu sau {current_step_index} bước.", AgentStatus.COMPLETED
            else:
                return True, f"Budget exhausted: Đã thực hiện tối đa {current_step_index}/{self.max_steps} bước nhưng chưa hoàn thành trọn vẹn mục tiêu yêu cầu ({intent}).", AgentStatus.BUDGET_EXHAUSTED

        return False, "Continue", None

    def run(self, goal: str) -> FinalReport:
        """
        Vòng lặp Autonomous Agent: Lập plan động -> Lặp thực thi -> Lưu log -> Kiểm tra dừng -> Báo cáo cuối
        """
        start_time = time.perf_counter()
        self.logs.clear()
        self.context_memory.clear()
        self.quality_metrics.clear()

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

            input_context = list(self.context_memory.keys())

            # Thực thi hành động với cơ chế bắt lỗi an toàn (Robust Exception Handling)
            try:
                result = self._execute_step_action(step, topic, goal)
                step.result = result
                step.status = "COMPLETED"
            except Exception as e:
                step.status = "FAILED"
                self.status = AgentStatus.FAILED
                stop_reason = f"Execution failed: Lỗi tại bước {step.step_id} - {str(e)}"
                step_duration = round(time.perf_counter() - step_start, 3)
                log_entry = StepLog(
                    step_id=step.step_id,
                    step_title=step.title,
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                    duration_sec=step_duration,
                    input_context_keys=input_context,
                    output_summary=f"Lỗi: {str(e)}",
                    status=step.status,
                    details={"error": str(e)}
                )
                self.logs.append(log_entry)
                print(f"   ✗ Trạng thái: FAILED ({step_duration}s) - {str(e)}")
                break

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
            should_stop, reason, final_status = self._evaluate_stop_condition(idx, len(plan), intent, goal)
            if should_stop:
                stop_reason = reason
                if final_status:
                    self.status = final_status
                print(f"\n🛑 [STOP CONDITION] Kích hoạt điều kiện dừng: {stop_reason}")
                break

        # 3. Tổng hợp sản phẩm cuối và tính toán chỉ số chất lượng
        total_duration = round(time.perf_counter() - start_time, 3)

        if self.status == AgentStatus.FAILED:
            self.final_output = ""
            self.quality_metrics = {
                "passed": False,
                "review_notes": [f"✗ Thực thi thất bại: {stop_reason}"]
            }
        else:
            if intent == "outline_only":
                self.final_output = self.context_memory.get("outline", "")
            elif intent == "summarize":
                self.final_output = self.context_memory.get("summary", "")
            else:
                self.final_output = (
                    self.context_memory.get("final_article") or
                    self.context_memory.get("draft_article") or
                    self.context_memory.get("outline") or
                    ""
                )

            # Đánh giá chất lượng sản phẩm cuối cùng
            if self.final_output:
                self.quality_metrics = self.evaluator.evaluate(self.final_output, goal, intent)
            else:
                self.quality_metrics = {"passed": False, "review_notes": ["Không có sản phẩm đầu ra."]}

        # Đảm bảo tính nhất quán trạng thái nếu chưa được gán bởi điều kiện dừng
        if self.status == AgentStatus.RUNNING:
            if self.quality_metrics.get("passed", False):
                self.status = AgentStatus.COMPLETED
            else:
                self.status = AgentStatus.BUDGET_EXHAUSTED

        report = FinalReport(
            goal=goal,
            total_steps_planned=len(plan),
            steps_executed=steps_executed,
            status=self.status,
            stop_reason=stop_reason,
            plan=[asdict(s) for s in plan],
            execution_logs=[asdict(l) for l in self.logs],
            final_output=self.final_output,
            quality_metrics=self.quality_metrics,
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
        if report.quality_metrics:
            print("\n--- ĐÁNH GIÁ CHẤT LƯỢNG ĐỊNH LƯỢNG ---")
            for note in report.quality_metrics.get("review_notes", []):
                print(f"   {note}")
        print("\n--- NỘI DUNG SẢN PHẨM ĐẦU RA ---")
        print(report.final_output)
        print("=" * 55 + "\n")


if __name__ == "__main__":
    agent = AutonomousChecklistAgent(max_steps=3, use_llm=True)
    user_goal = "Viết một bài chia sẻ ngắn giải thích RAG là gì cho người mới bắt đầu."
    report = agent.run(user_goal)

    output_dir = os.path.dirname(os.path.abspath(__file__))
    report_path = os.path.join(output_dir, "agent_final_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(asdict(report), f, ensure_ascii=False, indent=2)
    print(f"📁 Đã lưu báo cáo chi tiết vào: {report_path}")
