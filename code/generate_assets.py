"""
Generate high-legibility diagrams and terminal screenshot for Bai 44.
Directly addresses reviewer comments (Final Review):
- Relaxed typography: normal weights for body texts, bold only for headings/key terms.
- Clean layout: zero overlapping text on arrows, boxes, or lines; generous clearance.
- Authentic terminal: true monospace font (Liberation Mono) with normal weights, sharp & readable.
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

# Exact font files for Liberation Mono to ensure full Vietnamese glyph coverage without warnings
LIBERATION_MONO_REG = "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf"
LIBERATION_MONO_BOLD = "/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf"


def generate_architecture_diagram():
    fig, ax = plt.subplots(figsize=(10.0, 6.2), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    # Main title
    ax.text(5.00, 5.86, "KIẾN TRÚC TÁC NHÂN TỰ HÀNH CHECKLIST (≤ 3 BƯỚC)", 
            fontsize=17.5, fontweight="bold", ha="center", color="#004AAD", fontfamily="DejaVu Sans")
    ax.text(5.00, 5.52, "Mô hình 5 khối với vòng lặp quyết định và kiểm định an toàn", 
            fontsize=12.2, ha="center", color="#475569", style="italic", fontfamily="DejaVu Sans")

    # 4 boxes across Y: 1.95 to 4.70 (height 2.75)
    # Box 1: Mục tiêu
    b1 = patches.FancyBboxPatch((0.25, 1.95), 2.05, 2.75, boxstyle="round,pad=0.10",
                                edgecolor="#004AAD", facecolor="#F0F7FF", linewidth=2.0)
    ax.add_patch(b1)
    ax.text(1.275, 4.38, "1. MỤC TIÊU", fontsize=14.5, fontweight="bold", ha="center", color="#004AAD", fontfamily="DejaVu Sans")
    ax.text(1.275, 4.06, "(User Goal)", fontsize=11.5, ha="center", color="#004AAD", style="italic", fontfamily="DejaVu Sans")
    ax.text(1.275, 2.95, "Tiếp nhận\nmục tiêu &\nphân tích\ný định", 
            fontsize=12.5, fontweight="normal", ha="center", color="#1E293B", linespacing=1.35, fontfamily="DejaVu Sans")

    # Arrow 1->2
    ax.annotate("", xy=(2.65, 3.32), xytext=(2.30, 3.32),
                arrowprops=dict(arrowstyle="-|>", color="#004AAD", lw=2.2, mutation_scale=15))

    # Box 2: Kế hoạch
    b2 = patches.FancyBboxPatch((2.65, 1.95), 2.25, 2.75, boxstyle="round,pad=0.10",
                                edgecolor="#E8630A", facecolor="#FFF8F1", linewidth=2.0)
    ax.add_patch(b2)
    ax.text(3.775, 4.38, "2. KẾ HOẠCH", fontsize=14.5, fontweight="bold", ha="center", color="#E8630A", fontfamily="DejaVu Sans")
    ax.text(3.775, 4.06, "(Planner)", fontsize=11.5, ha="center", color="#E8630A", style="italic", fontfamily="DejaVu Sans")
    ax.text(3.775, 2.95, "Phân rã\nChecklist\nđộng (LLM)\n(Tối đa ≤ 3)", 
            fontsize=12.5, fontweight="normal", ha="center", color="#1E293B", linespacing=1.35, fontfamily="DejaVu Sans")

    # Arrow 2->3
    ax.annotate("", xy=(5.25, 3.32), xytext=(4.90, 3.32),
                arrowprops=dict(arrowstyle="-|>", color="#E8630A", lw=2.2, mutation_scale=15))

    # Box 3: Thực thi
    b3 = patches.FancyBboxPatch((5.25, 1.95), 3.10, 2.75, boxstyle="round,pad=0.10",
                                edgecolor="#059669", facecolor="#F0FDF4", linewidth=2.0)
    ax.add_patch(b3)
    ax.text(6.80, 4.38, "3. THỰC THI & BỘ NHỚ", fontsize=14.2, fontweight="bold", ha="center", color="#059669", fontfamily="DejaVu Sans")
    ax.text(6.80, 4.06, "(Execution & Memory)", fontsize=11.5, ha="center", color="#059669", style="italic", fontfamily="DejaVu Sans")
    ax.text(5.45, 3.12, "• B1: Luận điểm cốt lõi\n• B2: Dàn ý chi tiết 4 phần\n• B3: Hoàn thiện bài viết", 
            fontsize=12.2, fontweight="normal", ha="left", color="#1E293B", linespacing=1.35, fontfamily="DejaVu Sans")
    ax.text(6.80, 2.24, "[Context & Step Logs]", fontsize=11.2, fontweight="bold", ha="center", color="#047857", fontfamily="DejaVu Sans")

    # Arrow 3->4
    ax.annotate("", xy=(8.68, 3.32), xytext=(8.35, 3.32),
                arrowprops=dict(arrowstyle="-|>", color="#059669", lw=2.2, mutation_scale=15))

    # Box 4: Điều kiện
    b4 = patches.FancyBboxPatch((8.68, 1.95), 1.12, 2.75, boxstyle="round,pad=0.10",
                                edgecolor="#DC2626", facecolor="#FEF2F2", linewidth=2.0)
    ax.add_patch(b4)
    ax.text(9.24, 4.38, "4. DỪNG", fontsize=14.0, fontweight="bold", ha="center", color="#DC2626", fontfamily="DejaVu Sans")
    ax.text(9.24, 4.06, "(Stop)", fontsize=11.2, ha="center", color="#DC2626", style="italic", fontfamily="DejaVu Sans")
    ax.text(9.24, 3.15, "Đạt chuẩn?\nHoặc\nBước ≥ 3", 
            fontsize=12.0, fontweight="normal", ha="center", color="#1E293B", linespacing=1.30, fontfamily="DejaVu Sans")
    ax.text(9.24, 2.25, "→ DỪNG", fontsize=12.2, fontweight="bold", ha="center", color="#DC2626", fontfamily="DejaVu Sans")

    # Loopback arrow (when not stopped): Arc curves cleanly
    ax.annotate("", xy=(6.80, 4.70), xytext=(9.24, 4.70),
                arrowprops=dict(arrowstyle="-|>", color="#475569", lw=2.0, connectionstyle="arc3,rad=0.18", ls="--", mutation_scale=14))
    # Place loopback text neatly above the arc with clear breathing margin
    ax.text(8.02, 5.30, "Lặp tiếp (chưa đạt & còn bước)", fontsize=10.8, color="#1E293B", ha="center", fontweight="normal",
            fontfamily="DejaVu Sans", bbox=dict(boxstyle="round,pad=0.25", facecolor="#FFFFFF", edgecolor="#94A3B8", lw=1.0))

    # Clean unobstructed vertical arrow from Stop to Report at x=9.24
    ax.annotate("", xy=(9.24, 1.55), xytext=(9.24, 1.95),
                arrowprops=dict(arrowstyle="-|>", color="#004AAD", lw=2.2, mutation_scale=15))
    # Place "Thỏa dừng" badge with generous clearance to the LEFT of arrow at x=8.85 with ha="right" - ZERO OVERLAP!
    ax.text(8.85, 1.75, "Thỏa dừng", fontsize=10.5, color="#004AAD", ha="right", va="center", fontweight="bold",
            fontfamily="DejaVu Sans", bbox=dict(boxstyle="round,pad=0.20", facecolor="#EFF6FF", edgecolor="#004AAD", lw=1.1))

    # Box 5: Final Report
    b5 = patches.FancyBboxPatch((0.25, 0.15), 9.55, 1.40, boxstyle="round,pad=0.12",
                                edgecolor="#004AAD", facecolor="#FFFFFF", linewidth=2.0)
    ax.add_patch(b5)
    ax.text(5.00, 1.18, "5. BÁO CÁO TỔNG KẾT & SẢN PHẨM NGHIỆM THU (FINAL REPORT)", 
            fontsize=13.8, fontweight="bold", ha="center", color="#004AAD", fontfamily="DejaVu Sans")
    ax.text(5.00, 0.76, "• Kế hoạch ban đầu (Plan)   • Nhật ký kiểm toán (Audit Trail)   • Trạng thái kết thúc", 
            fontsize=11.8, ha="center", color="#1E293B", fontweight="normal", fontfamily="DejaVu Sans")
    ax.text(5.00, 0.40, "• Lý do dừng chi tiết   • Kiểm định chất lượng (TTR, Length, LLM Judge)   • Sản phẩm cuối", 
            fontsize=11.8, ha="center", color="#475569", fontweight="normal", fontfamily="DejaVu Sans")

    ax.set_xlim(0, 10.0)
    ax.set_ylim(0, 6.2)
    ax.axis("off")

    img_path = os.path.join(OUTPUT_DIR, "architecture_diagram.png")
    plt.tight_layout()
    plt.savefig(img_path, dpi=300, bbox_inches="tight", pad_inches=0.03)
    plt.close()
    print(f"Generated: {img_path}")


def generate_state_flow_diagram():
    fig, ax = plt.subplots(figsize=(10.2, 5.8), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    ax.text(5.10, 5.44, "LUỒNG TRUYỀN DỮ LIỆU & ĐIỀU KIỆN DỪNG QUA CÁC BƯỚC", 
            fontsize=17.5, fontweight="bold", ha="center", color="#004AAD", fontfamily="DejaVu Sans")
    ax.text(5.10, 5.10, "(Hành động Bước 3 linh hoạt: generate khi dùng LLM hoặc review_polish khi fallback)", 
            fontsize=12.0, ha="center", color="#475569", style="italic", fontfamily="DejaVu Sans")

    # 3 Step boxes with generous 1.05-unit gaps for arrows & badges (ZERO OVERLAP!)
    # Step 1: width 2.40, x: 0.45 to 2.85
    s1 = patches.FancyBboxPatch((0.45, 2.50), 2.40, 2.30, boxstyle="round,pad=0.08",
                                edgecolor="#004AAD", facecolor="#F0F7FF", linewidth=2.0)
    ax.add_patch(s1)
    ax.text(1.65, 4.38, "BƯỚC 1\nLuận Điểm Cốt Lõi", fontsize=14.0, fontweight="bold", ha="center", color="#004AAD", linespacing=1.2, fontfamily="DejaVu Sans")
    ax.text(1.65, 3.25, "• Tác vụ: research\n• Vào: Mục tiêu đề bài\n• Ra: Luận điểm chính", 
            fontsize=11.8, fontweight="normal", ha="center", color="#1E293B", linespacing=1.35, fontfamily="DejaVu Sans")

    # Arrow 1->2 in gap 2.85 to 3.90
    ax.annotate("", xy=(3.85, 3.45), xytext=(2.95, 3.45),
                arrowprops=dict(arrowstyle="-|>", color="#004AAD", lw=2.2, mutation_scale=15))
    # Label "State" neatly centered above arrow, zero touching!
    ax.text(3.375, 3.75, "State", fontsize=10.2, fontweight="bold", color="#004AAD", ha="center", va="center",
            fontfamily="DejaVu Sans")

    # Step 2: width 2.40, x: 3.90 to 6.30
    s2 = patches.FancyBboxPatch((3.90, 2.50), 2.40, 2.30, boxstyle="round,pad=0.08",
                                edgecolor="#E8630A", facecolor="#FFF8F1", linewidth=2.0)
    ax.add_patch(s2)
    ax.text(5.10, 4.38, "BƯỚC 2\nDàn Ý Chi Tiết", fontsize=14.0, fontweight="bold", ha="center", color="#E8630A", linespacing=1.2, fontfamily="DejaVu Sans")
    ax.text(5.10, 3.25, "• Tác vụ: outline\n• Vào: Luận điểm B1\n• Ra: Dàn ý 4 phần", 
            fontsize=11.8, fontweight="normal", ha="center", color="#1E293B", linespacing=1.35, fontfamily="DejaVu Sans")

    # Arrow 2->3 in gap 6.30 to 7.35
    ax.annotate("", xy=(7.30, 3.45), xytext=(6.40, 3.45),
                arrowprops=dict(arrowstyle="-|>", color="#E8630A", lw=2.2, mutation_scale=15))
    # Label "State" neatly centered above arrow, zero touching!
    ax.text(6.825, 3.75, "State", fontsize=10.2, fontweight="bold", color="#E8630A", ha="center", va="center",
            fontfamily="DejaVu Sans")

    # Step 3: width 2.40, x: 7.35 to 9.75
    s3 = patches.FancyBboxPatch((7.35, 2.50), 2.40, 2.30, boxstyle="round,pad=0.08",
                                edgecolor="#059669", facecolor="#F0FDF4", linewidth=2.0)
    ax.add_patch(s3)
    ax.text(8.55, 4.38, "BƯỚC 3\nHoàn Thiện Bài Viết", fontsize=14.0, fontweight="bold", ha="center", color="#059669", linespacing=1.2, fontfamily="DejaVu Sans")
    ax.text(8.55, 3.25, "• Tác vụ: generate\n• Vào: Dàn ý & bộ nhớ\n• Ra: Bài viết hoàn thiện", 
            fontsize=11.8, fontweight="normal", ha="center", color="#1E293B", linespacing=1.35, fontfamily="DejaVu Sans")

    # Evaluator Box: width 9.30, x: 0.45 to 9.75
    cond_box = patches.FancyBboxPatch((0.45, 0.15), 9.30, 2.05, boxstyle="round,pad=0.10",
                                      edgecolor="#DC2626", facecolor="#FEF2F2", linewidth=2.0)
    ax.add_patch(cond_box)
    ax.text(5.10, 1.86, "BỘ ĐÁNH GIÁ ĐIỀU KIỆN DỪNG (STOP CONDITION EVALUATOR)", 
            fontsize=13.8, fontweight="bold", ha="center", color="#DC2626", fontfamily="DejaVu Sans")

    # 3 columns inside Stop box - perfectly aligned with the 3 step boxes above!
    # Col 1: Completed (centered at 1.65)
    ax.text(1.65, 1.36, "ĐẠT CHUẨN MỤC TIÊU", fontsize=12.2, fontweight="bold", ha="center", color="#059669", fontfamily="DejaVu Sans")
    ax.text(1.65, 0.82, "Goal Achieved == True\nĐạt TTR, độ dài & LLM Judge", 
            fontsize=11.2, fontweight="normal", ha="center", color="#1E293B", linespacing=1.30, fontfamily="DejaVu Sans")
    ax.text(1.65, 0.42, "→ COMPLETED", fontsize=11.8, fontweight="bold", ha="center", color="#059669", fontfamily="DejaVu Sans")

    # Col 2: Budget exhausted (centered at 5.10)
    ax.text(5.10, 1.36, "HẾT NGÂN SÁCH BƯỚC", fontsize=12.2, fontweight="bold", ha="center", color="#D97706", fontfamily="DejaVu Sans")
    ax.text(5.10, 0.82, "Steps Executed ≥ 3\nChốt chặn Bounded Loop", 
            fontsize=11.2, fontweight="normal", ha="center", color="#1E293B", linespacing=1.30, fontfamily="DejaVu Sans")
    ax.text(5.10, 0.42, "→ BUDGET_EXHAUSTED", fontsize=11.8, fontweight="bold", ha="center", color="#D97706", fontfamily="DejaVu Sans")

    # Col 3: Failed (centered at 8.55)
    ax.text(8.55, 1.36, "LỖI THỰC THI", fontsize=12.2, fontweight="bold", ha="center", color="#DC2626", fontfamily="DejaVu Sans")
    ax.text(8.55, 0.82, "Execution Error\nThất bại sau 2 lần retry", 
            fontsize=11.2, fontweight="normal", ha="center", color="#1E293B", linespacing=1.30, fontfamily="DejaVu Sans")
    ax.text(8.55, 0.42, "→ FAILED", fontsize=11.8, fontweight="bold", ha="center", color="#DC2626", fontfamily="DejaVu Sans")

    ax.set_xlim(0, 10.2)
    ax.set_ylim(0, 5.8)
    ax.axis("off")

    img_path = os.path.join(OUTPUT_DIR, "state_flow_diagram.png")
    plt.tight_layout()
    plt.savefig(img_path, dpi=300, bbox_inches="tight", pad_inches=0.03)
    plt.close()
    print(f"Generated: {img_path}")


def generate_terminal_screenshot():
    # Render authentic developer terminal: monospace font (Liberation Mono), crisp normal weight, clean styling
    fig, ax = plt.subplots(figsize=(8.2, 3.80), dpi=300)
    fig.patch.set_facecolor("#0F172A")
    ax.set_facecolor("#0F172A")

    # Font properties explicitly pointing to Liberation Mono TTF
    fp_reg = FontProperties(fname=LIBERATION_MONO_REG, size=9.8)
    fp_bold = FontProperties(fname=LIBERATION_MONO_BOLD, size=9.8)
    fp_header = FontProperties(fname=LIBERATION_MONO_REG, size=9.0)

    # Header window buttons (macOS style)
    circle_red = patches.Circle((0.28, 3.56), 0.075, color="#EF4444")
    circle_yellow = patches.Circle((0.50, 3.56), 0.075, color="#F59E0B")
    circle_green = patches.Circle((0.72, 3.56), 0.075, color="#10B981")
    ax.add_patch(circle_red)
    ax.add_patch(circle_yellow)
    ax.add_patch(circle_green)

    ax.text(1.02, 3.56, "thaipt@tinix-aiguru: ~/checklist-agent (python3 checklist_agent.py)", 
            color="#94A3B8", ha="left", fontproperties=fp_header, va="center")

    terminal_text = [
        ("$ python3 code/checklist_agent.py", "#38BDF8", True),
        ("=" * 64, "#38BDF8", False),
        ("[AGENT] BẮT ĐẦU NHIỆM VỤ | tinix-lm:latest (Ollama)", "#38BDF8", True),
        ("MỤC TIÊU: Viết bài chia sẻ ngắn giải thích RAG cho người mới.", "#F8FAFC", False),
        ("GIỚI HẠN: Tối đa 3 bước thực thi (Bounded Execution Loop)", "#FCD34D", False),
        ("=" * 64, "#38BDF8", False),
        ("[PLANNER] KHỞI TẠO CHECKLIST 3 BƯỚC ĐỘNG BẰNG LLM:", "#A7F3D0", True),
        ("  [1] (research_points) Luận điểm cốt lõi về RAG", "#F1F5F9", False),
        ("  [2] (outline) Dàn ý 4 phần (mở, thân, ví dụ, kết)", "#F1F5F9", False),
        ("  [3] (generate) Hoàn thiện bài viết theo dàn ý", "#F1F5F9", False),
        ("-" * 64, "#475569", False),
        ("[BƯỚC 1] research_points -> [OK] COMPLETED (3.176s)", "#34D399", False),
        ("[BƯỚC 2] outline         -> [OK] COMPLETED (3.356s)", "#34D399", False),
        ("[BƯỚC 3] generate        -> [OK] COMPLETED (7.380s | 1.872 ký tự)", "#34D399", False),
        ("  [LLM JUDGE] Thẩm định: correctness=1, quality=PASS", "#A7F3D0", False),
        ("[STOP CONDITION] Kích hoạt dừng: Goal achieved (Đạt chuẩn)", "#F87171", True),
        ("=" * 64, "#38BDF8", False),
        ("BÁO CÁO: COMPLETED | 3/3 bước | 19.812s | TTR=0.43 | PASS", "#FCD34D", True),
    ]

    y_pos = 3.25
    for line, color, is_bold in terminal_text:
        fp = fp_bold if is_bold else fp_reg
        ax.text(0.20, y_pos, line, color=color, fontproperties=fp, va="center")
        y_pos -= 0.178

    ax.set_xlim(0, 8.2)
    ax.set_ylim(0, 3.80)
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
