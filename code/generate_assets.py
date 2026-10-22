"""
Generate high-legibility diagrams and authentic terminal screenshot for Bai 44.
Directly addresses reviewer comments:
- Relaxed typography: eliminate all unnecessary bolding inside figures; regular weights with curated colors.
- Zero line/arrow collision: generous breathing room (>0.35 units) between badges, text labels, and connection lines.
- Authentic terminal: Catppuccin/VS Code developer theme, subtle dim dividers, strictly 100% REGULAR monospace font,
  distinguishing keywords purely by harmonious color accents (NO bold glyphs), highly legible at 100% zoom.
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

NOTO_SANS_MONO_LIGHT = "/usr/share/fonts/truetype/noto/NotoSansMono-Light.ttf"
NOTO_SANS_MONO_REG = "/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf"
LIBERATION_MONO_REG = "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf"


def generate_architecture_diagram():
    # 10.0 x 6.2 canvas, spacious and elegant
    fig, ax = plt.subplots(figsize=(10.0, 6.2), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")
    ax.set_xlim(0, 10.0)
    ax.set_ylim(0, 6.2)

    # Main title: only the overall diagram title is bold; all internal box titles use regular weight
    ax.text(5.00, 5.90, "Kiến trúc tác nhân tự hành với vòng lặp giới hạn (≤ 3 bước)", 
            fontsize=15.0, fontweight="bold", ha="center", color="#1E3A8A", fontfamily="DejaVu Sans")
    ax.text(5.00, 5.58, "Mô hình 5 thành phần với vòng lặp quyết định và kiểm định an toàn", 
            fontsize=10.6, ha="center", color="#64748B", style="italic", fontfamily="DejaVu Sans")

    # 4 top boxes: y from 2.05 to 4.55 (height 2.50)
    # Box 1: Mục tiêu
    b1 = patches.FancyBboxPatch((0.25, 2.05), 2.05, 2.50, boxstyle="round,pad=0.10",
                                edgecolor="#3B82F6", facecolor="#F8FAFC", linewidth=1.4)
    ax.add_patch(b1)
    ax.text(1.275, 4.22, "1. Tiếp nhận mục tiêu", fontsize=11.6, fontweight="normal", ha="center", color="#1E40AF", fontfamily="DejaVu Sans")
    ax.text(1.275, 3.94, "(User Goal)", fontsize=10.0, ha="center", color="#3B82F6", style="italic", fontfamily="DejaVu Sans")
    ax.text(1.275, 2.96, "Tiếp nhận\nmục tiêu &\nphân tích\ný định", 
            fontsize=10.8, fontweight="normal", ha="center", color="#475569", linespacing=1.35, fontfamily="DejaVu Sans")

    # Arrow 1->2
    ax.annotate("", xy=(2.65, 3.30), xytext=(2.30, 3.30),
                arrowprops=dict(arrowstyle="-|>", color="#3B82F6", lw=1.6, mutation_scale=13))

    # Box 2: Kế hoạch
    b2 = patches.FancyBboxPatch((2.65, 2.05), 2.25, 2.50, boxstyle="round,pad=0.10",
                                edgecolor="#D97706", facecolor="#FFFBEB", linewidth=1.4)
    ax.add_patch(b2)
    ax.text(3.775, 4.22, "2. Lập kế hoạch", fontsize=11.6, fontweight="normal", ha="center", color="#B45309", fontfamily="DejaVu Sans")
    ax.text(3.775, 3.94, "(Dynamic Planner)", fontsize=10.0, ha="center", color="#D97706", style="italic", fontfamily="DejaVu Sans")
    ax.text(3.775, 2.96, "Phân rã\nChecklist\nđộng (LLM)\n(Tối đa ≤ 3)", 
            fontsize=10.8, fontweight="normal", ha="center", color="#475569", linespacing=1.35, fontfamily="DejaVu Sans")

    # Arrow 2->3
    ax.annotate("", xy=(5.25, 3.30), xytext=(4.90, 3.30),
                arrowprops=dict(arrowstyle="-|>", color="#D97706", lw=1.6, mutation_scale=13))

    # Box 3: Thực thi & Bộ nhớ
    b3 = patches.FancyBboxPatch((5.25, 2.05), 3.05, 2.50, boxstyle="round,pad=0.10",
                                edgecolor="#059669", facecolor="#F0FDF4", linewidth=1.4)
    ax.add_patch(b3)
    ax.text(6.775, 4.22, "3. Thực thi & Bộ nhớ", fontsize=11.6, fontweight="normal", ha="center", color="#047857", fontfamily="DejaVu Sans")
    ax.text(6.775, 3.94, "(Execution & Memory)", fontsize=10.0, ha="center", color="#059669", style="italic", fontfamily="DejaVu Sans")
    ax.text(5.50, 3.06, "• Bước 1: Luận điểm cốt lõi\n• Bước 2: Dàn ý chi tiết 4 phần\n• Bước 3: Hoàn thiện bài viết", 
            fontsize=10.5, fontweight="normal", ha="left", color="#475569", linespacing=1.35, fontfamily="DejaVu Sans")
    ax.text(6.775, 2.24, "Ngữ cảnh & Nhật ký từng bước", fontsize=9.8, fontweight="normal", ha="center", color="#059669", style="italic", fontfamily="DejaVu Sans")

    # Arrow 3->4
    ax.annotate("", xy=(8.65, 3.30), xytext=(8.30, 3.30),
                arrowprops=dict(arrowstyle="-|>", color="#059669", lw=1.6, mutation_scale=13))

    # Box 4: Kiểm định
    b4 = patches.FancyBboxPatch((8.65, 2.05), 1.15, 2.50, boxstyle="round,pad=0.10",
                                edgecolor="#DC2626", facecolor="#FEF2F2", linewidth=1.4)
    ax.add_patch(b4)
    ax.text(9.225, 4.22, "4. Kiểm định", fontsize=11.6, fontweight="normal", ha="center", color="#B91C1C", fontfamily="DejaVu Sans")
    ax.text(9.225, 3.94, "(Stop Gate)", fontsize=10.0, ha="center", color="#DC2626", style="italic", fontfamily="DejaVu Sans")
    ax.text(9.225, 3.04, "Đạt chuẩn\nmục tiêu?\nHoặc\nbước ≥ 3", 
            fontsize=10.5, fontweight="normal", ha="center", color="#475569", linespacing=1.30, fontfamily="DejaVu Sans")
    ax.text(9.225, 2.24, "Chốt chặn", fontsize=9.8, fontweight="normal", ha="center", color="#B91C1C", fontfamily="DejaVu Sans")

    # Loopback arrow: gentle curve from Box 4 top (9.225, 4.55) to Box 3 top (6.775, 4.55)
    # rad=0.11 produces a gentle arc peaking at y=4.82.
    ax.annotate("", xy=(6.775, 4.55), xytext=(9.225, 4.55),
                arrowprops=dict(arrowstyle="-|>", color="#64748B", lw=1.6, connectionstyle="arc3,rad=0.11", ls="--", mutation_scale=13))
    
    # Place loopback pill at y=5.20:
    # Pill bottom is at ~5.07. Clearance above arc apex (4.82) is a whopping 0.25 units (>50 px)!
    # Clearance below subtitle (5.58) is 0.38 units. ZERO OVERLAP!
    ax.text(8.00, 5.20, "Chưa đạt chuẩn & còn bước (Lặp)", fontsize=9.5, color="#475569", ha="center", va="center", fontweight="normal",
            fontfamily="DejaVu Sans", bbox=dict(boxstyle="round,pad=0.22", facecolor="#FFFFFF", edgecolor="#CBD5E1", lw=0.9))

    # Vertical downward arrow from Box 4 bottom (9.225, 2.05) to Box 5 top (9.225, 1.25)
    # Height of gap = 0.80 units (generous and clear!)
    ax.annotate("", xy=(9.225, 1.25), xytext=(9.225, 2.05),
                arrowprops=dict(arrowstyle="-|>", color="#1E40AF", lw=1.6, mutation_scale=13))
    
    # Place "Thỏa điều kiện dừng" badge cleanly at x=7.95, y=1.65 (centered in the 0.80 gap)
    # Badge right edge is at ~8.45. Arrow is at 9.225. Gap is 0.775 units (>150 px of pure whitespace)!
    ax.text(7.95, 1.65, "Thỏa điều kiện dừng", fontsize=9.5, color="#1E40AF", ha="center", va="center", fontweight="normal",
            fontfamily="DejaVu Sans", bbox=dict(boxstyle="round,pad=0.22", facecolor="#EFF6FF", edgecolor="#93C5FD", lw=0.9))

    # Box 5: Final Report (height 1.10: y from 0.15 to 1.25)
    b5 = patches.FancyBboxPatch((0.25, 0.15), 9.55, 1.10, boxstyle="round,pad=0.12",
                                edgecolor="#3B82F6", facecolor="#F8FAFC", linewidth=1.4)
    ax.add_patch(b5)
    ax.text(5.00, 0.98, "5. Báo cáo tổng kết & Sản phẩm nghiệm thu (Final Report)", 
            fontsize=11.6, fontweight="normal", ha="center", color="#1E40AF", fontfamily="DejaVu Sans")
    ax.text(5.00, 0.65, "• Kế hoạch ban đầu (Plan)     • Nhật ký kiểm toán (Audit Trail)     • Trạng thái kết thúc", 
            fontsize=10.4, ha="center", color="#475569", fontweight="normal", fontfamily="DejaVu Sans")
    ax.text(5.00, 0.35, "• Lý do dừng chi tiết     • Thẩm định chất lượng (TTR, Length, LLM Judge)     • Bài viết hoàn chỉnh", 
            fontsize=10.4, ha="center", color="#64748B", fontweight="normal", fontfamily="DejaVu Sans")

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
    ax.set_xlim(0, 10.2)
    ax.set_ylim(0, 5.8)

    # Main title: Title Case, refined bold
    ax.text(5.10, 5.45, "Luồng truyền dữ liệu & Điều kiện dừng qua các bước", 
            fontsize=15.0, fontweight="bold", ha="center", color="#1E3A8A", fontfamily="DejaVu Sans")
    ax.text(5.10, 5.14, "Cơ chế truyền ngữ cảnh (Context Memory) và rà soát điều kiện dừng ở từng bước", 
            fontsize=10.6, ha="center", color="#64748B", style="italic", fontfamily="DejaVu Sans")

    # 3 Step boxes with generous gaps
    # Step 1: width 2.40, x: 0.45 to 2.85
    s1 = patches.FancyBboxPatch((0.45, 2.50), 2.40, 2.30, boxstyle="round,pad=0.08",
                                edgecolor="#3B82F6", facecolor="#F8FAFC", linewidth=1.4)
    ax.add_patch(s1)
    ax.text(1.65, 4.45, "Bước 1", fontsize=11.6, fontweight="normal", ha="center", color="#1E40AF", fontfamily="DejaVu Sans")
    ax.text(1.65, 4.18, "Luận điểm cốt lõi", fontsize=10.8, fontweight="normal", ha="center", color="#1E40AF", fontfamily="DejaVu Sans")
    ax.text(1.65, 3.25, "• Tác vụ: research\n• Vào: Mục tiêu đề bài\n• Ra: Luận điểm chính", 
            fontsize=10.0, fontweight="normal", ha="center", color="#475569", linespacing=1.35, fontfamily="DejaVu Sans")

    # Arrow Step 1 -> Step 2
    ax.annotate("", xy=(3.90, 3.65), xytext=(2.85, 3.65),
                arrowprops=dict(arrowstyle="-|>", color="#3B82F6", lw=1.6, mutation_scale=13))
    ax.text(3.375, 3.90, "Ngữ cảnh", fontsize=9.2, color="#2563EB", ha="center", style="italic", fontfamily="DejaVu Sans")

    # Step 2: width 2.40, x: 3.90 to 6.30
    s2 = patches.FancyBboxPatch((3.90, 2.50), 2.40, 2.30, boxstyle="round,pad=0.08",
                                edgecolor="#D97706", facecolor="#FFFBEB", linewidth=1.4)
    ax.add_patch(s2)
    ax.text(5.10, 4.45, "Bước 2", fontsize=11.6, fontweight="normal", ha="center", color="#B45309", fontfamily="DejaVu Sans")
    ax.text(5.10, 4.18, "Dàn ý chi tiết", fontsize=10.8, fontweight="normal", ha="center", color="#B45309", fontfamily="DejaVu Sans")
    ax.text(5.10, 3.25, "• Tác vụ: outline\n• Vào: Luận điểm B1\n• Ra: Dàn ý 4 phần", 
            fontsize=10.0, fontweight="normal", ha="center", color="#475569", linespacing=1.35, fontfamily="DejaVu Sans")

    # Arrow Step 2 -> Step 3
    ax.annotate("", xy=(7.35, 3.65), xytext=(6.30, 3.65),
                arrowprops=dict(arrowstyle="-|>", color="#D97706", lw=1.6, mutation_scale=13))
    ax.text(6.825, 3.90, "Ngữ cảnh", fontsize=9.2, color="#D97706", ha="center", style="italic", fontfamily="DejaVu Sans")

    # Step 3: width 2.40, x: 7.35 to 9.75
    s3 = patches.FancyBboxPatch((7.35, 2.50), 2.40, 2.30, boxstyle="round,pad=0.08",
                                edgecolor="#059669", facecolor="#F0FDF4", linewidth=1.4)
    ax.add_patch(s3)
    ax.text(8.55, 4.45, "Bước 3", fontsize=11.6, fontweight="normal", ha="center", color="#047857", fontfamily="DejaVu Sans")
    ax.text(8.55, 4.18, "Hoàn thiện bài viết", fontsize=10.8, fontweight="normal", ha="center", color="#047857", fontfamily="DejaVu Sans")
    ax.text(8.55, 3.25, "• Tác vụ: generate\n• Vào: Dàn ý & bộ nhớ\n• Ra: Bài viết hoàn thiện", 
            fontsize=10.0, fontweight="normal", ha="center", color="#475569", linespacing=1.35, fontfamily="DejaVu Sans")

    # Stop Condition Evaluator Box
    eval_box = patches.FancyBboxPatch((0.45, 0.20), 9.30, 1.95, boxstyle="round,pad=0.10",
                                      edgecolor="#DC2626", facecolor="#FFFFFF", linewidth=1.3)
    ax.add_patch(eval_box)
    ax.text(5.10, 1.82, "Bộ đánh giá điều kiện dừng (Stop Condition Evaluator)", 
            fontsize=11.6, fontweight="normal", ha="center", color="#B91C1C", fontfamily="DejaVu Sans")

    # Col 1: Completed
    ax.text(1.65, 1.36, "Đạt chuẩn mục tiêu", fontsize=10.6, fontweight="normal", ha="center", color="#047857", fontfamily="DejaVu Sans")
    ax.text(1.65, 0.82, "Goal Achieved == True\nĐạt TTR, độ dài & LLM Judge", 
            fontsize=9.8, fontweight="normal", ha="center", color="#475569", linespacing=1.30, fontfamily="DejaVu Sans")
    ax.text(1.65, 0.42, "→ COMPLETED", fontsize=10.2, fontweight="normal", ha="center", color="#059669", fontfamily="DejaVu Sans")

    # Col 2: Budget exhausted
    ax.text(5.10, 1.36, "Hết ngân sách bước", fontsize=10.6, fontweight="normal", ha="center", color="#B45309", fontfamily="DejaVu Sans")
    ax.text(5.10, 0.82, "Steps Executed ≥ 3\nChốt chặn Bounded Loop", 
            fontsize=9.8, fontweight="normal", ha="center", color="#475569", linespacing=1.30, fontfamily="DejaVu Sans")
    ax.text(5.10, 0.42, "→ BUDGET_EXHAUSTED", fontsize=10.2, fontweight="normal", ha="center", color="#D97706", fontfamily="DejaVu Sans")

    # Col 3: Failed
    ax.text(8.55, 1.36, "Lỗi thực thi", fontsize=10.6, fontweight="normal", ha="center", color="#B91C1C", fontfamily="DejaVu Sans")
    ax.text(8.55, 0.82, "Execution Error\nThất bại sau 2 lần retry", 
            fontsize=9.8, fontweight="normal", ha="center", color="#475569", linespacing=1.30, fontfamily="DejaVu Sans")
    ax.text(8.55, 0.42, "→ FAILED", fontsize=10.2, fontweight="normal", ha="center", color="#DC2626", fontfamily="DejaVu Sans")

    ax.axis("off")
    img_path = os.path.join(OUTPUT_DIR, "state_flow_diagram.png")
    plt.tight_layout()
    plt.savefig(img_path, dpi=300, bbox_inches="tight", pad_inches=0.03)
    plt.close()
    print(f"Generated: {img_path}")


def generate_terminal_screenshot():
    # 8.2 x 3.65 canvas: 16 well-spaced lines, strictly NOTO SANS MONO LIGHT (thinner, elegant, non-bold)
    fig, ax = plt.subplots(figsize=(8.2, 3.65), dpi=300)
    fig.patch.set_facecolor("#181825")
    ax.set_facecolor("#181825")
    ax.set_xlim(0, 8.2)
    ax.set_ylim(0, 3.65)

    fp_reg = FontProperties(fname=NOTO_SANS_MONO_LIGHT, size=9.2)
    fp_header = FontProperties(fname=NOTO_SANS_MONO_LIGHT, size=8.4)

    # Measure exact char width dynamically for 100% regular font
    t_measure = ax.text(0, -10, "A" * 100, fontproperties=fp_reg)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    inv = ax.transData.inverted()
    bbox = t_measure.get_window_extent(renderer=renderer)
    char_w = bbox.transformed(inv).width / 100.0
    t_measure.remove()

    # Window chrome dots
    circle_red = patches.Circle((0.28, 3.42), 0.075, color="#F38BA8")
    circle_yellow = patches.Circle((0.50, 3.42), 0.075, color="#F9E2AF")
    circle_green = patches.Circle((0.72, 3.42), 0.075, color="#A6E3A1")
    ax.add_patch(circle_red)
    ax.add_patch(circle_yellow)
    ax.add_patch(circle_green)

    ax.text(1.02, 3.42, "thaipt@tinix-aiguru: ~/checklist-agent (python3 checklist_agent.py)", 
            color="#9399B2", ha="left", fontproperties=fp_header, va="center")

    div_line = "─" * 68

    # 100% REGULAR WEIGHT: Keywords are differentiated solely by harmonious color accents.
    lines = [
        # Line 1: Command prompt
        [("$ ", "#6C7086"), ("python3 code/checklist_agent.py", "#89DCEB")],
        # Line 2: Divider
        [(div_line, "#313244")],
        # Line 3: Agent start
        [("[AGENT] ", "#89B4FA"), ("Bắt đầu nhiệm vụ | tinix-lm:latest (Ollama)", "#BAC2DE")],
        # Line 4: Mission
        [("Mục tiêu: ", "#9399B2"), ("Viết bài chia sẻ ngắn giải thích RAG cho người mới.", "#CDD6F4")],
        # Line 5: Limit
        [("Giới hạn: ", "#9399B2"), ("Tối đa 3 bước thực thi (Bounded Execution Loop)", "#F9E2AF")],
        # Line 6: Divider
        [(div_line, "#313244")],
        # Line 7: Planner
        [("[PLANNER] ", "#94E2D5"), ("Khởi tạo checklist 3 bước động bằng LLM:", "#CDD6F4")],
        # Line 8: Step 1 plan
        [("  [1] (research_points) ", "#A6ADC8"), ("Luận điểm cốt lõi về RAG", "#BAC2DE")],
        # Line 9: Step 2 plan
        [("  [2] (outline)         ", "#A6ADC8"), ("Dàn ý 4 phần (mở, thân, ví dụ, kết)", "#BAC2DE")],
        # Line 10: Step 3 plan
        [("  [3] (generate)        ", "#A6ADC8"), ("Hoàn thiện bài viết theo dàn ý", "#BAC2DE")],
        # Line 11: Step 1 exec
        [("[BƯỚC 1] research_points -> [OK] ", "#A6ADC8"), ("COMPLETED", "#A6E3A1"), (" (3.176s)", "#6C7086")],
        # Line 12: Step 2 exec
        [("[BƯỚC 2] outline         -> [OK] ", "#A6ADC8"), ("COMPLETED", "#A6E3A1"), (" (3.356s)", "#6C7086")],
        # Line 13: Step 3 exec
        [("[BƯỚC 3] generate        -> [OK] ", "#A6ADC8"), ("COMPLETED", "#A6E3A1"), (" (7.380s | 1.872 ký tự)", "#6C7086")],
        # Line 14: LLM Judge
        [("  [LLM JUDGE] Thẩm định: correctness=1, quality=", "#94E2D5"), ("PASS", "#A6E3A1")],
        # Line 15: Stop condition
        [("[STOP CONDITION] Kích hoạt dừng: ", "#F38BA8"), ("Goal achieved", "#FAB387"), (" (Đạt chuẩn)", "#BAC2DE")],
        # Line 16: Divider
        [(div_line, "#313244")],
        # Line 17: Summary report
        [("BÁO CÁO: ", "#F9E2AF"), ("COMPLETED", "#A6E3A1"), 
         (" | 3/3 bước | 19.812s | TTR=0.43 | ", "#F9E2AF"), ("PASS", "#A6E3A1")],
    ]

    y_pos = 3.12
    y_step = 0.188

    for line_segments in lines:
        cur_x = 0.22
        for text, color in line_segments:
            ax.text(cur_x, y_pos, text, color=color, fontproperties=fp_reg, va="center")
            cur_x += len(text) * char_w
        y_pos -= y_step

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
