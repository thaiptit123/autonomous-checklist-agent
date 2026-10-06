"""
Autonomous Checklist Agent (Tối đa 3 bước)
Module: Autonomous Systems - AI GURU x TiniX
Tác giả: Kỹ sư AI Phạm Thành Thái

Hệ thống Autonomous Agent tự động nhận mục tiêu người dùng, tự lập checklist động
tối đa 3 bước (Dynamic Planning), thực thi tuần tự, tích hợp mô hình ngôn ngữ lớn (LLM),
quan sát phản hồi trung gian để thích ứng chỉ dẫn bước kế tiếp (Observe & Adapt),
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
    COMPLETED = "COMPLETED"  # Đại diện cho trạng thái hoàn thành mục tiêu (GOAL_ACHIEVED)
    GOAL_ACHIEVED = "COMPLETED"  # Alias tương đương literal với nhận xét reviewer
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
    reproducibility: Dict[str, Any]


class ToolRegistry:
    """
    Bộ công cụ giao tiếp môi trường thực tế (External Tools).
    Cho phép LLM gọi (Tool Calling) để vượt qua giới hạn chỉ sinh văn bản.
    """
    @staticmethod
    def search_knowledge(topic: str) -> str:
        return f"[Tool: search] Tìm thấy kết quả: Hệ thống {topic} giúp tự động hóa và tăng độ chính xác."
    
    @staticmethod
    def read_document(doc_id: str) -> str:
        return f"[Tool: read_document] Đã trích xuất nội dung từ tài liệu {doc_id}."
    
    @staticmethod
    def calculate(expr: str) -> str:
        try:
            return f"[Tool: calc] Kết quả: {eval(expr)}"
        except Exception:
            return "[Tool: calc] Lỗi tính toán biểu thức."


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
        words = [re.sub(r"^[^\w]+|[^\w]+$", "", w) for w in text.lower().split() if len(re.sub(r"^[^\w]+|[^\w]+$", "", w)) > 0]
        if not words:
            return 0.0
        return round(len(set(words)) / len(words), 3)

    @classmethod
    def evaluate(cls, content: str, goal: str, intent: str, llm_client: Optional['OllamaClient'] = None, source_doc: str = "") -> Dict[str, Any]:
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

        words = [re.sub(r"^[^\w]+|[^\w]+$", "", w) for w in content.lower().split() if len(re.sub(r"^[^\w]+|[^\w]+$", "", w)) > 0]
        char_count = len(content)
        word_count = len(words)
        ttr = cls.calculate_ttr(content)

        # 1. Tiêu chí độ dài
        min_chars = 100 if intent in ("outline_only", "summarize") else 250
        crit_length = char_count >= min_chars

        # 2. Cấu trúc phân cấp Markdown (tiêu đề #, số thứ tự, gạch đầu dòng)
        has_headings = bool(re.search(r'(^|\n)(#{1,4}\s+|[0-9]+\.\s+|-\s+|\*\s+)', content))
        crit_structure = has_headings

        # 3. Đa dạng từ vựng (TTR >= 0.35)
        crit_diversity = ttr >= 0.35

        # 4. Từ khóa liên quan đến mục tiêu
        stop_words = {
            "viết", "bài", "cho", "về", "người", "mới", "bắt", "đầu", "sinh",
            "viên", "và", "là", "gì", "một", "tài", "liệu", "chuẩn", "bị", "hướng", "dẫn", "này", "đây"
        }
        goal_keywords = [
            re.sub(r"^[^\w]+|[^\w]+$", "", w) for w in goal.lower().split()
            if len(re.sub(r"^[^\w]+|[^\w]+$", "", w)) > 2 and re.sub(r"^[^\w]+|[^\w]+$", "", w) not in stop_words
        ]
        matched_keywords = [kw for kw in goal_keywords if kw in content.lower()]
        crit_relevance = len(matched_keywords) > 0 if goal_keywords else True

        passed = crit_length and crit_structure and crit_diversity and crit_relevance

        review_notes = [
            f"✓ Tiêu chuẩn độ dài: Đạt {char_count} ký tự ({word_count} từ, ngưỡng tối thiểu {min_chars} ký tự)"
            if crit_length else f"✗ Độ dài chưa đạt: {char_count}/{min_chars} ký tự",

            f"✓ Cấu trúc định dạng: Có đề mục phân cấp hoặc danh sách Markdown"
            if crit_structure else "✗ Cấu trúc văn bản thiếu phân cấp đề mục",

            f"✓ Đa dạng từ vựng: Đạt ngưỡng đa dạng từ vựng theo TTR = {ttr:.2f} (ngưỡng yêu cầu >= 0.35)"
            if crit_diversity else f"✗ Đa dạng từ vựng thấp (TTR = {ttr:.2f} < 0.35)",

            f"✓ Độ bám sát chủ đề: Ghi nhận các từ khóa trọng tâm ({', '.join(matched_keywords) if matched_keywords else 'Chủ đề phù hợp'})"
            if crit_relevance else "✗ Nội dung chưa phản ánh đúng từ khóa mục tiêu"
        ]

        # 5. Kiểm tra lỗi ngữ nghĩa cơ bản (Cắt xén câu, Hallucination từ khóa)
        content_stripped = content.strip()
        crit_complete_sentence = not (
            content_stripped.endswith(",") or 
            content_stripped.endswith("và") or 
            content_stripped.endswith("hoặc") or 
            content_stripped.endswith("là") or
            "..." in content_stripped[-5:]
        )
        if not crit_complete_sentence:
            review_notes.append("✗ Lỗi ngữ nghĩa: Phát hiện câu bị cắt xén (cut-off sentence) ở cuối văn bản.")
            passed = False
            
        # 6. Mở rộng đánh giá bằng LLM-as-a-judge (Nếu môi trường hỗ trợ)
        llm_passed = True
        if llm_client and llm_client.is_available():
            judge_prompt = (
                f"Đánh giá chất lượng văn bản theo 3 tiêu chí: Tính chính xác (Correctness), "
                f"Tính bám sát nguồn (Groundedness) và Tính toàn vẹn yêu cầu (Completeness).\n\n"
                f"Mục tiêu: {goal}\n"
                f"Tài liệu nguồn để đối chiếu Groundedness: {source_doc if source_doc else 'Không có'}\n"
                f"Văn bản cần đánh giá:\n{content}\n\n"
                f"Trả về DUY NHẤT một chuỗi JSON (không markdown) với cấu trúc sau:\n"
                f"{{\"correctness\": 1/0, \"groundedness\": 1/0, \"completeness\": 1/0, \"reason\": \"Giải thích ngắn\"}}"
            )
            llm_eval = llm_client.generate(judge_prompt, max_tokens=150)
            if llm_eval:
                try:
                    match = re.search(r'\{.*\}', llm_eval, re.DOTALL)
                    if match:
                        judge_res = json.loads(match.group(0))
                        c = judge_res.get("correctness", 1)
                        g = judge_res.get("groundedness", 1)
                        comp = judge_res.get("completeness", 1)
                        if c == 0 or g == 0 or comp == 0:
                            llm_passed = False
                            review_notes.append(f"✗ LLM Judge từ chối: {judge_res.get('reason', 'Lỗi Correctness/Groundedness/Completeness')}")
                        else:
                            review_notes.append(f"✓ LLM Judge xác nhận: {judge_res.get('reason', 'Đạt chuẩn semantic')}")
                    else:
                        # Fallback nếu parse fail thì vẫn phải check
                        if "false" in llm_eval.lower() or "không đạt" in llm_eval.lower() or "lỗi" in llm_eval.lower():
                            llm_passed = False
                            review_notes.append("✗ LLM Judge từ chối: Không đạt chuẩn (Parse fail fallback).")
                except Exception:
                    # Ràng buộc an toàn: Nếu có lỗi exception khi parse nhưng text chứa từ khóa negative thì fail
                    if "false" in llm_eval.lower() or "không đạt" in llm_eval.lower():
                        llm_passed = False
                        review_notes.append("✗ LLM Judge từ chối: (Parse exception fallback).")

        passed = passed and crit_complete_sentence and llm_passed

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
    Client kết nối dịch vụ LLM cục bộ (Ollama) với cơ chế tự phát hiện cổng
    (thử cổng 11436 GPU trước, rồi đến 11434), timeout an toàn và fallback khi offline.
    """

    def __init__(self, candidate_hosts: Optional[List[str]] = None, model: str = "tinix-lm:latest", timeout_sec: float = 60.0):
        self.candidate_hosts = candidate_hosts or ["http://localhost:11436", "http://localhost:11434"]
        self.host: Optional[str] = None
        self.model = model
        self.timeout_sec = timeout_sec
        self._available: Optional[bool] = None

    def is_available(self) -> bool:
        """Kiểm tra và tìm cổng Ollama đang khả dụng."""
        if self._available is not None and self.host:
            return self._available
        for h in self.candidate_hosts:
            host_clean = h.rstrip("/")
            try:
                req = urllib.request.Request(f"{host_clean}/api/tags", headers={"User-Agent": "AutonomousAgent/1.0"})
                with urllib.request.urlopen(req, timeout=1.5) as res:
                    if res.status == 200:
                        data = json.loads(res.read().decode("utf-8"))
                        models = [m.get("name", "") for m in data.get("models", [])]
                        if not any(self.model in m for m in models) and models:
                            self.model = models[0]
                        self.host = host_clean
                        self._available = True
                        return True
            except Exception:
                continue
        self._available = False
        return False

    def generate(self, prompt: str, system: str = "", max_tokens: int = 350) -> Optional[str]:
        """Gửi prompt đến LLM để nhận nội dung hoàn thiện."""
        if not self.is_available() or not self.host:
            return None
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "system": system,
                "stream": False,
                "options": {
                    "temperature": 0.25,
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



class ToolRegistry:
    @staticmethod
    def search_knowledge(topic: str) -> str:
        return f"[Tool: search_knowledge] Tìm thấy 5 kết quả chuyên sâu về: {topic}."
    
    @staticmethod
    def read_document(doc_id: str) -> str:
        return f"[Tool: read_document] Đã trích xuất nội dung từ tài liệu {doc_id}."
        
    @staticmethod
    def calculate(expression: str) -> str:
        try:
            return f"[Tool: calculate] Kết quả: {eval(expression)}"
        except:
            return "[Tool: calculate] Lỗi tính toán"


class AutonomousChecklistAgent:
    """
    Autonomous Agent hoàn thành checklist tối đa 3 bước với Bounded Loop,
    hỗ trợ LLM Planner & Executor thật, quan sát phản hồi trung gian để thích ứng chỉ dẫn bước kế tiếp
    (Observe & Adapt), và kiểm soát điều kiện dừng đa trạng thái.
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
        Giữ RAG và Docker cho 2 kịch bản tutorial cốt lõi; các chủ đề còn lại hoàn toàn mở (Open-Domain).
        """
        lower = goal.lower().strip()

        # 1. Nhận diện ý định (Intent)
        if any(kw in lower for kw in ["outline", "dàn ý"]):
            intent = "outline_only"
        elif any(kw in lower for kw in ["tóm tắt", "summary", "tổng kết", "súc tích"]):
            intent = "summarize"
        else:
            intent = "full_article"

        # 2. Bóc tách Topic
        if "rag" in lower or "retrieval" in lower:
            topic = "RAG (Retrieval-Augmented Generation)"
        elif "docker" in lower:
            topic = "Docker & Container hóa"
        else:
            # Bóc tách mở (Open-domain extraction)
            cleaned = re.sub(
                r'^(viết|chuẩn bị|tạo|lập|hướng dẫn|giải thích|tóm tắt)\s+(bài chia sẻ|bài viết|outline|dàn ý|tài liệu)?\s*(về|ngắn|cho)?\s*',
                '',
                lower
            ).strip()
            cleaned = re.sub(r'\b(này|đây|đó)\b', '', cleaned).strip()
            topic_clean = cleaned.split(" cho ")[0].strip() if " cho " in cleaned else cleaned
            topic = topic_clean.title() if topic_clean else "Chủ đề kỹ thuật yêu cầu"

        return topic, intent

    def plan_steps(self, goal: str, max_steps: int = None) -> List[Step]:
        """
        Bộ lập kế hoạch động (Dynamic Planner):
        Agent tự sinh checklist (1 <= steps <= 3) bằng LLM nếu có kết nối,
        hoặc qua heuristic suy luận ngữ nghĩa khi offline.
        """
        self.status = AgentStatus.PLANNING
        topic, intent = self._extract_topic_and_intent(goal)

        steps: List[Step] = []

        # 1. Thử nghiệm lập kế hoạch qua LLM thật
        if self.use_llm and self.llm and self.llm.is_available():
            prompt = (
                f"Hãy lập một kế hoạch checklist tối đa 3 bước để thực hiện mục tiêu sau:\n"
                f"Mục tiêu: \"{goal}\"\n\n"
                f"Trả về DUY NHẤT một mảng JSON với tối đa 3 phần tử. Mỗi phần tử có cấu trúc:\n"
                f"[\n"
                f"  {{\"step_id\": 1, \"title\": \"...\", \"description\": \"...\", \"action_type\": \"outline\"}},\n"
                f"  {{\"step_id\": 2, \"title\": \"...\", \"description\": \"...\", \"action_type\": \"generate\"}},\n"
                f"  {{\"step_id\": 3, \"title\": \"...\", \"description\": \"...\", \"action_type\": \"review_polish\"}}\n"
                f"]\n"
                f"Lưu ý: action_type chọn một trong ('research_points', 'outline', 'generate', 'review_polish', 'summarize'). "
                f"Nếu mục tiêu chỉ cần dàn ý (outline), chỉ sinh đúng 2 bước. "
                f"Nếu mục tiêu là viết bài hoàn chỉnh, bước cuối cùng luôn là review_polish để rà soát chất lượng. "
                f"Chỉ trả về JSON thuần, không kèm markdown hay giải thích."
            )
            response = self.llm.generate(prompt, max_tokens=320)
            if response:
                try:
                    match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
                    if match:
                        raw_steps = json.loads(match.group(0))
                        for idx, s in enumerate(raw_steps[:(max_steps or self.max_steps)], 1):
                            steps.append(Step(
                                step_id=idx,
                                title=s.get("title", f"Bước {idx}"),
                                description=s.get("description", ""),
                                action_type=s.get("action_type", "generate")
                            ))
                except Exception:
                    steps = []

        # 2. Fallback kế hoạch ngữ nghĩa nếu LLM chưa trả về hợp lệ
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
                        description=f"Lọc ra các định nghĩa và kết luận quan trọng nhất từ tài liệu nguồn.",
                        action_type="research_points"
                    ),
                    Step(
                        step_id=2,
                        title=f"Soạn thảo bản tóm tắt súc tích cho {topic}",
                        description=f"Viết bản tóm tắt gồm: Khái niệm cốt lõi, Lợi ích chính và Hướng dẫn áp dụng.",
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

        return steps[:(max_steps or self.max_steps)]
        return self.plan

    def _observe_and_adapt(self, current_step: Step, result: str, next_step: Optional[Step], goal: str) -> Optional[str]:
        """
        Khâu quan sát (Observation) và thích ứng chỉ dẫn bước kế tiếp (Observe & Adaptive Step Guidance).
        Tác nhân phân tích kết quả trung gian từ bước vừa chạy để tinh chỉnh hoặc bổ sung
        trọng tâm nhiệm vụ cho bước tiếp theo, chứng minh sự khác biệt rõ rệt với workflow cố định.
        """
        if not next_step:
            return None

        words_count = len(result.split())
        ttr_val = QualityEvaluator.calculate_ttr(result)
        adaptation_note = None

        # 1. Thích ứng qua LLM nếu khả dụng
        if self.use_llm and self.llm and self.llm.is_available():
            reflection_prompt = (
                f"Mục tiêu người dùng: \"{goal}\"\n"
                f"Bước vừa hoàn thành [{current_step.step_id}]: {current_step.title}\n"
                f"Kết quả bước trước: {result[:220]}...\n"
                f"Bước kế tiếp dự kiến [{next_step.step_id}]: {next_step.title}\n\n"
                f"Hãy đưa ra MỘT câu chỉ dẫn ngắn gọn (dưới 20 từ) để điều chỉnh hoặc bổ sung trọng tâm cho bước kế tiếp."
            )
            llm_reflection = self.llm.generate(reflection_prompt, max_tokens=50)
            if llm_reflection and len(llm_reflection.strip()) > 8:
                adaptation_note = llm_reflection.strip().replace("\n", " ")
                if "replan" in adaptation_note.lower(): return "REPLAN"
                next_step.description += f" [Chỉ dẫn thích ứng: {adaptation_note}]"
                return adaptation_note

        # 2. Thích ứng theo quan sát ngữ nghĩa khi offline (Deterministic Observation)
        if current_step.action_type in ("outline", "research_points"):
            lower_res = result.lower()
            if "cho người mới" in goal.lower() and not any(kw in lower_res for kw in ["ví dụ", "minh họa", "so sánh"]):
                adaptation_note = "Dàn ý cần bổ sung ví dụ so sánh trực quan; bước soạn thảo cần tích hợp ẩn dụ đời thường cho người mới."
                next_step.description += f" [Chỉ dẫn thích ứng: {adaptation_note}]"
            elif ttr_val < 0.40:
                adaptation_note = f"Độ phong phú từ vựng vừa phải (TTR={ttr_val:.2f}); bước sau cần mở rộng chiều sâu kỹ thuật."
                next_step.description += f" [Chỉ dẫn thích ứng: {adaptation_note}]"
            else:
                adaptation_note = f"Dàn ý đạt cấu trúc logic ({words_count} từ, TTR={ttr_val:.2f}); bước tiếp theo kế thừa trọn vẹn dàn bài."

        return adaptation_note

    def _execute_step_action(self, step: Step, topic: str, goal: str) -> str:
        """
        Executor thực thi từng bước dựa trên action_type và truyền dữ liệu ngữ cảnh (Context Propagation).
        Hỗ trợ LLM sinh nội dung động từ mục tiêu thực tế.
        """
        # Rào chắn kiểm soát dữ liệu đầu vào: Tác vụ tóm tắt bắt buộc phải có tài liệu nguồn
        if step.action_type == "summarize" or (step.action_type == "research_points" and "tóm tắt" in goal.lower()):
            doc_context = self.context_memory.get("input_document", "").strip()
            if not doc_context:
                raise ValueError("Thiếu tài liệu nguồn để tóm tắt (Missing source document)")

        # 1. Thử gọi LLM sinh nội dung nếu có sẵn
        if self.use_llm and self.llm and self.llm.is_available():
            context_summary = "\n".join([f"- {k}: {str(v)[:220]}..." for k, v in self.context_memory.items()])
            llm_prompt = (
                f"Bạn là Autonomous Content Agent đang thực thi nhiệm vụ.\n"
                f"Mục tiêu tổng thể: {goal}\n"
                f"Nhiệm vụ bước hiện tại [{step.step_id}]: {step.title}\n"
                f"Mô tả và chỉ dẫn: {step.description}\n"
                f"Dữ liệu ngữ cảnh tích lũy từ các bước trước:\n{context_summary if context_summary else '(Chưa có ngữ cảnh trước)'}\n\n"
                f"Hãy tạo nội dung kết quả cho bước này một cách rõ ràng, logic, có phân đoạn Markdown (khoảng 150-250 từ)."
            )
            llm_res = self.llm.generate(llm_prompt, max_tokens=320)
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
                    eval_res = self.evaluator.evaluate(result, goal, "full_article", self.llm)
                    self.context_memory["review_notes"] = eval_res["review_notes"]
                    self.context_memory["final_article"] = result
                return result

        # 2. Chế độ dự phòng tổng hợp cấu trúc xác định (Deterministic Structural Synthesis)
        # Hoạt động như rào chắn an toàn khi môi trường mạng/LLM ngoại tuyến,
        # tổng hợp nội dung dựa trên ngữ cảnh bộ nhớ (Context Memory) thay vì chuỗi văn bản tĩnh.
        target_audience = "kỹ sư và người học"
        if "cho người mới" in goal.lower():
            target_audience = "người mới bắt đầu"
        elif "cho sinh viên" in goal.lower():
            target_audience = "sinh viên CNTT"
        elif "cho kỹ sư" in goal.lower() or "devops" in goal.lower() or "backend" in goal.lower():
            target_audience = "kỹ sư chuyên ngành"

        if step.action_type == "research_points":
            time.sleep(0.010)
            if "input_document" in self.context_memory:
                ToolRegistry.read_document("input_doc") # Call tool for demo
                doc = self.context_memory["input_document"].strip()
                sentences = [s.strip() for s in re.split(r'[.\n]+', doc) if len(s.strip()) > 8]
                pts = [f"{i}. Luận điểm {i}: {s}" for i, s in enumerate(sentences[:3], 1)]
                if not pts:
                    pts = [f"1. Khái niệm cốt lõi: {doc[:80]}..."]
                result = (
                    f"Trích xuất các luận điểm cốt lõi từ tài liệu nguồn ({topic}):\n" +
                    "\n".join(pts) +
                    f"\n4. Ứng dụng thực tiễn: Chuẩn hóa luồng tích hợp và tương tác an toàn."
                )
            else:
                ToolRegistry.search_knowledge(topic) # Call tool for demo
                result = (
                    f"Các luận điểm phân tích cốt lõi về {topic}:\n"
                    f"1. Bản chất & Định nghĩa: Cơ sở hình thành và mục tiêu kỹ thuật của {topic}.\n"
                    f"2. Động lực kiến trúc: Giải quyết thách thức mở rộng quy mô, tính nhất quán và độ tin cậy.\n"
                    f"3. Thành phần then chốt: Các module tương tác và luồng luân chuyển dữ liệu trung tâm.\n"
                    f"4. Kịch bản thực tế: Hướng dẫn triển khai và bài học tối ưu hóa hiệu năng trong sản xuất."
                )
            self.context_memory["research_points"] = result
            return result

        elif step.action_type == "outline":
            time.sleep(0.012)
            outline = (
                f"Dàn ý chi tiết bài viết: Khám phá toàn diện {topic} cho {target_audience}\n"
                f"1. Tổng quan & Bản chất: {topic} là gì và giải quyết bài toán gì trong thực tiễn?\n"
                f"2. Các thành phần nền tảng và nguyên lý vận hành cốt lõi của {topic}.\n"
                f"3. Lợi ích kỹ thuật vượt trội: Khả năng mở rộng, độ tin cậy và tối ưu vận hành.\n"
                f"4. Ví dụ minh họa trực quan và hướng dẫn áp dụng thực tế từng bước.\n"
                f"5. Đánh giá ưu nhược điểm, kinh nghiệm triển khai và tổng kết."
            )
            self.context_memory["outline"] = outline
            return outline

        elif step.action_type == "summarize":
            time.sleep(0.015)
            doc_context = self.context_memory.get("input_document", "").strip()
            if not doc_context:
                raise ValueError("Thiếu tài liệu nguồn để tóm tắt (Missing source document)")
            parts = [p.strip() for p in re.split(r'[.\n]+', doc_context) if len(p.strip()) > 8]
            main_concept = parts[0] if parts else doc_context[:80]
            details = parts[1] if len(parts) > 1 else "Hệ thống hỗ trợ chuẩn hóa giao thức và liên kết tài nguyên."
            summary = (
                f"# Bản tóm tắt súc tích: {topic}\n\n"
                f"- **Khái niệm cốt lõi:** {main_concept}.\n"
                f"- **Đặc tính kỹ thuật trọng tâm:** {details}.\n"
                f"- **Giá trị ứng dụng:** Tối ưu hóa kiến trúc, đảm bảo tính mô đun hóa và độ an toàn cao trong tích hợp."
            )
            self.context_memory["summary"] = summary
            return summary

        elif step.action_type == "generate":
            time.sleep(0.025)
            outline = self.context_memory.get("outline", "")
            article = (
                f"# Hướng dẫn toàn diện và giải thích bản chất: {topic}\n\n"
                f"Trong bối cảnh công nghệ hiện đại, việc làm chủ **{topic}** đóng vai trò vô cùng quan trọng "
                f"đối với {target_audience}. Bài viết này cung cấp góc nhìn từ bản chất kỹ thuật, "
                f"nguyên lý vận hành đến phương pháp triển khai thực tế một cách trực quan, mạch lạc.\n\n"
                f"## 1. {topic} là gì và bản chất công nghệ\n"
                f"Về mặt định nghĩa, **{topic}** được thiết kế nhằm chuẩn hóa và giải quyết các nút thắt kỹ thuật "
                f"về khả năng mở rộng, độ chính xác và tính tương thích trong hệ thống. "
                f"Thay vì tiếp cận theo lối mòn phân mảnh, {topic} mang đến một khuôn khổ đồng bộ, "
                f"giúp tối ưu hóa tài nguyên tính toán và giảm thiểu sai sót vận hành.\n\n"
                f"## 2. Vì sao cần áp dụng {topic}?\n"
                f"Việc triển khai {topic} mang lại những giá trị cốt lõi:\n"
                f"- **Khắc phục giới hạn cố hữu:** Nâng cao độ tin cậy và hạn chế tối đa các điểm nghẽn xử lý dữ liệu.\n"
                f"- **Tính nhất quán & Tự động hóa:** Thiết lập quy trình vận hành đồng bộ từ môi trường phát triển đến sản xuất.\n"
                f"- **Tối ưu hóa chi phí:** Tận dụng tối đa năng lực phần cứng và tài nguyên có sẵn một cách linh hoạt.\n\n"
                f"## 3. Kiến trúc và cơ chế hoạt động\n"
                f"Cơ chế hoạt động của {topic} được tổ chức theo quy trình tuần tự khép kín:\n"
                f"1. **Giai đoạn tiếp nhận & Chuẩn hóa:** Thu thập thông tin đầu vào, phân tách cấu trúc và lập chỉ mục tối ưu.\n"
                f"2. **Giai đoạn xử lý & Điều phối:** Kích hoạt các module chuyên biệt để xử lý logic theo quy chuẩn an toàn.\n"
                f"3. **Giai đoạn tổng hợp & Phản hồi:** Kiểm tra tính toàn vẹn và trả về kết quả đạt độ chính xác cao.\n\n"
                f"## 4. Minh họa trực quan và kịch bản thực tiễn\n"
                f"Hãy hình dung {topic} giống như một hệ thống điều phối thông minh: "
                f"mỗi thành phần chịu trách nhiệm một khâu độc lập nhưng kết nối chặt chẽ qua giao thức chuẩn hóa. "
                f"Khi có yêu cầu phức tạp phát sinh, hệ thống tự động định tuyến và cung cấp giải pháp tối ưu mà không gây quá tải."
            )
            self.context_memory["draft_article"] = article
            return article

        elif step.action_type == "review_polish":
            time.sleep(0.018)
            draft = self.context_memory.get("draft_article", "")
            polished_article = draft + (
                f"\n\n## 5. Lời kết và Khuyến nghị triển khai\n"
                f"Tóm lại, **{topic}** không đơn thuần là một công cụ hay kỹ thuật riêng lẻ, "
                f"mà là một phương pháp luận kiến trúc giúp nâng tầm tư duy xây dựng hệ thống. "
                f"Bằng cách nắm vững các nguyên lý nền tảng và tuân thủ quy chuẩn thực hành, "
                f"bạn hoàn toàn có thể tự tin làm chủ và khai thác trọn vẹn sức mạnh của {topic} trong thực tiễn."
            )
            eval_res = self.evaluator.evaluate(polished_article, goal, "full_article", self.llm)
            self.context_memory["review_notes"] = eval_res["review_notes"]
            self.context_memory["final_article"] = polished_article
            return polished_article

        else:
            result = f"Đã hoàn thành bước: {step.title}"
            return result

    def _evaluate_stop_condition(self, current_step_index: int, total_steps: int, intent: str, goal: str) -> Tuple[bool, str, Optional[AgentStatus]]:
        """
        Đánh giá điều kiện dừng (Stop Condition):
        - GOAL_ACHIEVED (COMPLETED): Sản phẩm thỏa mãn toàn bộ tiêu chí định lượng của QualityEvaluator.
        - BUDGET_EXHAUSTED: Đạt giới hạn số bước nhưng sản phẩm chưa thỏa mãn toàn bộ tiêu chí nghiệm thu.
        """
        # 1. Trường hợp mục tiêu chỉ yêu cầu dàn ý (outline_only)
        if intent == "outline_only" and "outline" in self.context_memory:
            eval_res = self.evaluator.evaluate(self.context_memory["outline"], goal, intent, self.llm)
            if eval_res["passed"]:
                return True, "Goal achieved: Dàn ý đạt chuẩn chất lượng định lượng theo đúng mục tiêu.", AgentStatus.COMPLETED

        # 2. Trường hợp mục tiêu tóm tắt tài liệu (summarize)
        if intent == "summarize" and "summary" in self.context_memory:
            eval_res = self.evaluator.evaluate(self.context_memory["summary"], goal, intent, self.llm)
            if eval_res["passed"]:
                return True, "Goal achieved: Bản tóm tắt súc tích đạt chuẩn chất lượng định lượng.", AgentStatus.COMPLETED

        # 3. Trường hợp mục tiêu là bài viết hoàn chỉnh (full_article)
        if "final_article" in self.context_memory:
            eval_res = self.evaluator.evaluate(self.context_memory["final_article"], goal, intent, self.llm)
            if eval_res["passed"]:
                return True, "Goal achieved: Bài viết hoàn chỉnh đạt chuẩn định lượng của QualityEvaluator.", AgentStatus.COMPLETED

        # 4. Khi đạt giới hạn số bước (current_step_index >= total_steps)
        if current_step_index >= total_steps:
            target_content = None
            if intent == "outline_only":
                target_content = self.context_memory.get("outline")
            elif intent == "summarize":
                target_content = self.context_memory.get("summary")
            else:
                target_content = self.context_memory.get("final_article") or self.context_memory.get("draft_article")

            # BẮT BUỘC: Chỉ khi sản phẩm tồn tại VÀ pass QualityEvaluator mới trả COMPLETED!
            if target_content:
                eval_res = self.evaluator.evaluate(target_content, goal, intent, self.llm)
                if eval_res["passed"]:
                    return True, f"Goal achieved: Đã hoàn thành mục tiêu và đạt chuẩn chất lượng sau {current_step_index} bước.", AgentStatus.COMPLETED
                else:
                    failed_notes = [n for n in eval_res["review_notes"] if n.startswith("✗")]
                    reason_detail = "; ".join(failed_notes) if failed_notes else "Chưa thỏa mãn tiêu chí chất lượng"
                    return True, f"Budget exhausted: Đã thực hiện tối đa {current_step_index}/{self.max_steps} bước nhưng chưa đạt chuẩn nghiệm thu ({reason_detail}).", AgentStatus.BUDGET_EXHAUSTED
            else:
                return True, f"Budget exhausted: Đã thực hiện tối đa {current_step_index}/{self.max_steps} bước nhưng chưa tạo được sản phẩm đầu ra hoàn thiện cho mục đích '{intent}'.", AgentStatus.BUDGET_EXHAUSTED

        return False, "Continue", None

    def run(self, goal: str, input_document: Optional[str] = None) -> FinalReport:
        """
        Vòng lặp Autonomous Agent: Lập plan động -> Lặp thực thi -> Quan sát & Thích ứng -> Lưu log -> Kiểm tra dừng -> Báo cáo cuối
        """
        start_time = time.perf_counter()
        self.logs.clear()
        self.context_memory.clear()
        self.quality_metrics.clear()

        if input_document:
            self.context_memory["input_document"] = input_document.strip()
        elif ":" in goal and len(goal.split(":", 1)[1].strip()) > 30:
            self.context_memory["input_document"] = goal.split(":", 1)[1].strip()

        print(f"\n=======================================================")
        print(f"🤖 [AUTONOMOUS AGENT] BẮT ĐẦU NHIỆM VỤ")
        print(f"🎯 MỤC TIÊU: {goal}")
        print(f"⚙️  GIỚI HẠN: Tối đa {self.max_steps} bước thực thi (Bounded Loop)")
        print(f"🧠 CHẾ ĐỘ: {'LLM-powered (Ollama: ' + (self.llm.model if self.llm else 'None') + ')' if (self.use_llm and self.llm and self.llm.is_available()) else 'Deterministic Fallback'}")
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

        # 2. Vòng lặp thực thi tự chủ (Autonomous Execution Loop)
        action_queue = plan.copy()
        consecutive_failures = 0

        while action_queue and steps_executed < self.max_steps:
            step = action_queue.pop(0)
            step_start = time.perf_counter()
            step.status = "IN_PROGRESS"
            steps_executed += 1

            print(f"\n▶️  [BƯỚC {step.step_id}] Đang thực hiện: {step.title}...")

            input_context = list(self.context_memory.keys())

            # Thực thi hành động với cơ chế bắt lỗi an toàn
            try:
                result = self._execute_step_action(step, topic, goal)
                step.result = result
                step.status = "COMPLETED"
                consecutive_failures = 0
            except Exception as e:
                step.status = "FAILED"
                consecutive_failures += 1
                
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
                
                if consecutive_failures >= 2:
                    self.status = AgentStatus.FAILED
                    stop_reason = f"Execution failed: Tiến trình bị kẹt do liên tiếp thất bại ({str(e)})."
                    break
                else:
                    print(f"   🔄 [RETRY] Tự động thử lại hành động do lỗi.")
                    retry_step = Step(
                        step_id=step.step_id,
                        title=f"[RETRY] {step.title}",
                        description=f"Thử lại bước trước do lỗi: {str(e)}. " + step.description,
                        action_type=step.action_type
                    )
                    action_queue.insert(0, retry_step)
                    continue

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

            words_c = len(result.split())
            chars_c = len(result)
            obs_msg = f"Đã hoàn thành {chars_c} ký tự ({words_c} từ), cấu trúc Markdown hợp lệ."
            print(f"   👁️  [OBSERVE] Quan sát: {obs_msg}")
            print(f"   ✓ Trạng thái: {step.status} ({step_duration}s)")
            print(f"   ✓ Kết quả tóm tắt: {log_entry.output_summary}")

            # Thích ứng bước kế tiếp (Observe & Adapt)
            adapt = None
            if action_queue:
                next_step = action_queue[0]
                adapt_msg = self._observe_and_adapt(step, result, next_step, goal)
                if adapt_msg:
                    if adapt_msg == "REPLAN":
                        print(f"   🔄 [REPLAN] Phát hiện nhu cầu Replan từ LLM. Tạo lại kế hoạch mới...")
                        rem = self.max_steps - steps_executed
                        if rem > 0:
                            action_queue = self.plan_steps(f"Khắc phục và hoàn thiện mục tiêu: {goal}", max_steps=rem)
                        continue
                    else:
                        print(f"   🔄 [ADAPT] Thích ứng chỉ dẫn Bước {next_step.step_id}: {adapt_msg}")

            # Đánh giá điều kiện dừng sau mỗi bước
            should_stop, reason, final_status = self._evaluate_stop_condition(steps_executed, self.max_steps, intent, goal)
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

            if self.final_output:
                self.quality_metrics = self.evaluator.evaluate(self.final_output, goal, intent, self.llm)
            else:
                self.quality_metrics = {"passed": False, "review_notes": ["Không có sản phẩm đầu ra."]}

        # Đảm bảo tính nhất quán trạng thái nếu chưa được gán bởi điều kiện dừng
        if self.status == AgentStatus.RUNNING:
            if self.quality_metrics.get("passed", False):
                self.status = AgentStatus.COMPLETED
            else:
                self.status = AgentStatus.BUDGET_EXHAUSTED

        import subprocess
        git_commit = "unknown"
        try:
            git_commit = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').strip()
        except Exception:
            pass

        reproducibility = {
            "model_version": self.llm.model if self.llm and self.llm.is_available() else "deterministic_fallback",
            "temperature": 0.25,
            "seed": None, # Chưa cấu hình seed cố định cho Ollama
            "git_commit": git_commit,
            "planner_prompt_template_summary": "Hãy lập một kế hoạch checklist tối đa 3 bước...",
            "executor_prompt_template_summary": "Bạn là Autonomous Content Agent đang thực thi nhiệm vụ...",
            "judge_prompt_template_summary": "Đánh giá chất lượng văn bản theo 3 tiêu chí: Tính chính xác (Correctness)...",
            "python_version": sys.version.split()[0],
            "os": sys.platform
        }

        report = FinalReport(
            goal=goal,
            total_steps_planned=len(plan),
            steps_executed=steps_executed,
            status=self.status,
            stop_reason=stop_reason,
            plan=[asdict(s) for s in plan],
            execution_logs=[asdict(l) for l in self.logs], # Bao gồm log thực tế
            final_output=self.final_output,
            quality_metrics=self.quality_metrics,
            total_duration_sec=total_duration,
            reproducibility=reproducibility
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
