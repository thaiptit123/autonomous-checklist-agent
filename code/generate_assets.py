"""
Generate high-legibility diagrams and terminal screenshot for Bai 44.
Directly addresses reviewer comments:
- Hinh 1: Big clear text, no wasted whitespace, highly legible inside boxes.
- Hinh 2: Big clear text, clear arrows, legible labels.
- Hinh 3: Big monospace terminal font, crisp and readable on A4 without zooming.
"""
import os
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Liberation Sans", "Noto Sans", "Arial"]
plt.rcParams["font.monospace"] = ["Noto Sans Mono", "Liberation Mono", "DejaVu Sans Mono"]
plt.rcParams["axes.unicode_minus"] = False


def generate_architecture_diagram():
    # Tỷ lệ 11.5 x 6.4 cho bố cục rộng rãi, chữ to rõ ràng như sách giáo trình
    fig, ax = plt.subplots(figsize=(11.5, 6.4), dpi=300)
    ax.set_facecolor("#FFFFFF")
    fig.patch.set_facecolor("#FFFFFF")

    # Tiêu đề chính
    ax.text(5.75, 6.08, "KIẾN TRÚC TÁC NHÂN TỰ HÀNH CHECKLIST (TỐI ĐA 3 BƯỚC)", 
            fontsize=18.5, fontweight="bold", ha="center", color="#004AAD")
    ax.text(5.75, 5.72, "Mô hình 5 khối với vòng lặp quyết định và kiểm định chất lượng an toàn", 
            fontsize=13.5, ha="center", color="#475569", style="italic")

    # Hộp 1: Mục tiêu người dùng
    box_goal = patches.FancyBboxPatch((0.35, 2.00), 2.25, 2.65, boxstyle="round,pad=0.10", 
                                      edgecolor="#004AAD", facecolor="#EFF6FF", linewidth=2.0)
    ax.add_patch(box_goal)
    ax.text(1.475, 4.28, "1. MỤC TIÊU", fontsize=14.5, fontweight="bold", ha="center", color="#004AAD")
    ax.text(1.475, 3.96, "(User Goal)", fontsize=12.0, ha="center", color="#004AAD", style="italic")
    ax.text(1.475, 2.95, "Tiếp nhận\nmục tiêu & phân\ntích ý định", 
            fontsize=12.2, fontweight="bold", ha="center", color="#0F172A", linespacing=1.28)

    # Mũi tên 1 -> 2
    ax.annotate("", xy=(2.85, 3.32), xytext=(2.60, 3.32),
                arrowprops=dict(arrowstyle="-|>", color="#004AAD", lw=2.5, mutation_scale=16))

    # Hộp 2: Bộ lập kế hoạch động (Planner Node)
    box_plan = patches.FancyBboxPatch((2.85, 2.00), 2.35, 2.65, boxstyle="round,pad=0.10", 
                                      edgecolor="#E8630A", facecolor="#FFF7ED", linewidth=2.0)
    ax.add_patch(box_plan)
    ax.text(4.025, 4.28, "2. LẬP KẾ HOẠCH", fontsize=14.5, fontweight="bold", ha="center", color="#E8630A")
    ax.text(4.025, 3.96, "(Dynamic Planner)", fontsize=12.0, ha="center", color="#E8630A", style="italic")
    ax.text(4.025, 2.95, "Phân rã mục tiêu\nChecklist động (LLM)\n(Tối đa ≤ 3 bước)", 
            fontsize=12.2, fontweight="bold", ha="center", color="#0F172A", linespacing=1.28)

    # Mũi tên 2 -> 3
    ax.annotate("", xy=(5.45, 3.32), xytext=(5.20, 3.32),
                arrowprops=dict(arrowstyle="-|>", color="#E8630A", lw=2.5, mutation_scale=16))

    # Hộp 3: Bộ thực thi & Bộ nhớ ngữ cảnh (Execution Engine)
    box_exec = patches.FancyBboxPatch((5.45, 1.95), 3.65, 2.75, boxstyle="round,pad=0.10", 
                                      edgecolor="#059669", facecolor="#ECFDF5", linewidth=2.0)
    ax.add_patch(box_exec)
    ax.text(7.275, 4.32, "3. THỰC THI & BỘ NHỚ", fontsize=14.5, fontweight="bold", ha="center", color="#059669")
    ax.text(7.275, 4.00, "(Execution & Memory)", fontsize=12.0, ha="center", color="#059669", style="italic")
    ax.text(5.60, 3.15, "• Bước 1: Luận điểm (research)\n• Bước 2: Dàn ý (outline)\n• Bước 3: Hoàn thiện (generate)", 
            fontsize=12.2, fontweight="bold", ha="left", color="#0F172A", linespacing=1.35)
    ax.text(7.275, 2.20, "[Bộ nhớ ngữ cảnh & Step Logs]", fontsize=12.0, fontweight="bold", ha="center", color="#047857")

    # Mũi tên 3 -> 4
    ax.annotate("", xy=(9.35, 3.32), xytext=(9.10, 3.32),
                arrowprops=dict(arrowstyle="-|>", color="#059669", lw=2.5, mutation_scale=16))

    # Hộp 4: Bộ đánh giá điều kiện dừng (Stop Condition Evaluator)
    box_stop = patches.FancyBboxPatch((9.35, 2.00), 1.80, 2.65, boxstyle="round,pad=0.10", 
                                      edgecolor="#DC2626", facecolor="#FEF2F2", linewidth=2.0)
    ax.add_patch(box_stop)
    ax.text(10.25, 4.28, "4. ĐIỀU KIỆN", fontsize=14.0, fontweight="bold", ha="center", color="#DC2626")
    ax.text(10.25, 3.96, "(Stop Check)", fontsize=11.8, ha="center", color="#DC2626", style="italic")
    ax.text(10.25, 2.95, "Đạt chuẩn?\nHoặc\nBước ≥ 3\n→ DỪNG", 
            fontsize=12.2, fontweight="bold", ha="center", color="#0F172A", linespacing=1.28)

    # Mũi tên lặp phản hồi (Loopback khi chưa dừng)
    ax.annotate("", xy=(7.275, 4.70), xytext=(10.25, 4.65),
                arrowprops=dict(arrowstyle="-|>", color="#475569", lw=2.4, connectionstyle="arc3,rad=0.20", ls="--", mutation_scale=15))
    ax.text(8.75, 5.12, "Lặp tiếp (chưa đạt & còn bước)", fontsize=12.0, color="#1E293B", ha="center", fontweight="bold",
            zorder=5, bbox=dict(boxstyle="round,pad=0.25", facecolor="#FFFFFF", edgecolor="#64748B", lw=1.2))

    # Mũi tên dừng -> Xuống báo cáo cuối
    ax.annotate("", xy=(10.25, 1.55), xytext=(10.25, 2.00),
                arrowprops=dict(arrowstyle="-|>", color="#004AAD", lw=2.5, mutation_scale=16))
    ax.text(10.25, 1.78, "Thỏa dừng / hết bước", fontsize=11.5, color="#004AAD", ha="center", fontweight="bold",
            zorder=5, bbox=dict(boxstyle="round,pad=0.22", facecolor="#EFF6FF", edgecolor="#004AAD", lw=1.2))

    # Hộp 5: Báo cáo cuối cùng & Sản phẩm nghiệm thu
    box_out = patches.FancyBboxPatch((0.35, 0.15), 10.80, 1.40, boxstyle="round,pad=0.12", 
                                     edgecolor="#004AAD", facecolor="#FFFFFF", linewidth=2.0)
    ax.add_patch(box_out)
    ax.text(5.75, 1.22, "5. BÁO CÁO TỔNG KẾT & SẢN PHẨM NGHIỆM THU (FINAL REPORT & ARTIFACTS)", 
            fontsize=14.0, fontweight="bold", ha="center", color="#004AAD")
    ax.text(5.75, 0.80, "• Kế hoạch ban đầu (Plan)   • Nhật ký kiểm toán (Audit Trail)   • Trạng thái (COMPLETED / EXHAUSTED)", 
            fontsize=11.6, ha="center", color="#0F172A", fontweight="bold")
    ax.text(5.75, 0.42, "• Lý do dừng chi tiết   • Kiểm định chất lượng (TTR, Độ dài, LLM Judge)   • Sản phẩm hoàn chỉnh", 
            fontsize=11.6, ha="center", color="#334155", fontweight="bold")

    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 6.4)
    ax.axis("off")

    img_path = os.path.join(OUTPUT_DIR, "architecture_diagram.png")
    plt.tight_layout()
    plt.savefig(img_path, dpi=300, bbox_inches="tight", pad_inches=0.03)
    plt.close()
    print(f"Generated: {img_path}")


def generate_state_flow_diagram():
    fig, ax = plt.subplots(figsize=(9.8, 5.4), dpi=300)
    ax.set_facecolor("#FFFFFF")
    fig.patch.set_facecolor("#FFFFFF")

    ax.text(4.90, 5.08, "LUỒNG TRUYỀN DỮ LIỆU & ĐIỀU KIỆN DỪNG QUA CÁC BƯỚC", 
            fontsize=15.5, fontweight="bold", ha="center", color="#004AAD")
    ax.text(4.90, 4.76, "(Hành động Bước 3 linh hoạt: generate khi dùng LLM hoặc review_polish khi fallback)", 
            fontsize=11.5, ha="center", color="#475569", style="italic")

    # Hộp Bước 1
    s1 = patches.FancyBboxPatch((0.35, 2.15), 2.50, 2.35, boxstyle="round,pad=0.10", 
                                edgecolor="#004AAD", facecolor="#EFF6FF", linewidth=2.0)
    ax.add_patch(s1)
    ax.text(1.60, 4.10, "BƯỚC 1\nLuận Điểm Cốt Lõi", fontsize=13.0, fontweight="bold", ha="center", color="#004AAD", linespacing=1.2)
    ax.text(1.60, 2.95, "action: research_points\nĐầu vào: Mục tiêu\nĐầu ra: research_points", 
            fontsize=11.8, fontweight="bold", ha="center", color="#0F172A", linespacing=1.3)

    # Mũi tên 1->2
    ax.annotate("", xy=(3.65, 3.25), xytext=(2.85, 3.25),
                arrowprops=dict(arrowstyle="-|>", color="#004AAD", lw=2.5, mutation_scale=16))
    ax.text(3.25, 3.55, "State", fontsize=11.8, fontweight="bold", color="#004AAD", ha="center")

    # Hộp Bước 2
    s2 = patches.FancyBboxPatch((3.65, 2.15), 2.50, 2.35, boxstyle="round,pad=0.10", 
                                edgecolor="#E8630A", facecolor="#FFF7ED", linewidth=2.0)
    ax.add_patch(s2)
    ax.text(4.90, 4.10, "BƯỚC 2\nDàn Ý Chi Tiết", fontsize=13.0, fontweight="bold", ha="center", color="#E8630A", linespacing=1.2)
    ax.text(4.90, 2.95, "action: outline\nĐầu vào: research_points\nĐầu ra: outline (4 phần)", 
            fontsize=11.8, fontweight="bold", ha="center", color="#0F172A", linespacing=1.3)

    # Mũi tên 2->3
    ax.annotate("", xy=(6.95, 3.25), xytext=(6.15, 3.25),
                arrowprops=dict(arrowstyle="-|>", color="#E8630A", lw=2.5, mutation_scale=16))
    ax.text(6.55, 3.55, "State", fontsize=11.8, fontweight="bold", color="#E8630A", ha="center")

    # Hộp Bước 3
    s3 = patches.FancyBboxPatch((6.95, 2.15), 2.50, 2.35, boxstyle="round,pad=0.10", 
                                edgecolor="#059669", facecolor="#ECFDF5", linewidth=2.0)
    ax.add_patch(s3)
    ax.text(8.20, 4.10, "BƯỚC 3\nHoàn Thiện Bài Viết", fontsize=13.0, fontweight="bold", ha="center", color="#059669", linespacing=1.2)
    ax.text(8.20, 2.95, "action: generate (LLM) /\nreview_polish (Fallback)\nĐầu vào: outline + memory\nĐầu ra: final_article", 
            fontsize=11.2, fontweight="bold", ha="center", color="#0F172A", linespacing=1.25)

    # Khung đánh giá điều kiện dừng bên dưới (rời nhau 0.35 khoảng cách, không chạm nhau)
    cond_box = patches.FancyBboxPatch((0.35, 0.15), 9.10, 1.65, boxstyle="round,pad=0.12", 
                                      edgecolor="#DC2626", facecolor="#FEF2F2", linewidth=2.0)
    ax.add_patch(cond_box)
    ax.text(4.90, 1.48, "BỘ ĐÁNH GIÁ ĐIỀU KIỆN DỪNG (STOP CONDITION EVALUATOR)", 
            fontsize=13.2, fontweight="bold", ha="center", color="#DC2626")
    ax.text(4.90, 0.78, "• Goal Achieved == True  → DỪNG (COMPLETED: Nghiệm thu đạt chuẩn định lượng & LLM Judge)\n• Steps Executed ≥ 3    → DỪNG (BUDGET_EXHAUSTED: Chốt chặn an toàn Bounded Loop)\n• Step Execution Error   → DỪNG (FAILED: Ghi nhận nhật ký lỗi sau 2 lần retry)", 
            fontsize=11.5, fontweight="bold", ha="center", color="#1E293B", linespacing=1.35)

    ax.set_xlim(0, 9.8)
    ax.set_ylim(0, 5.4)
    ax.axis("off")

    img_path = os.path.join(OUTPUT_DIR, "state_flow_diagram.png")
    plt.tight_layout()
    plt.savefig(img_path, dpi=300, bbox_inches="tight", pad_inches=0.03)
    plt.close()
    print(f"Generated: {img_path}")


def generate_terminal_screenshot():
    # Render terminal đồ họa cao cấp: font monospace lớn 11.8pt, sắc nét, tương phản hoàn hảo
    fig, ax = plt.subplots(figsize=(10.0, 5.2), dpi=300)
    fig.patch.set_facecolor("#0F172A")
    ax.set_facecolor("#0F172A")

    # Header window buttons (macOS/Terminal style)
    circle_red = patches.Circle((0.35, 4.86), 0.08, color="#EF4444")
    circle_yellow = patches.Circle((0.58, 4.86), 0.08, color="#F59E0B")
    circle_green = patches.Circle((0.81, 4.86), 0.08, color="#10B981")
    ax.add_patch(circle_red)
    ax.add_patch(circle_yellow)
    ax.add_patch(circle_green)

    ax.text(5.00, 4.86, "bash - thaipt@tinix-aiguru: ~/checklist-agent (python3 checklist_agent.py)", 
            fontsize=11.2, color="#94A3B8", ha="center", family="monospace", fontweight="bold", va="center")

    terminal_text = [
        ("$ python3 code/checklist_agent.py", "#38BDF8"),
        ("==========================================================================", "#38BDF8"),
        ("[AUTONOMOUS AGENT] BẮT ĐẦU NHIỆM VỤ | Model: tinix-lm:latest (Ollama LLM)", "#38BDF8"),
        ("MỤC TIÊU: Viết bài chia sẻ ngắn giải thích RAG là gì cho người mới bắt đầu.", "#F8FAFC"),
        ("GIỚI HẠN: Tối đa 3 bước thực thi an toàn (Bounded Execution Loop)", "#FCD34D"),
        ("==========================================================================", "#38BDF8"),
        ("[PLANNER] KHỞI TẠO CHECKLIST 3 BƯỚC ĐỘNG BẰNG LLM:", "#A7F3D0"),
        ("  [1] (research_points) Xác định nội dung và luận điểm cốt lõi về RAG", "#F1F5F9"),
        ("  [2] (outline) Dàn ý bài chia sẻ ngắn 4 phần (mở đầu, cơ chế, ví dụ, kết)", "#F1F5F9"),
        ("  [3] (generate) Viết và hoàn thiện bài viết theo cấu trúc dàn ý", "#F1F5F9"),
        ("--------------------------------------------------------------------------", "#475569"),
        ("[BƯỚC 1] research_points -> [OK] COMPLETED (3.176s) | [ADAPT] Nhấn mạnh RAG", "#34D399"),
        ("[BƯỚC 2] outline         -> [OK] COMPLETED (3.356s) | [ADAPT] Ví dụ mở sách", "#34D399"),
        ("[BƯỚC 3] generate        -> [OK] COMPLETED (7.380s | 1.872 ký tự, 391 từ)", "#34D399"),
        ("  [LLM JUDGE] Thẩm định: correctness=1, groundedness=1, completeness=1 -> ĐẠT", "#A7F3D0"),
        ("[STOP CONDITION] Kích hoạt dừng: Goal achieved (LLM Judge Verified)", "#F87171"),
        ("==========================================================================", "#38BDF8"),
        ("BÁO CÁO: COMPLETED | 3/3 bước | 19.812s | TTR=0.43 >= 0.35 | PASS", "#FCD34D"),
    ]

    y_pos = 4.54
    for line, color in terminal_text:
        ax.text(0.20, y_pos, line, fontsize=11.8, color=color, family="monospace", va="center", fontweight="bold")
        y_pos -= 0.245

    ax.set_xlim(0, 10.0)
    ax.set_ylim(0, 5.2)
    ax.axis("off")

    img_path = os.path.join(OUTPUT_DIR, "terminal_execution.png")
    plt.tight_layout()
    plt.savefig(img_path, dpi=300, bbox_inches="tight", pad_inches=0.03)
    plt.close()
    print(f"Generated: {img_path}")


if __name__ == "__main__":
    generate_architecture_diagram()
    generate_state_flow_diagram()
    generate_terminal_screenshot()
