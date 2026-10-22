"""
Generate high-legibility diagrams and authentic terminal screenshot for Bai 44.
Directly addresses reviewer comments:
- Relaxed typography: Title Case instead of aggressive ALL-CAPS BOLD; normal weights for body texts.
- Visual hierarchy: elements do not compete for attention; calm, professional software architecture styling.
- Zero line/arrow collision: generous breathing room (>0.35 units) between badges, text labels, and connection lines.
- Authentic terminal: Catppuccin/VS Code developer theme, subtle dim dividers, 100% regular monospace weights,
  only accenting key keywords (COMPLETED, PASS), highly legible at 100% zoom.
"""
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.font_manager import FontProperties

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Liberation Sans", "Noto Sans", "Arial"]
plt.rcParams["axes.unicode_minus"] = False

LIBERATION_MONO_REG = "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf"
LIBERATION_MONO_BOLD = "/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf"


def generate_architecture_diagram():
    # 10.0 x 6.2 canvas, clean white background, refined typography
    fig, ax = plt.subplots(figsize=(10.0, 6.2), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    # Main title: Title Case, refined semi-bold, not screaming ALL-CAPS
    ax.text(5.00, 5.86, "Kiến trúc tác nhân tự hành với vòng lặp giới hạn (≤ 3 bước)", 
            fontsize=15.8, fontweight="bold", ha="center", color="#1E3A8A", fontfamily="DejaVu Sans")
    ax.text(5.00, 5.54, "Mô hình 5 thành phần với vòng lặp quyết định và kiểm định an toàn", 
            fontsize=11.2, ha="center", color="#64748B", style="italic", fontfamily="DejaVu Sans")

    # 4 boxes across Y: 1.95 to 4.70 (height 2.75)
    # Box 1: Mục tiêu (User Goal)
    b1 = patches.FancyBboxPatch((0.25, 1.95), 2.05, 2.75, boxstyle="round,pad=0.10",
                                edgecolor="#3B82F6", facecolor="#F8FAFC", linewidth=1.5)
    ax.add_patch(b1)
    ax.text(1.275, 4.38, "1. Tiếp nhận mục tiêu", fontsize=12.5, fontweight="bold", ha="center", color="#1E40AF", fontfamily="DejaVu Sans")
    ax.text(1.275, 4.08, "(User Goal)", fontsize=10.5, ha="center", color="#3B82F6", style="italic", fontfamily="DejaVu Sans")
    ax.text(1.275, 3.00, "Tiếp nhận\nmục tiêu &\nphân tích\ný định", 
            fontsize=11.5, fontweight="normal", ha="center", color="#334155", linespacing=1.35, fontfamily="DejaVu Sans")

    # Arrow 1->2
    ax.annotate("", xy=(2.65, 3.32), xytext=(2.30, 3.32),
                arrowprops=dict(arrowstyle="-|>", color="#3B82F6", lw=1.8, mutation_scale=14))

    # Box 2: Kế hoạch (Planner)
    b2 = patches.FancyBboxPatch((2.65, 1.95), 2.25, 2.75, boxstyle="round,pad=0.10",
                                edgecolor="#D97706", facecolor="#FFFBEB", linewidth=1.5)
    ax.add_patch(b2)
    ax.text(3.775, 4.38, "2. Lập kế hoạch", fontsize=12.5, fontweight="bold", ha="center", color="#B45309", fontfamily="DejaVu Sans")
    ax.text(3.775, 4.08, "(Dynamic Planner)", fontsize=10.5, ha="center", color="#D97706", style="italic", fontfamily="DejaVu Sans")
    ax.text(3.775, 3.00, "Phân rã\nChecklist\nđộng (LLM)\n(Tối đa ≤ 3)", 
            fontsize=11.5, fontweight="normal", ha="center", color="#334155", linespacing=1.35, fontfamily="DejaVu Sans")

    # Arrow 2->3
    ax.annotate("", xy=(5.25, 3.32), xytext=(4.90, 3.32),
                arrowprops=dict(arrowstyle="-|>", color="#D97706", lw=1.8, mutation_scale=14))

    # Box 3: Thực thi & Bộ nhớ (Execution & Memory)
    b3 = patches.FancyBboxPatch((5.25, 1.95), 3.05, 2.75, boxstyle="round,pad=0.10",
                                edgecolor="#059669", facecolor="#F0FDF4", linewidth=1.5)
    ax.add_patch(b3)
    ax.text(6.775, 4.38, "3. Thực thi & Bộ nhớ", fontsize=12.5, fontweight="bold", ha="center", color="#047857", fontfamily="DejaVu Sans")
    ax.text(6.775, 4.08, "(Execution & Memory)", fontsize=10.5, ha="center", color="#059669", style="italic", fontfamily="DejaVu Sans")
    ax.text(5.50, 3.12, "• Bước 1: Luận điểm cốt lõi\n• Bước 2: Dàn ý chi tiết 4 phần\n• Bước 3: Hoàn thiện bài viết", 
            fontsize=11.2, fontweight="normal", ha="left", color="#334155", linespacing=1.35, fontfamily="DejaVu Sans")
    ax.text(6.775, 2.25, "Ngữ cảnh & Nhật ký từng bước", fontsize=10.2, fontweight="normal", ha="center", color="#047857", style="italic", fontfamily="DejaVu Sans")

    # Arrow 3->4
    ax.annotate("", xy=(8.65, 3.32), xytext=(8.30, 3.32),
                arrowprops=dict(arrowstyle="-|>", color="#059669", lw=1.8, mutation_scale=14))

    # Box 4: Điều kiện dừng (Stop Condition)
    b4 = patches.FancyBboxPatch((8.65, 1.95), 1.15, 2.75, boxstyle="round,pad=0.10",
                                edgecolor="#DC2626", facecolor="#FEF2F2", linewidth=1.5)
    ax.add_patch(b4)
    ax.text(9.225, 4.38, "4. Kiểm định", fontsize=12.5, fontweight="bold", ha="center", color="#B91C1C", fontfamily="DejaVu Sans")
    ax.text(9.225, 4.08, "(Stop Gate)", fontsize=10.5, ha="center", color="#DC2626", style="italic", fontfamily="DejaVu Sans")
    ax.text(9.225, 3.10, "Đạt chuẩn\nmục tiêu?\nHoặc\nbước ≥ 3", 
            fontsize=11.2, fontweight="normal", ha="center", color="#334155", linespacing=1.30, fontfamily="DejaVu Sans")
    ax.text(9.225, 2.25, "Chốt chặn", fontsize=10.5, fontweight="normal", ha="center", color="#B91C1C", fontfamily="DejaVu Sans")

    # Loopback arrow: curves smoothly from Box 4 back to Box 3
    ax.annotate("", xy=(6.775, 4.70), xytext=(9.225, 4.70),
                arrowprops=dict(arrowstyle="-|>", color="#64748B", lw=1.8, connectionstyle="arc3,rad=0.15", ls="--", mutation_scale=14))
    # Place loopback text neatly above the arc with clear breathing margin (NO OVERLAP!)
    ax.text(8.00, 5.32, "Chưa đạt chuẩn & còn bước (Lặp)", fontsize=9.8, color="#475569", ha="center", va="center", fontweight="normal",
            fontfamily="DejaVu Sans", bbox=dict(boxstyle="round,pad=0.22", facecolor="#FFFFFF", edgecolor="#CBD5E1", lw=0.9))

    # Clean unobstructed vertical arrow from Stop to Report at x=9.225
    ax.annotate("", xy=(9.225, 1.55), xytext=(9.225, 1.95),
                arrowprops=dict(arrowstyle="-|>", color="#1E40AF", lw=1.8, mutation_scale=14))
    # Place "Thỏa điều kiện dừng" badge cleanly to the left at x=8.45 with ha="right" (0.50+ clearance to arrow!)
    ax.text(8.45, 1.75, "Thỏa điều kiện dừng", fontsize=9.8, color="#1E40AF", ha="right", va="center", fontweight="normal",
            fontfamily="DejaVu Sans", bbox=dict(boxstyle="round,pad=0.22", facecolor="#EFF6FF", edgecolor="#93C5FD", lw=0.9))

    # Box 5: Final Report
    b5 = patches.FancyBboxPatch((0.25, 0.15), 9.55, 1.40, boxstyle="round,pad=0.12",
                                edgecolor="#3B82F6", facecolor="#F8FAFC", linewidth=1.5)
    ax.add_patch(b5)
    ax.text(5.00, 1.18, "5. Báo cáo tổng kết & Sản phẩm nghiệm thu (Final Report)", 
            fontsize=12.5, fontweight="bold", ha="center", color="#1E40AF", fontfamily="DejaVu Sans")
    ax.text(5.00, 0.76, "• Kế hoạch ban đầu (Plan)     • Nhật ký kiểm toán (Audit Trail)     • Trạng thái kết thúc", 
            fontsize=11.0, ha="center", color="#334155", fontweight="normal", fontfamily="DejaVu Sans")
    ax.text(5.00, 0.40, "• Lý do dừng chi tiết     • Thẩm định chất lượng (TTR, Length, LLM Judge)     • Bài viết hoàn chỉnh", 
            fontsize=11.0, ha="center", color="#64748B", fontweight="normal", fontfamily="DejaVu Sans")

    ax.set_xlim(0, 10.0)
    ax.set_ylim(0, 6.2)
    ax.axis("off")

    img_path = os.path.join(OUTPUT_DIR, "architecture_diagram.png")
    plt.tight_layout()
    plt.savefig(img_path, dpi=300, bbox_inches="tight", pad_inches=0.03)
    plt.close()
    print(f"Generated: {img_path}")


def generate_state_flow_diagram():
    # 10.2 x 5.8 canvas, calm and readable
    fig, ax = plt.subplots(figsize=(10.2, 5.8), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    # Main title: Title Case, refined
    ax.text(5.10, 5.45, "Luồng truyền dữ liệu & Điều kiện dừng qua các bước", 
            fontsize=15.8, fontweight="bold", ha="center", color="#1E3A8A", fontfamily="DejaVu Sans")
    ax.text(5.10, 5.14, "Cơ chế truyền ngữ cảnh (Context Memory) và rà soát điều kiện dừng ở từng bước", 
            fontsize=11.0, ha="center", color="#64748B", style="italic", fontfamily="DejaVu Sans")

    # 3 Step boxes with generous gaps
    # Step 1: width 2.40, x: 0.45 to 2.85
    s1 = patches.FancyBboxPatch((0.45, 2.50), 2.40, 2.30, boxstyle="round,pad=0.08",
                                edgecolor="#3B82F6", facecolor="#F8FAFC", linewidth=1.5)
    ax.add_patch(s1)
    ax.text(1.65, 4.40, "Bước 1\nLuận điểm cốt lõi", fontsize=12.5, fontweight="bold", ha="center", color="#1E40AF", linespacing=1.2, fontfamily="DejaVu Sans")
    ax.text(1.65, 3.25, "• Tác vụ: research\n• Vào: Mục tiêu đề bài\n• Ra: Luận điểm chính", 
            fontsize=11.0, fontweight="normal", ha="center", color="#334155", linespacing=1.35, fontfamily="DejaVu Sans")

    # Arrow 1->2 in gap 2.85 to 3.90
    ax.annotate("", xy=(3.85, 3.45), xytext=(2.95, 3.45),
                arrowprops=dict(arrowstyle="-|>", color="#3B82F6", lw=1.8, mutation_scale=14))
    # Label "Ngữ cảnh" centered above arrow with clear margin
    ax.text(3.375, 3.75, "Ngữ cảnh", fontsize=9.5, fontweight="normal", color="#1E40AF", ha="center", va="center",
            fontfamily="DejaVu Sans")

    # Step 2: width 2.40, x: 3.90 to 6.30
    s2 = patches.FancyBboxPatch((3.90, 2.50), 2.40, 2.30, boxstyle="round,pad=0.08",
                                edgecolor="#D97706", facecolor="#FFFBEB", linewidth=1.5)
    ax.add_patch(s2)
    ax.text(5.10, 4.40, "Bước 2\nDàn ý chi tiết", fontsize=12.5, fontweight="bold", ha="center", color="#B45309", linespacing=1.2, fontfamily="DejaVu Sans")
    ax.text(5.10, 3.25, "• Tác vụ: outline\n• Vào: Luận điểm B1\n• Ra: Dàn ý 4 phần", 
            fontsize=11.0, fontweight="normal", ha="center", color="#334155", linespacing=1.35, fontfamily="DejaVu Sans")

    # Arrow 2->3 in gap 6.30 to 7.35
    ax.annotate("", xy=(7.30, 3.45), xytext=(6.40, 3.45),
                arrowprops=dict(arrowstyle="-|>", color="#D97706", lw=1.8, mutation_scale=14))
    # Label "Ngữ cảnh" centered above arrow
    ax.text(6.825, 3.75, "Ngữ cảnh", fontsize=9.5, fontweight="normal", color="#B45309", ha="center", va="center",
            fontfamily="DejaVu Sans")

    # Step 3: width 2.40, x: 7.35 to 9.75
    s3 = patches.FancyBboxPatch((7.35, 2.50), 2.40, 2.30, boxstyle="round,pad=0.08",
                                edgecolor="#059669", facecolor="#F0FDF4", linewidth=1.5)
    ax.add_patch(s3)
    ax.text(8.55, 4.40, "Bước 3\nHoàn thiện bài viết", fontsize=12.5, fontweight="bold", ha="center", color="#047857", linespacing=1.2, fontfamily="DejaVu Sans")
    ax.text(8.55, 3.25, "• Tác vụ: generate\n• Vào: Dàn ý & bộ nhớ\n• Ra: Bài viết hoàn thiện", 
            fontsize=11.0, fontweight="normal", ha="center", color="#334155", linespacing=1.35, fontfamily="DejaVu Sans")

    # Evaluator Box: width 9.30, x: 0.45 to 9.75
    cond_box = patches.FancyBboxPatch((0.45, 0.15), 9.30, 2.05, boxstyle="round,pad=0.10",
                                      edgecolor="#DC2626", facecolor="#FEF2F2", linewidth=1.5)
    ax.add_patch(cond_box)
    ax.text(5.10, 1.86, "Bộ đánh giá điều kiện dừng (Stop Condition Evaluator)", 
            fontsize=12.2, fontweight="bold", ha="center", color="#B91C1C", fontfamily="DejaVu Sans")

    # 3 columns inside Stop box - perfectly aligned with the 3 step boxes above
    # Col 1: Completed
    ax.text(1.65, 1.36, "Đạt chuẩn mục tiêu", fontsize=11.2, fontweight="bold", ha="center", color="#047857", fontfamily="DejaVu Sans")
    ax.text(1.65, 0.82, "Goal Achieved == True\nĐạt TTR, độ dài & LLM Judge", 
            fontsize=10.2, fontweight="normal", ha="center", color="#334155", linespacing=1.30, fontfamily="DejaVu Sans")
    ax.text(1.65, 0.42, "→ COMPLETED", fontsize=10.8, fontweight="bold", ha="center", color="#059669", fontfamily="DejaVu Sans")

    # Col 2: Budget exhausted
    ax.text(5.10, 1.36, "Hết ngân sách bước", fontsize=11.2, fontweight="bold", ha="center", color="#B45309", fontfamily="DejaVu Sans")
    ax.text(5.10, 0.82, "Steps Executed ≥ 3\nChốt chặn Bounded Loop", 
            fontsize=10.2, fontweight="normal", ha="center", color="#334155", linespacing=1.30, fontfamily="DejaVu Sans")
    ax.text(5.10, 0.42, "→ BUDGET_EXHAUSTED", fontsize=10.8, fontweight="bold", ha="center", color="#D97706", fontfamily="DejaVu Sans")

    # Col 3: Failed
    ax.text(8.55, 1.36, "Lỗi thực thi", fontsize=11.2, fontweight="bold", ha="center", color="#B91C1C", fontfamily="DejaVu Sans")
    ax.text(8.55, 0.82, "Execution Error\nThất bại sau 2 lần retry", 
            fontsize=10.2, fontweight="normal", ha="center", color="#334155", linespacing=1.30, fontfamily="DejaVu Sans")
    ax.text(8.55, 0.42, "→ FAILED", fontsize=10.8, fontweight="bold", ha="center", color="#DC2626", fontfamily="DejaVu Sans")

    ax.set_xlim(0, 10.2)
    ax.set_ylim(0, 5.8)
    ax.axis("off")

    img_path = os.path.join(OUTPUT_DIR, "state_flow_diagram.png")
    plt.tight_layout()
    plt.savefig(img_path, dpi=300, bbox_inches="tight", pad_inches=0.03)
    plt.close()
    print(f"Generated: {img_path}")


def generate_terminal_screenshot():
    # Modern developer terminal styling (Catppuccin/VS Code theme)
    # Compact height 3.75 to ensure Page 14 accommodates all 3 enumerate items cleanly
    fig, ax = plt.subplots(figsize=(8.2, 3.75), dpi=300)
    fig.patch.set_facecolor("#181825")
    ax.set_facecolor("#181825")

    # Font properties: strictly regular weight Liberation Mono for 100% genuine monospace terminal
    fp_reg = FontProperties(fname=LIBERATION_MONO_REG, size=9.8)
    fp_bold = FontProperties(fname=LIBERATION_MONO_BOLD, size=9.8)
    fp_header = FontProperties(fname=LIBERATION_MONO_REG, size=9.0)

    # Header window chrome (macOS style dots)
    circle_red = patches.Circle((0.28, 3.52), 0.075, color="#F38BA8")
    circle_yellow = patches.Circle((0.50, 3.52), 0.075, color="#F9E2AF")
    circle_green = patches.Circle((0.72, 3.52), 0.075, color="#A6E3A1")
    ax.add_patch(circle_red)
    ax.add_patch(circle_yellow)
    ax.add_patch(circle_green)

    ax.text(1.02, 3.52, "thaipt@tinix-aiguru: ~/checklist-agent (python3 checklist_agent.py)", 
            color="#9399B2", ha="left", fontproperties=fp_header, va="center")

    # Subtle divider line
    div_line = "─" * 66

    terminal_elements = [
        # (text, color, is_bold)
        ("$ python3 code/checklist_agent.py", "#89B4FA", False),
        (div_line, "#313244", False),
        ("[AGENT] BẮT ĐẦU NHIỆM VỤ | tinix-lm:latest (Ollama)", "#89B4FA", False),
        ("MỤC TIÊU: Viết bài chia sẻ ngắn giải thích RAG cho người mới.", "#CDD6F4", False),
        ("GIỚI HẠN: Tối đa 3 bước thực thi (Bounded Execution Loop)", "#F9E2AF", False),
        (div_line, "#313244", False),
        ("[PLANNER] Khởi tạo checklist 3 bước động bằng LLM:", "#94E2D5", False),
        ("  [1] (research_points) Luận điểm cốt lõi về RAG", "#BAC2DE", False),
        ("  [2] (outline) Dàn ý 4 phần (mở, thân, ví dụ, kết)", "#BAC2DE", False),
        ("  [3] (generate) Hoàn thiện bài viết theo dàn ý", "#BAC2DE", False),
        (div_line, "#313244", False),
        ("[BƯỚC 1] research_points -> [OK] COMPLETED (3.176s)", "#A6E3A1", False),
        ("[BƯỚC 2] outline         -> [OK] COMPLETED (3.356s)", "#A6E3A1", False),
        ("[BƯỚC 3] generate        -> [OK] COMPLETED (7.380s | 1.872 ký tự)", "#A6E3A1", False),
        ("  [LLM JUDGE] Thẩm định: correctness=1, quality=PASS", "#94E2D5", False),
        ("[STOP CONDITION] Kích hoạt dừng: Goal achieved (Đạt chuẩn)", "#FAB387", False),
        (div_line, "#313244", False),
        ("BÁO CÁO: COMPLETED | 3/3 bước | 19.812s | TTR=0.43 | PASS", "#F9E2AF", True),
    ]

    y_pos = 3.22
    for line, color, is_bold in terminal_elements:
        fp = fp_bold if is_bold else fp_reg
        ax.text(0.22, y_pos, line, color=color, fontproperties=fp, va="center")
        y_pos -= 0.176

    ax.set_xlim(0, 8.2)
    ax.set_ylim(0, 3.75)
    ax.axis("off")

    img_path = os.path.join(OUTPUT_DIR, "terminal_execution.png")
    plt.tight_layout()
    plt.savefig(img_path, dpi=300, bbox_inches="tight", pad_inches=0.02)
    plt.close()
    print(f"Generated: {img_path}")


if __name__ == "__main__":
    generate_architecture_diagram()
    generate_state_flow_diagram()
    generate_terminal_screenshot()
