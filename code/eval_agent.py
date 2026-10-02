"""
Bộ kịch bản kiểm thử toàn diện cho Autonomous Checklist Agent (Series AI Guru x TiniX)
Đánh giá:
1. Dynamic Planning & Execution với Bounded Loop (<= 3 bước)
2. Kiểm tra điều kiện dừng (Goal Achieved vs Budget Exhausted vs Failed)
3. Kiểm định chất lượng định lượng (Quality Evaluator: TTR, Length, Structure, Relevance)
4. Các kịch bản biên & kịch bản thất bại (Failure cases, Open-domain goals, Step failures)
"""

import sys
from checklist_agent import AutonomousChecklistAgent, AgentStatus


def test_scenario_full_rag():
    print("\n" + "#" * 68)
    print("TEST 1: Kịch bản 3 bước - Viết bài chia sẻ giải thích RAG cho người mới")
    print("#" * 68)
    agent = AutonomousChecklistAgent(max_steps=3, use_llm=False)
    goal = "Viết một bài chia sẻ ngắn giải thích RAG là gì cho người mới bắt đầu."
    report = agent.run(goal)

    assert report.status == AgentStatus.COMPLETED
    assert report.steps_executed == 3
    assert report.total_steps_planned == 3
    assert len(report.execution_logs) == 3
    assert "Retrieval-Augmented Generation" in report.final_output
    assert "Goal achieved" in report.stop_reason
    assert report.quality_metrics["passed"] is True
    assert report.quality_metrics["ttr"] >= 0.35
    print("✅ TEST 1 PASSED: Planner tự tạo 3 bước, thực thi trọn vẹn và đạt mục tiêu nghiệm thu.")


def test_scenario_outline_docker_early_stop():
    print("\n" + "#" * 68)
    print("TEST 2: Kịch bản mục tiêu nhỏ (Chuẩn bị outline Docker) -> Dừng sớm sau 2 bước")
    print("#" * 68)
    agent = AutonomousChecklistAgent(max_steps=3, use_llm=False)
    goal = "Chuẩn bị outline cho bài viết về Docker cho sinh viên IT."
    report = agent.run(goal)

    assert report.status == AgentStatus.COMPLETED
    assert report.total_steps_planned == 2  # Dynamic Planner chỉ sinh 2 bước
    assert report.steps_executed == 2
    assert "Goal achieved" in report.stop_reason
    assert "DOCKER" in report.final_output.upper()
    assert report.quality_metrics["passed"] is True
    print("✅ TEST 2 PASSED: Dynamic Planner tự tạo 2 bước, không ép khuôn 3 bước và dừng sớm an toàn.")


def test_scenario_summarize_two_steps():
    print("\n" + "#" * 68)
    print("TEST 3: Kịch bản tóm tắt tài liệu kỹ thuật (Summarize 2 bước)")
    print("#" * 68)
    agent = AutonomousChecklistAgent(max_steps=3, use_llm=False)
    goal = "Tóm tắt tài liệu kỹ thuật về Model Context Protocol (MCP) cho kỹ sư phần mềm."
    report = agent.run(goal)

    assert report.status == AgentStatus.COMPLETED
    assert report.total_steps_planned == 2
    assert report.steps_executed == 2
    assert "Goal achieved" in report.stop_reason
    assert "BẢN TÓM TẮT SÚC TÍCH" in report.final_output.upper()
    assert report.quality_metrics["passed"] is True
    print("✅ TEST 3 PASSED: Hoàn thành tóm tắt tài liệu 2 bước và nghiệm thu đạt chuẩn.")


def test_scenario_budget_exhausted_unmet_goal():
    print("\n" + "#" * 68)
    print("TEST 4: Kịch bản hết bước nhưng CHƯA đạt mục tiêu (Budget Exhausted)")
    print("#" * 68)
    # Mục tiêu yêu cầu viết bài hoàn chỉnh (cần outline -> draft -> review = 3 bước)
    # nhưng cấu hình max_steps = 1 (ngân sách chỉ cho phép 1 bước)
    agent = AutonomousChecklistAgent(max_steps=1, use_llm=False)
    goal = "Viết bài chia sẻ chuyên sâu về Kubernetes cho đội ngũ DevOps."
    report = agent.run(goal)

    # Đảm bảo hệ thống KHÔNG được báo COMPLETED khi mới chỉ xong dàn ý
    assert report.status == AgentStatus.BUDGET_EXHAUSTED
    assert report.steps_executed == 1
    assert "Budget exhausted" in report.stop_reason
    assert "chưa hoàn thành trọn vẹn mục tiêu" in report.stop_reason
    print("✅ TEST 4 PASSED: Phân định chính xác BUDGET_EXHAUSTED khi hết ngân sách bước nhưng chưa thỏa nghiệm thu.")


def test_scenario_open_domain_goal():
    print("\n" + "#" * 68)
    print("TEST 5: Kịch bản mục tiêu mở ngoài các chủ đề định nghĩa sẵn")
    print("#" * 68)
    agent = AutonomousChecklistAgent(max_steps=3, use_llm=False)
    goal = "Hướng dẫn tối ưu hóa cơ sở dữ liệu PostgreSQL cho các ứng dụng tải cao."
    report = agent.run(goal)

    assert report.status == AgentStatus.COMPLETED
    assert "PostgreSQL" in report.final_output
    assert "Goal achieved" in report.stop_reason
    assert report.quality_metrics["passed"] is True
    print("✅ TEST 5 PASSED: Hệ thống xử lý mục tiêu mở linh hoạt, sinh cấu trúc bài viết và nghiệm thu hợp lệ.")


def test_scenario_action_failure_recovery():
    print("\n" + "#" * 68)
    print("TEST 6: Kịch bản xử lý lỗi khi một Action thất bại (Action Failure -> FAILED)")
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

    assert report.status == AgentStatus.FAILED
    assert "Execution failed" in report.stop_reason
    assert "Mất kết nối" in report.stop_reason
    assert report.steps_executed == 2  # Bước 1 thành công, bước 2 gặp lỗi và dừng lại
    assert report.execution_logs[-1]["status"] == "FAILED"
    print("✅ TEST 6 PASSED: Bắt lỗi bước thực thi chính xác, chuyển trạng thái FAILED và ghi nhận log nhất quán.")


def test_scenario_bounded_loop_validation():
    print("\n" + "#" * 68)
    print("TEST 7: Kiểm định rào chắn Bounded Loop (Khống chế max_steps <= 3)")
    print("#" * 68)
    try:
        agent = AutonomousChecklistAgent(max_steps=5)
        print("❌ FAILED: Không chặn được max_steps > 3")
        sys.exit(1)
    except ValueError as e:
        print(f"✅ Bắt lỗi thành công: {e}")
        print("✅ TEST 7 PASSED: Cơ chế Bounded Loop chặn đứng vi phạm giới hạn số bước.")


if __name__ == "__main__":
    test_scenario_full_rag()
    test_scenario_outline_docker_early_stop()
    test_scenario_summarize_two_steps()
    test_scenario_budget_exhausted_unmet_goal()
    test_scenario_open_domain_goal()
    test_scenario_action_failure_recovery()
    test_scenario_bounded_loop_validation()
    print("\n" + "=" * 68)
    print("🎉 TẤT CẢ 7/7 KỊCH BẢN KIỂM THỬ ĐỀU ĐẠT CHUẨN (ALL PASSED)!")
    print("=" * 68)
