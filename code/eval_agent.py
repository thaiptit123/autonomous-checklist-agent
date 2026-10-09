import sys
import unittest
import os
from checklist_agent import AutonomousChecklistAgent, AgentStatus, OllamaClient

def assert_status_stop_reason_consistent(report):
    """Kiểm tra tính nhất quán hệ thống giữa AgentStatus và nội dung stop_reason."""
    if report.status == AgentStatus.COMPLETED:
        assert "Goal achieved" in report.stop_reason, (
            f"Mâu thuẫn: status là COMPLETED nhưng stop_reason là '{report.stop_reason}'"
        )
    elif report.status == AgentStatus.BUDGET_EXHAUSTED:
        assert "Budget exhausted" in report.stop_reason, (
            f"Mâu thuẫn: status là BUDGET_EXHAUSTED nhưng stop_reason là '{report.stop_reason}'"
        )
    elif report.status == AgentStatus.FAILED:
        assert "Execution failed" in report.stop_reason, (
            f"Mâu thuẫn: status là FAILED nhưng stop_reason là '{report.stop_reason}'"
        )
    else:
        raise AssertionError(f"Trạng thái không hợp lệ: {report.status}")


def is_ollama_available():
    """Kiểm tra môi trường có sẵn Ollama hay không."""
    client = OllamaClient()
    return client.is_available()


class TestUnitOffline(unittest.TestCase):
    """
    Unit Tests (Offline) - Kiểm tra logic nền tảng, không cần gọi LLM thực tế.
    Môi trường: Deterministic Fallback.
    """
    
    def test_outline_docker_early_stop(self):
        print("\n[Unit Test] 1. Kịch bản mục tiêu nhỏ (outline Docker) -> Dừng sớm")
        agent = AutonomousChecklistAgent(max_steps=3, use_llm=False)
        goal = "Chuẩn bị outline cho bài viết về Docker cho sinh viên IT."
        report = agent.run(goal)

        assert_status_stop_reason_consistent(report)
        self.assertEqual(report.status, AgentStatus.COMPLETED)
        self.assertEqual(report.steps_executed, 2)
        self.assertIn("Docker", report.final_output)
        self.assertTrue(report.quality_metrics["passed"])

    def test_summarize_with_input_document(self):
        print("\n[Unit Test] 2. Tóm tắt tài liệu nguồn (Summarize with Input Document)")
        agent = AutonomousChecklistAgent(max_steps=3, use_llm=False)
        sample_doc = (
            "Model Context Protocol (MCP) là giao thức chuẩn mở do Anthropic phát triển. "
            "MCP kết nối an toàn các mô hình AI với các công cụ cục bộ và kho dữ liệu phân tán doanh nghiệp."
        )
        goal = "Tóm tắt tài liệu kỹ thuật về Model Context Protocol (MCP) cho kỹ sư phần mềm."
        report = agent.run(goal, input_document=sample_doc)

        assert_status_stop_reason_consistent(report)
        self.assertEqual(report.status, AgentStatus.COMPLETED)
        self.assertEqual(report.steps_executed, 2)
        self.assertIn("MCP", report.final_output)
        self.assertTrue(report.quality_metrics["passed"])

    def test_budget_exhausted_unmet_goal(self):
        print("\n[Unit Test] 3. Hết ngân sách bước nhưng CHƯA đạt mục tiêu (Budget Exhausted)")
        agent = AutonomousChecklistAgent(max_steps=1, use_llm=False)
        goal = "Viết bài chia sẻ chuyên sâu về Kubernetes cho đội ngũ DevOps."
        report = agent.run(goal)

        assert_status_stop_reason_consistent(report)
        self.assertEqual(report.status, AgentStatus.BUDGET_EXHAUSTED)
        self.assertEqual(report.steps_executed, 1)
        self.assertIn("chưa tạo được sản phẩm đầu ra hoàn thiện", report.stop_reason)

    def test_quality_rejection_budget_exhausted(self):
        print("\n[Unit Test] 4. QualityEvaluator từ chối nghiệm thu -> BUDGET_EXHAUSTED")
        agent = AutonomousChecklistAgent(max_steps=3, use_llm=False)
        original_execute = agent._execute_step_action

        def degraded_execute(step, topic, goal):
            if step.action_type == "review_polish":
                bad_content = "RAG là retrieval augmented generation hết."
                agent.context_memory["final_article"] = bad_content
                return bad_content
            return original_execute(step, topic, goal)

        agent._execute_step_action = degraded_execute
        goal = "Viết một bài chia sẻ ngắn giải thích RAG là gì cho người mới bắt đầu."
        report = agent.run(goal)

        assert_status_stop_reason_consistent(report)
        self.assertEqual(report.status, AgentStatus.BUDGET_EXHAUSTED)
        self.assertFalse(report.quality_metrics["passed"])

    def test_open_domain_kafka(self):
        print("\n[Unit Test] 5. Kịch bản mục tiêu mở hoàn toàn (Open-Domain: Apache Kafka)")
        agent = AutonomousChecklistAgent(max_steps=3, use_llm=False)
        goal = "Hướng dẫn cơ bản về kiến trúc Event-Driven với Apache Kafka cho kỹ sư backend."
        report = agent.run(goal)

        assert_status_stop_reason_consistent(report)
        self.assertEqual(report.status, AgentStatus.COMPLETED)
        self.assertIn("Kafka", report.final_output)
        self.assertTrue(report.quality_metrics["passed"])

    def test_dynamic_observation_and_adaptation(self):
        print("\n[Unit Test] 6. Quan sát & Thích ứng chỉ dẫn bước kế tiếp (Observe & Adapt)")
        agent = AutonomousChecklistAgent(max_steps=3, use_llm=False)
        goal = "Viết một bài chia sẻ ngắn giải thích RAG là gì cho người mới bắt đầu."
        plan = agent.plan_steps(goal)

        mock_outline = "1. Định nghĩa RAG.\n2. Cấu trúc Vector DB.\n3. Kết luận."
        next_step = plan[1]
        adaptation_note = agent._observe_and_adapt(plan[0], mock_outline, next_step, goal)

        self.assertIsNotNone(adaptation_note)
        self.assertIn("Chỉ dẫn thích ứng", next_step.description)

    def test_action_failure_recovery_stuck(self):
        print("\n[Unit Test] 7. Xử lý lỗi Action và phát hiện kẹt (Retry & Progress Stuck)")
        agent = AutonomousChecklistAgent(max_steps=3, use_llm=False)

        original_execute = agent._execute_step_action

        def failing_execute(step, topic, goal):
            if step.action_type == "generate":
                raise RuntimeError("Mất kết nối tới máy chủ")
            return original_execute(step, topic, goal)

        agent._execute_step_action = failing_execute
        goal = "Viết một bài chia sẻ ngắn giải thích RAG là gì cho người mới bắt đầu."
        report = agent.run(goal)

        assert_status_stop_reason_consistent(report)
        self.assertEqual(report.status, AgentStatus.FAILED)
        self.assertIn("Tiến trình bị kẹt", report.stop_reason)
        # 1 thành công (outline) + 2 lần lỗi (generate + retry) = 3
        self.assertEqual(report.steps_executed, 3)

    def test_bounded_loop_validation(self):
        print("\n[Unit Test] 8. Kiểm định rào chắn Bounded Loop (max_steps <= 3)")
        with self.assertRaises(ValueError):
            AutonomousChecklistAgent(max_steps=5)

    def test_summarize_without_document_fails(self):
        print("\n[Unit Test] 9. Từ chối tóm tắt khi thiếu tài liệu nguồn (Missing Source Doc -> FAILED)")
        agent = AutonomousChecklistAgent(max_steps=3, use_llm=False)
        goal = "Tóm tắt tài liệu này cho ban giám đốc."
        report = agent.run(goal, input_document=None)

        assert_status_stop_reason_consistent(report)
        self.assertEqual(report.status, AgentStatus.FAILED)
        self.assertIn("tài liệu", report.stop_reason.lower())

    def test_adversarial_plumbing_wrong_fact_right_format(self):
        print("\n[Unit Test] 10. Judge Plumbing Test: Xử lý nội dung sai sự thật nhưng chuẩn format")
        agent = AutonomousChecklistAgent(max_steps=3, use_llm=False)
        # Bật mock LLM để kiểm thử logic Evaluator thay vì monkeypatch evaluate
        agent.use_llm = True
        agent.llm = OllamaClient()
        agent.llm.is_available = lambda: True
        
        # Mock executor để trả về content sai sự thật
        original_execute = agent._execute_step_action
        def degraded_execute(step, topic, goal):
            if step.action_type == "review_polish":
                bad_content = "# RAG là gì?\n\nRAG là một kỹ thuật. RAG gồm Indexing -> Retrieval -> Generation. RAG luôn đảm bảo câu trả lời chính xác 100%. RAG luôn dựa hoàn toàn trên dữ liệu thực tế không bao giờ sai sót."
                agent.context_memory["final_article"] = bad_content
                return bad_content
            return original_execute(step, topic, goal)
        agent._execute_step_action = degraded_execute
        
        # Mock LLM sinh ra phán quyết từ chối correctness
        def mock_generate(prompt, max_tokens=100):
            if "Đánh giá chất lượng văn bản" in prompt:
                return '{"correctness": 0, "groundedness": 1, "completeness": 1, "reason": "Khẳng định tuyệt đối sai sự thật (RAG luôn đảm bảo chính xác 100%)"}'
            return "Mock response"
        agent.llm.generate = mock_generate

        goal = "Viết bài chia sẻ ngắn giải thích RAG."
        report = agent.run(goal)
        
        self.assertEqual(report.status, AgentStatus.BUDGET_EXHAUSTED)
        self.assertFalse(report.quality_metrics["passed"])

    def test_adversarial_plumbing_missing_content(self):
        print("\n[Unit Test] 11. Judge Plumbing Test: Xử lý nội dung thiếu bắt buộc")
        agent = AutonomousChecklistAgent(max_steps=3, use_llm=False)
        agent.use_llm = True
        agent.llm = OllamaClient()
        agent.llm.is_available = lambda: True
        
        def mock_generate(prompt, max_tokens=100):
            if "Đánh giá chất lượng văn bản" in prompt:
                return '{"correctness": 1, "groundedness": 1, "completeness": 0, "reason": "Thiếu định nghĩa cơ bản về RAG"}'
            return ""
        agent.llm.generate = mock_generate
        
        report = agent.run("Viết bài giải thích RAG")
        self.assertFalse(report.quality_metrics["passed"])

    def test_adversarial_plumbing_not_grounded(self):
        print("\n[Unit Test] 12. Judge Plumbing Test: Xử lý nội dung không bám sát (Not Grounded)")
        agent = AutonomousChecklistAgent(max_steps=3, use_llm=False)
        agent.use_llm = True
        agent.llm = OllamaClient()
        agent.llm.is_available = lambda: True
        
        def mock_generate(prompt, max_tokens=100):
            if "Đánh giá chất lượng văn bản" in prompt:
                return '{"correctness": 1, "groundedness": 0, "completeness": 1, "reason": "Bịa đặt thông tin không có trong source"}'
            return ""
        agent.llm.generate = mock_generate
        
        report = agent.run("Viết bài giải thích RAG")
        self.assertFalse(report.quality_metrics["passed"])

    def test_dynamic_replan_execution(self):
        print("\n[Unit Test] 13. Chứng minh REPLAN thực sự thay đổi action_queue (Replan Execution)")
        agent = AutonomousChecklistAgent(max_steps=3, use_llm=False)
        agent.use_llm = True
        agent.llm = OllamaClient()
        agent.llm.is_available = lambda: True
        
        # Bắt agent trả về 'REPLAN' ở bước observe
        original_generate = agent.llm.generate
        def mock_generate(prompt, max_tokens=100):
            if "MỘT câu chỉ dẫn ngắn gọn" in prompt:
                return "Cần phải REPLAN toàn bộ kế hoạch."
            if "lập kế hoạch" in prompt.lower() or "checklist" in prompt.lower():
                return '[{"step_id": "REPLAN_1", "title": "Bước Replan", "description": "Làm lại", "action_type": "generate"}]'
            return original_generate(prompt, max_tokens)
        agent.llm.generate = mock_generate
        
        # Test sẽ thất bại hoặc dừng sớm, nhưng quan trọng là log/queue có REPLAN
        report = agent.run("Viết bài chia sẻ ngắn.")
        # Nếu replan xảy ra, kế hoạch mới sẽ được thực thi và lưu vào execution_logs
        self.assertIsNotNone(report)
        replan_executed = any("Bước Replan" in log["step_title"] for log in report.execution_logs)
        self.assertTrue(replan_executed, "Bước mới từ REPLAN chưa thực sự được thực thi và ghi nhận vào execution_logs")



@unittest.skipUnless(is_ollama_available(), "Bỏ qua Integration Test vì không kết nối được Ollama cục bộ")
class TestIntegrationLLM(unittest.TestCase):
    """
    Integration Tests - Phụ thuộc vào môi trường Ollama thực tế.
    """

    def test_full_rag_llm(self):
        print("\n[Integration Test] 1. Kịch bản LLM tự hành thực tế - Viết bài chia sẻ giải thích RAG")
        agent = AutonomousChecklistAgent(max_steps=3, use_llm=True)
        goal = "Viết một bài chia sẻ ngắn giải thích RAG là gì cho người mới bắt đầu."
        report = agent.run(goal)

        assert_status_stop_reason_consistent(report)
        self.assertEqual(report.status, AgentStatus.COMPLETED)
        self.assertTrue(report.quality_metrics["passed"])
        self.assertGreater(report.total_duration_sec, 0.5)

    def test_adversarial_integration_correctness_generic(self):
        print("\n[Integration Test] 2. Adversarial (Real LLM): Kiểm tra lỗi Correctness (Mô tả chung chung, sai bản chất)")
        agent = AutonomousChecklistAgent(max_steps=1, use_llm=True)
        adversarial_content = "RAG là một khuôn khổ để chuẩn hóa và giải quyết tính tương thích trong hệ thống phần mềm, giúp tối ưu vận hành."
        res = agent.evaluator.evaluate(adversarial_content, "Viết bài chia sẻ ngắn giải thích RAG", "full_article", agent.llm)
        self.assertFalse(res["passed"], "Nội dung chung chung sai bản chất nhưng lại được pass.")
        self.assertIsNotNone(res.get("judge_verdict"), "Không nhận được judge_verdict.")
        self.assertNotIn("error", res["judge_verdict"], f"LLM Judge gặp lỗi: {res['judge_verdict']}")
        self.assertEqual(res["judge_verdict"].get("correctness"), 0, "Judge không phát hiện lỗi correctness đối với mô tả chung chung.")

    def test_adversarial_integration_correctness(self):
        print("\n[Integration Test] 3. Adversarial (Real LLM): Kiểm tra lỗi Correctness (Sai hoàn toàn)")
        agent = AutonomousChecklistAgent(max_steps=1, use_llm=True)
        adversarial_content = "RAG là một công cụ để nén ảnh JPEG và tăng tốc độ wifi. RAG không liên quan gì đến trí tuệ nhân tạo."
        res = agent.evaluator.evaluate(adversarial_content, "Viết bài chia sẻ ngắn giải thích RAG", "full_article", agent.llm)
        self.assertFalse(res["passed"], "Nội dung sai bản chất nhưng lại được pass.")
        self.assertIsNotNone(res.get("judge_verdict"), "Không nhận được judge_verdict.")
        self.assertNotIn("error", res["judge_verdict"], f"LLM Judge gặp lỗi: {res['judge_verdict']}")
        self.assertEqual(res["judge_verdict"].get("correctness"), 0, "Judge không phát hiện lỗi correctness.")

    def test_adversarial_integration_completeness(self):
        print("\n[Integration Test] 4. Adversarial (Real LLM): Kiểm tra lỗi Completeness (Thiếu yêu cầu)")
        agent = AutonomousChecklistAgent(max_steps=1, use_llm=True)
        adversarial_content = "RAG (Retrieval-Augmented Generation) là công nghệ kết hợp tìm kiếm và sinh văn bản."
        # Quá ngắn, thiếu phân tích, ví dụ
        res = agent.evaluator.evaluate(adversarial_content, "Viết bài chia sẻ ngắn giải thích RAG với ví dụ và ưu nhược điểm chi tiết", "full_article", agent.llm)
        self.assertFalse(res["passed"], "Nội dung thiếu yêu cầu nhưng lại được pass.")
        self.assertIsNotNone(res.get("judge_verdict"), "Không nhận được judge_verdict.")
        self.assertNotIn("error", res["judge_verdict"], f"LLM Judge gặp lỗi: {res['judge_verdict']}")
        self.assertEqual(res["judge_verdict"].get("completeness"), 0, "Judge không phát hiện lỗi completeness.")

    def test_adversarial_integration_groundedness(self):
        print("\n[Integration Test] 5. Adversarial (Real LLM): Kiểm tra lỗi Groundedness (Bịa đặt nguồn)")
        agent = AutonomousChecklistAgent(max_steps=1, use_llm=True)
        source_doc = "Sản phẩm A chỉ hỗ trợ kết nối Bluetooth 4.0 và không có WiFi."
        adversarial_content = "Sản phẩm A là thiết bị tiên tiến nhất hiện nay, trang bị WiFi 6 băng tần kép và Bluetooth 5.2, mang lại tốc độ vượt trội."
        res = agent.evaluator.evaluate(adversarial_content, "Tóm tắt tính năng sản phẩm A", "summarize", agent.llm, source_doc=source_doc)
        self.assertFalse(res["passed"], "Nội dung không bám sát nguồn nhưng lại được pass.")
        self.assertIsNotNone(res.get("judge_verdict"), "Không nhận được judge_verdict.")
        self.assertNotIn("error", res["judge_verdict"], f"LLM Judge gặp lỗi: {res['judge_verdict']}")
        self.assertEqual(res["judge_verdict"].get("groundedness"), 0, "Judge không phát hiện lỗi groundedness.")



if __name__ == "__main__":
    print("\n" + "=" * 68)
    print("🚀 KHỞI CHẠY TEST SUITE (UNIT TESTS & INTEGRATION TESTS)")
    print("=" * 68)
    unittest.main(verbosity=2)


