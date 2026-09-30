"""
Bộ kịch bản kiểm thử tự động cho Autonomous Checklist Agent
Đánh giá tính Dynamic Planning, điều kiện dừng, giới hạn số bước và tính toàn vẹn của báo cáo cuối.
"""

import sys
import os
import json

from checklist_agent import AutonomousChecklistAgent, AgentStatus

def test_scenario_full_rag():
    print("\n" + "#" * 65)
    print("TEST 1: Kịch bản 3 bước - Viết bài chia sẻ giải thích RAG cho người mới")
    print("#" * 65)
    agent = AutonomousChecklistAgent(max_steps=3)
    goal = "Viết một bài chia sẻ ngắn giải thích RAG là gì cho người mới bắt đầu."
    report = agent.run(goal)
    
    assert report.status == AgentStatus.COMPLETED
    assert report.steps_executed == 3
    assert report.total_steps_planned == 3
    assert len(report.execution_logs) == 3
    assert "Retrieval-Augmented Generation" in report.final_output
    assert "Goal achieved" in report.stop_reason
    print("✅ TEST 1 PASSED: Planner tự tạo 3 bước, thực thi trọn vẹn và đạt mục tiêu.")

def test_scenario_outline_docker_early_stop():
    print("\n" + "#" * 65)
    print("TEST 2: Kịch bản mục tiêu nhỏ (Chuẩn bị outline Docker) -> Dừng sớm sau 2 bước")
    print("#" * 65)
    agent = AutonomousChecklistAgent(max_steps=3)
    # Người dùng chỉ yêu cầu chuẩn bị dàn ý (outline), Agent tự nhận diện chỉ cần 2 bước!
    goal = "Chuẩn bị outline cho bài viết về Docker cho sinh viên IT."
    report = agent.run(goal)
    
    assert report.status == AgentStatus.COMPLETED
    assert report.total_steps_planned == 2  # Dynamic Planner chỉ sinh 2 bước
    assert report.steps_executed == 2
    assert "Goal achieved" in report.stop_reason
    assert "DOCKER" in report.final_output
    print("✅ TEST 2 PASSED: Dynamic Planner tự tạo 2 bước, không ép khuôn 3 bước và dừng sớm.")

def test_scenario_bounded_loop_validation():
    print("\n" + "#" * 65)
    print("TEST 3: Kiểm định rào chắn Bounded Loop (Khống chế max_steps <= 3)")
    print("#" * 65)
    try:
        # Giả lập tham số vượt quá ngưỡng 3 bước
        agent = AutonomousChecklistAgent(max_steps=5)
        print("❌ FAILED: Không chặn được max_steps > 3")
        sys.exit(1)
    except ValueError as e:
        print(f"✅ Bắt lỗi thành công: {e}")
        print("✅ TEST 3 PASSED: Cơ chế Bounded Loop chặn đứng vi phạm giới hạn số bước.")

if __name__ == "__main__":
    test_scenario_full_rag()
    test_scenario_outline_docker_early_stop()
    test_scenario_bounded_loop_validation()
    print("\n" + "=" * 65)
    print("🎉 TẤT CẢ 3 KỊCH BẢN ĐÁNH GIÁ ĐỀU ĐẠT CHUẨN XUẤT SẮC!")
    print("=" * 65)
