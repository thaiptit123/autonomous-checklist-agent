"""
Bộ kịch bản kiểm thử toàn diện cho Autonomous Checklist Agent (Series AI Guru x TiniX)
Đánh giá:
1. LLM Autonomous Execution & Real Latency (Chế độ LLM thật qua Ollama)
2. Dynamic Planning & Execution với Bounded Loop (<= 3 bước)
3. Đánh giá điều kiện dừng chặt chẽ (Goal Achieved vs Budget Exhausted vs Failed)
4. Kiểm định chất lượng định lượng (Quality Evaluator: TTR, Length, Structure, Relevance)
5. Quan sát và thích ứng chỉ dẫn bước kế tiếp (Observe & Adaptive Step Guidance)
6. Các kịch bản biên & kịch bản thất bại (Open-domain goals, Evaluator rejection, Action exceptions)
"""

import sys
from checklist_agent import AutonomousChecklistAgent, AgentStatus


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


def test_scenario_full_rag_llm():
    print("\n" + "#" * 68)
    print("TEST 1: Kịch bản LLM tự hành thực tế - Viết bài chia sẻ giải thích RAG")
    print("#" * 68)
    agent = AutonomousChecklistAgent(max_steps=3, use_llm=True)
    assert agent.llm is not None and agent.llm.is_available(), "Ollama LLM phải khả dụng cho Test 1"
    goal = "Viết một bài chia sẻ ngắn giải thích RAG là gì cho người mới bắt đầu."
    report = agent.run(goal)

    assert_status_stop_reason_consistent(report)
    assert report.status == AgentStatus.COMPLETED
    assert report.steps_executed == 3
    assert report.total_steps_planned == 3
    assert len(report.execution_logs) == 3
    assert report.quality_metrics["passed"] is True
    assert report.quality_metrics["ttr"] >= 0.35
    assert report.total_duration_sec > 0.5  # Minh chứng thời gian thực thi thực tế của LLM
    print(f"✅ TEST 1 PASSED: LLM Planner & Executor hoàn thành xuất sắc trong {report.total_duration_sec}s (TTR={report.quality_metrics['ttr']}).")


def test_scenario_outline_docker_early_stop():
    print("\n" + "#" * 68)
    print("TEST 2: Kịch bản mục tiêu nhỏ (Chuẩn bị outline Docker) -> Dừng sớm sau 2 bước")
    print("#" * 68)
    agent = AutonomousChecklistAgent(max_steps=3, use_llm=False)
    goal = "Chuẩn bị outline cho bài viết về Docker cho sinh viên IT."
    report = agent.run(goal)

    assert_status_stop_reason_consistent(report)
    assert report.status == AgentStatus.COMPLETED
    assert report.total_steps_planned == 2  # Dynamic Planner chỉ sinh 2 bước
    assert report.steps_executed == 2
    assert "Docker" in report.final_output
    assert report.quality_metrics["passed"] is True
    print("✅ TEST 2 PASSED: Dynamic Planner tự tạo đúng 2 bước và dừng sớm an toàn khi mục tiêu hoàn thành.")


def test_scenario_summarize_with_input_document():
    print("\n" + "#" * 68)
    print("TEST 3: Kịch bản tóm tắt tài liệu nguồn (Summarize with Input Document)")
    print("#" * 68)
    agent = AutonomousChecklistAgent(max_steps=3, use_llm=False)
    sample_doc = (
        "Model Context Protocol (MCP) là giao thức chuẩn mở do Anthropic phát triển. "
        "MCP kết nối an toàn các mô hình AI với các công cụ cục bộ và kho dữ liệu phân tán doanh nghiệp."
    )
    goal = "Tóm tắt tài liệu kỹ thuật về Model Context Protocol (MCP) cho kỹ sư phần mềm."
    report = agent.run(goal, input_document=sample_doc)

    assert_status_stop_reason_consistent(report)
    assert report.status == AgentStatus.COMPLETED
    assert report.total_steps_planned == 2
    assert report.steps_executed == 2
    assert "MCP" in report.final_output
    assert report.quality_metrics["passed"] is True
    print("✅ TEST 3 PASSED: Hoàn thành tóm tắt tài liệu nguồn 2 bước bám sát nội dung và nghiệm thu đạt chuẩn.")


def test_scenario_budget_exhausted_unmet_goal():
    print("\n" + "#" * 68)
    print("TEST 4: Kịch bản hết ngân sách bước nhưng CHƯA đạt mục tiêu (Budget Exhausted)")
    print("#" * 68)
    # Mục tiêu yêu cầu viết bài hoàn chỉnh (cần outline -> draft -> review = 3 bước)
    # nhưng cấu hình max_steps = 1 (ngân sách chỉ cho phép 1 bước)
    agent = AutonomousChecklistAgent(max_steps=1, use_llm=False)
    goal = "Viết bài chia sẻ chuyên sâu về Kubernetes cho đội ngũ DevOps."
    report = agent.run(goal)

    assert_status_stop_reason_consistent(report)
    assert report.status == AgentStatus.BUDGET_EXHAUSTED
    assert report.steps_executed == 1
    assert "chưa tạo được sản phẩm đầu ra hoàn thiện" in report.stop_reason
    print("✅ TEST 4 PASSED: Phân định chính xác BUDGET_EXHAUSTED khi hết ngân sách bước nhưng chưa hoàn thành mục tiêu.")


def test_scenario_quality_rejection_budget_exhausted():
    print("\n" + "#" * 68)
    print("TEST 5: Kịch bản QualityEvaluator từ chối nghiệm thu -> BUDGET_EXHAUSTED (dù chạy đủ 3 bước)")
    print("#" * 68)
    agent = AutonomousChecklistAgent(max_steps=3, use_llm=False)

    # Giả lập sản phẩm đầu ra bước 3 kém chất lượng (quá ngắn < 100 ký tự và thiếu cấu trúc)
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

    # Dù chạy đủ 3 bước, sản phẩm không pass QualityEvaluator -> BẮT BUỘC kết luận BUDGET_EXHAUSTED!
    assert_status_stop_reason_consistent(report)
    assert report.status == AgentStatus.BUDGET_EXHAUSTED
    assert report.quality_metrics["passed"] is False
    assert "Độ dài chưa đạt" in report.stop_reason or "Chưa thỏa mãn" in report.stop_reason
    print("✅ TEST 5 PASSED: QualityEvaluator đóng vai trò cổng gác chất lượng nghiêm ngặt, từ chối sản phẩm không đạt chuẩn.")


def test_scenario_open_domain_kafka():
    print("\n" + "#" * 68)
    print("TEST 6: Kịch bản mục tiêu mở hoàn toàn (Open-Domain: Apache Kafka)")
    print("#" * 68)
    agent = AutonomousChecklistAgent(max_steps=3, use_llm=False)
    # Chủ đề Apache Kafka không hề nằm trong bất kỳ câu lệnh if/elif hardcode nào
    goal = "Hướng dẫn cơ bản về kiến trúc Event-Driven với Apache Kafka cho kỹ sư backend."
    report = agent.run(goal)

    assert_status_stop_reason_consistent(report)
    assert report.status == AgentStatus.COMPLETED
    assert "Kafka" in report.final_output
    assert report.quality_metrics["passed"] is True
    print("✅ TEST 6 PASSED: Hệ thống xử lý mục tiêu mở hoàn toàn linh hoạt, sinh cấu trúc bài viết và nghiệm thu hợp lệ.")


def test_scenario_dynamic_observation_and_adaptation():
    print("\n" + "#" * 68)
    print("TEST 7: Kịch bản Quan sát & Thích ứng chỉ dẫn bước kế tiếp (Observe & Adaptive Step Guidance)")
    print("#" * 68)
    agent = AutonomousChecklistAgent(max_steps=3, use_llm=False)
    goal = "Viết một bài chia sẻ ngắn giải thích RAG là gì cho người mới bắt đầu."
    plan = agent.plan_steps(goal)

    # Giả lập kết quả bước 1 là dàn ý chưa có ví dụ đời thường
    mock_outline = "1. Định nghĩa RAG.\n2. Cấu trúc Vector DB.\n3. Kết luận."
    next_step = plan[1]
    adaptation_note = agent._observe_and_adapt(plan[0], mock_outline, next_step, goal)

    assert adaptation_note is not None
    assert "ví dụ" in adaptation_note.lower() or "thích ứng" in next_step.description.lower()
    assert "Chỉ dẫn thích ứng" in next_step.description
    print(f"✅ TEST 7 PASSED: Tác nhân quan sát kết quả trung gian và thích ứng chỉ dẫn Bước 2: '{adaptation_note}'.")


def test_scenario_action_failure_recovery():
    print("\n" + "#" * 68)
    print("TEST 8: Kịch bản xử lý lỗi khi một Action thất bại (Action Failure -> FAILED)")
    print("#" * 68)
    agent = AutonomousChecklistAgent(max_steps=3, use_llm=False)

    # Giả lập hành động bước 2 bị lỗi ngoại lệ (ví dụ lỗi mạng / tài nguyên)
    original_execute = agent._execute_step_action

    def failing_execute(step, topic, goal):
        if step.action_type == "generate":
            raise RuntimeError("Mất kết nối tới máy chủ cơ sở dữ liệu tri thức")
        return original_execute(step, topic, goal)

    agent._execute_step_action = failing_execute
    goal = "Viết một bài chia sẻ ngắn giải thích RAG là gì cho người mới bắt đầu."
    report = agent.run(goal)

    assert_status_stop_reason_consistent(report)
    assert report.status == AgentStatus.FAILED
    assert "Mất kết nối" in report.stop_reason
    assert report.steps_executed == 2
    assert report.execution_logs[-1]["status"] == "FAILED"
    print("✅ TEST 8 PASSED: Bắt lỗi bước thực thi chính xác, chuyển trạng thái FAILED và ghi nhận log nhất quán.")


def test_scenario_bounded_loop_validation():
    print("\n" + "#" * 68)
    print("TEST 9: Kiểm định rào chắn Bounded Loop (Khống chế max_steps <= 3)")
    print("#" * 68)
    try:
        agent = AutonomousChecklistAgent(max_steps=5)
        print("❌ FAILED: Không chặn được max_steps > 3")
        sys.exit(1)
    except ValueError as e:
        print(f"✅ Bắt lỗi thành công: {e}")
        print("✅ TEST 9 PASSED: Cơ chế Bounded Loop chặn đứng vi phạm giới hạn số bước.")


if __name__ == "__main__":
    test_scenario_full_rag_llm()
    test_scenario_outline_docker_early_stop()
    test_scenario_summarize_with_input_document()
    test_scenario_budget_exhausted_unmet_goal()
    test_scenario_quality_rejection_budget_exhausted()
    test_scenario_open_domain_kafka()
    test_scenario_dynamic_observation_and_adaptation()
    test_scenario_action_failure_recovery()
    test_scenario_bounded_loop_validation()
    print("\n" + "=" * 68)
    print("🎉 TẤT CẢ 9/9 KỊCH BẢN KIỂM THỬ ĐỀU ĐẠT CHUẨN (ALL 9/9 PASSED)!")
    print("=" * 68)
