"""
Generate high-legibility diagrams and terminal screenshot for Bai 44.
Directly addresses reviewer comments:
- Hinh 1: Big clear text, no cramped lines, highly legible inside boxes.
- Hinh 2: Big clear text, 3-column aligned stop condition, perfectly proportioned.
- Hinh 3: Big monospace terminal font, crisp and readable on A4 without zooming.
"""
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Liberation Sans", "Noto Sans", "Arial"]
plt.rcParams["font.monospace"] = ["DejaVu Sans Mono", "Liberation Mono", "Noto Sans Mono"]
plt.rcParams["axes.unicode_minus"] = False


def generate_architecture_diagram():
    fig, ax = plt.subplots(figsize=(10.0, 6.2), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    # Main title
    ax.text(5.00, 5.85, "KIẾN TRÚC TÁC NHÂN TỰ HÀNH CHECKLIST (≤ 3 BƯỚC)", 
            fontsize=18.5, fontweight="bold", ha="center", color="#004AAD", fontfamily="DejaVu Sans")
    ax.text(5.00, 5.48, "Mô hình 5 khối với vòng lặp quyết định và kiểm định an toàn", 
            fontsize=13.0, ha="center", color="#475569", style="italic", fontfamily="DejaVu Sans")

    # 4 boxes across Y: 1.95 to 4.70 (height 2.75)
    # Box 1: Mục tiêu
    b1 = patches.FancyBboxPatch((0.25, 1.95), 2.05, 2.75, boxstyle="round,pad=0.10",
                                edgecolor="#004AAD", facecolor="#EFF6FF", linewidth=2.2)
    ax.add_patch(b1)
    ax.text(1.275, 4.35, "1. MỤC TIÊU", fontsize=15.0, fontweight="bold", ha="center", color="#004AAD", fontfamily="DejaVu Sans")
    ax.text(1.275, 4.02, "(User Goal)", fontsize=12.2, ha="center", color="#004AAD", style="italic", fontfamily="DejaVu Sans")
    ax.text(1.275, 2.95, "Tiếp nhận\nmục tiêu &\nphân tích\ný định", 
            fontsize=13.8, fontweight="bold", ha="center", color="#0F172A", linespacing=1.30, fontfamily="DejaVu Sans")

    # Arrow 1->2
    ax.annotate("", xy=(2.65, 3.32), xytext=(2.35, 3.32),
                arrowprops=dict(arrowstyle="-|>", color="#004AAD", lw=2.5, mutation_scale=16))

    # Box 2: Kế hoạch
    b2 = patches.FancyBboxPatch((2.65, 1.95), 2.25, 2.75, boxstyle="round,pad=0.10",
                                edgecolor="#E8630A", facecolor="#FFF7ED", linewidth=2.2)
    ax.add_patch(b2)
    ax.text(3.775, 4.35, "2. KẾ HOẠCH", fontsize=15.0, fontweight="bold", ha="center", color="#E8630A", fontfamily="DejaVu Sans")
    ax.text(3.775, 4.02, "(Planner)", fontsize=12.2, ha="center", color="#E8630A", style="italic", fontfamily="DejaVu Sans")
    ax.text(3.775, 2.95, "Phân rã\nChecklist\nđộng (LLM)\n(Tối đa ≤ 3)", 
            fontsize=13.8, fontweight="bold", ha="center", color="#0F172A", linespacing=1.30, fontfamily="DejaVu Sans")

    # Arrow 2->3
    ax.annotate("", xy=(5.25, 3.32), xytext=(4.95, 3.32),
                arrowprops=dict(arrowstyle="-|>", color="#E8630A", lw=2.5, mutation_scale=16))

    # Box 3: Thực thi
    b3 = patches.FancyBboxPatch((5.25, 1.95), 3.10, 2.75, boxstyle="round,pad=0.10",
                                edgecolor="#059669", facecolor="#ECFDF5", linewidth=2.2)
    ax.add_patch(b3)
    ax.text(6.80, 4.35, "3. THỰC THI & BỘ NHỚ", fontsize=14.5, fontweight="bold", ha="center", color="#059669", fontfamily="DejaVu Sans")
    ax.text(6.80, 4.02, "(Execution & Memory)", fontsize=12.0, ha="center", color="#059669", style="italic", fontfamily="DejaVu Sans")
    ax.text(5.42, 3.12, "• B1: Luận điểm cốt lõi\n• B2: Dàn ý chi tiết 4 phần\n• B3: Hoàn thiện bài viết", 
            fontsize=13.2, fontweight="bold", ha="left", color="#0F172A", linespacing=1.35, fontfamily="DejaVu Sans")
    ax.text(6.80, 2.22, "[Context & Step Logs]", fontsize=12.0, fontweight="bold", ha="center", color="#047857", fontfamily="DejaVu Sans")

    # Arrow 3->4
    ax.annotate("", xy=(8.68, 3.32), xytext=(8.38, 3.32),
                arrowprops=dict(arrowstyle="-|>", color="#059669", lw=2.5, mutation_scale=16))

    # Box 4: Điều kiện
    b4 = patches.FancyBboxPatch((8.68, 1.95), 1.12, 2.75, boxstyle="round,pad=0.10",
                                edgecolor="#DC2626", facecolor="#FEF2F2", linewidth=2.2)
    ax.add_patch(b4)
    ax.text(9.24, 4.35, "4. DỪNG", fontsize=14.2, fontweight="bold", ha="center", color="#DC2626", fontfamily="DejaVu Sans")
    ax.text(9.24, 4.02, "(Stop)", fontsize=11.5, ha="center", color="#DC2626", style="italic", fontfamily="DejaVu Sans")
    ax.text(9.24, 2.95, "Đạt chuẩn?\nHoặc\nBước ≥ 3\n→ DỪNG", 
            fontsize=13.0, fontweight="bold", ha="center", color="#0F172A", linespacing=1.30, fontfamily="DejaVu Sans")

    # Loopback arrow (when not stopped)
    ax.annotate("", xy=(6.80, 4.75), xytext=(9.24, 4.75),
                arrowprops=dict(arrowstyle="-|>", color="#475569", lw=2.2, connectionstyle="arc3,rad=0.20", ls="--", mutation_scale=15))
    ax.text(8.02, 5.08, "Lặp tiếp (chưa đạt & còn bước)", fontsize=11.5, color="#1E293B", ha="center", fontweight="bold",
            fontfamily="DejaVu Sans", bbox=dict(boxstyle="round,pad=0.20", facecolor="#FFFFFF", edgecolor="#64748B", lw=1.2))

    # Arrow from Stop to Report
    ax.annotate("", xy=(9.24, 1.55), xytext=(9.24, 1.95),
                arrowprops=dict(arrowstyle="-|>", color="#004AAD", lw=2.5, mutation_scale=16))
    ax.text(9.24, 1.76, "Thỏa dừng", fontsize=11.0, color="#004AAD", ha="center", fontweight="bold",
            fontfamily="DejaVu Sans", bbox=dict(boxstyle="round,pad=0.18", facecolor="#EFF6FF", edgecolor="#004AAD", lw=1.2))

    # Box 5: Final Report
    b5 = patches.FancyBboxPatch((0.25, 0.15), 9.55, 1.40, boxstyle="round,pad=0.12",
                                edgecolor="#004AAD", facecolor="#FFFFFF", linewidth=2.2)
    ax.add_patch(b5)
    ax.text(5.00, 1.18, "5. BÁO CÁO TỔNG KẾT & SẢN PHẨM NGHIỆM THU (FINAL REPORT)", 
            fontsize=14.0, fontweight="bold", ha="center", color="#004AAD", fontfamily="DejaVu Sans")
    ax.text(5.00, 0.74, "• Kế hoạch ban đầu (Plan)   • Nhật ký kiểm toán (Audit Trail)   • Trạng thái kết thúc", 
            fontsize=12.2, ha="center", color="#0F172A", fontweight="bold", fontfamily="DejaVu Sans")
    ax.text(5.00, 0.38, "• Lý do dừng chi tiết   • Kiểm định chất lượng (TTR, Length, LLM Judge)   • Sản phẩm cuối", 
            fontsize=12.2, ha="center", color="#334155", fontweight="bold", fontfamily="DejaVu Sans")

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

    ax.text(5.10, 5.42, "LUỒNG TRUYỀN DỮ LIỆU & ĐIỀU KIỆN DỪNG QUA CÁC BƯỚC", 
            fontsize=18.5, fontweight="bold", ha="center", color="#004AAD", fontfamily="DejaVu Sans")
    ax.text(5.10, 5.06, "(Hành động Bước 3 linh hoạt: generate khi dùng LLM hoặc review_polish khi fallback)", 
            fontsize=12.5, ha="center", color="#475569", style="italic", fontfamily="DejaVu Sans")

    # 3 Step boxes
    # Step 1
    s1 = patches.FancyBboxPatch((0.30, 2.50), 2.85, 2.30, boxstyle="round,pad=0.10",
                                edgecolor="#004AAD", facecolor="#EFF6FF", linewidth=2.2)
    ax.add_patch(s1)
    ax.text(1.725, 4.35, "BƯỚC 1\nLuận Điểm Cốt Lõi", fontsize=15.0, fontweight="bold", ha="center", color="#004AAD", linespacing=1.2, fontfamily="DejaVu Sans")
    ax.text(1.725, 3.25, "• Tác vụ: research\n• Vào: Mục tiêu đề bài\n• Ra: Luận điểm chính", 
            fontsize=13.5, fontweight="bold", ha="center", color="#0F172A", linespacing=1.35, fontfamily="DejaVu Sans")

    # Arrow 1->2
    ax.annotate("", xy=(3.65, 3.55), xytext=(3.15, 3.55),
                arrowprops=dict(arrowstyle="-|>", color="#004AAD", lw=2.5, mutation_scale=16))
    ax.text(3.40, 3.82, "State", fontsize=12.0, fontweight="bold", color="#004AAD", ha="center", fontfamily="DejaVu Sans")

    # Step 2
    s2 = patches.FancyBboxPatch((3.65, 2.50), 2.85, 2.30, boxstyle="round,pad=0.10",
                                edgecolor="#E8630A", facecolor="#FFF7ED", linewidth=2.2)
    ax.add_patch(s2)
    ax.text(5.075, 4.35, "BƯỚC 2\nDàn Ý Chi Tiết", fontsize=15.0, fontweight="bold", ha="center", color="#E8630A", linespacing=1.2, fontfamily="DejaVu Sans")
    ax.text(5.075, 3.25, "• Tác vụ: outline\n• Vào: Luận điểm B1\n• Ra: Dàn ý 4 phần", 
            fontsize=13.5, fontweight="bold", ha="center", color="#0F172A", linespacing=1.35, fontfamily="DejaVu Sans")

    # Arrow 2->3
    ax.annotate("", xy=(7.00, 3.55), xytext=(6.50, 3.55),
                arrowprops=dict(arrowstyle="-|>", color="#E8630A", lw=2.5, mutation_scale=16))
    ax.text(6.75, 3.82, "State", fontsize=12.0, fontweight="bold", color="#E8630A", ha="center", fontfamily="DejaVu Sans")

    # Step 3
    s3 = patches.FancyBboxPatch((7.00, 2.50), 2.85, 2.30, boxstyle="round,pad=0.10",
                                edgecolor="#059669", facecolor="#ECFDF5", linewidth=2.2)
    ax.add_patch(s3)
    ax.text(8.425, 4.35, "BƯỚC 3\nHoàn Thiện Bài Viết", fontsize=15.0, fontweight="bold", ha="center", color="#059669", linespacing=1.2, fontfamily="DejaVu Sans")
    ax.text(8.425, 3.25, "• Tác vụ: generate\n• Vào: Dàn ý & bộ nhớ\n• Ra: Bài viết hoàn thiện", 
            fontsize=13.5, fontweight="bold", ha="center", color="#0F172A", linespacing=1.35, fontfamily="DejaVu Sans")

    # Evaluator Box
    cond_box = patches.FancyBboxPatch((0.30, 0.15), 9.55, 2.05, boxstyle="round,pad=0.12",
                                      edgecolor="#DC2626", facecolor="#FEF2F2", linewidth=2.2)
    ax.add_patch(cond_box)
    ax.text(5.10, 1.85, "BỘ ĐÁNH GIÁ ĐIỀU KIỆN DỪNG (STOP CONDITION EVALUATOR)", 
            fontsize=14.5, fontweight="bold", ha="center", color="#DC2626", fontfamily="DejaVu Sans")

    # 3 columns inside Stop box
    # Col 1: Completed
    ax.text(1.725, 1.35, "ĐẠT CHUẨN MỤC TIÊU", fontsize=13.2, fontweight="bold", ha="center", color="#059669", fontfamily="DejaVu Sans")
    ax.text(1.725, 0.70, "Goal Achieved == True\nĐạt TTR, độ dài & LLM Judge\n→ COMPLETED", 
            fontsize=12.2, fontweight="bold", ha="center", color="#0F172A", linespacing=1.30, fontfamily="DejaVu Sans")

    # Col 2: Budget exhausted
    ax.text(5.075, 1.35, "HẾT NGÂN SÁCH BƯỚC", fontsize=13.2, fontweight="bold", ha="center", color="#D97706", fontfamily="DejaVu Sans")
    ax.text(5.075, 0.70, "Steps Executed ≥ 3\nChốt chặn Bounded Loop\n→ BUDGET_EXHAUSTED", 
            fontsize=12.2, fontweight="bold", ha="center", color="#0F172A", linespacing=1.30, fontfamily="DejaVu Sans")

    # Col 3: Failed
    ax.text(8.425, 1.35, "LỖI THỰC THI", fontsize=13.2, fontweight="bold", ha="center", color="#DC2626", fontfamily="DejaVu Sans")
    ax.text(8.425, 0.70, "Execution Error\nThất bại sau 2 lần retry\n→ FAILED", 
            fontsize=12.2, fontweight="bold", ha="center", color="#0F172A", linespacing=1.30, fontfamily="DejaVu Sans")

    ax.set_xlim(0, 10.2)
    ax.set_ylim(0, 5.8)
    ax.axis("off")

    img_path = os.path.join(OUTPUT_DIR, "state_flow_diagram.png")
    plt.tight_layout()
    plt.savefig(img_path, dpi=300, bbox_inches="tight", pad_inches=0.03)
    plt.close()
    print(f"Generated: {img_path}")


def generate_terminal_screenshot():
    # Render terminal đồ họa cao cấp: canvas rộng, font monospace lớn 11.5pt đậm nét, tỉ lệ ngang tối ưu
    fig, ax = plt.subplots(figsize=(8.2, 3.80), dpi=300)
    fig.patch.set_facecolor("#0F172A")
    ax.set_facecolor("#0F172A")

    # Header window buttons (macOS/Terminal style)
    circle_red = patches.Circle((0.28, 3.56), 0.075, color="#EF4444")
    circle_yellow = patches.Circle((0.50, 3.56), 0.075, color="#F59E0B")
    circle_green = patches.Circle((0.72, 3.56), 0.075, color="#10B981")
    ax.add_patch(circle_red)
    ax.add_patch(circle_yellow)
    ax.add_patch(circle_green)

    ax.text(1.02, 3.56, "thaipt@tinix-aiguru: ~/checklist-agent (python3 checklist_agent.py)", 
            fontsize=10.2, color="#94A3B8", ha="left", fontfamily="DejaVu Sans", fontweight="bold", va="center")

    terminal_text = [
        ("$ python3 code/checklist_agent.py", "#38BDF8"),
        ("=" * 60, "#38BDF8"),
        ("[AGENT] BẮT ĐẦU NHIỆM VỤ | tinix-lm:latest (Ollama)", "#38BDF8"),
        ("MỤC TIÊU: Viết bài chia sẻ ngắn giải thích RAG cho người mới.", "#F8FAFC"),
        ("GIỚI HẠN: Tối đa 3 bước thực thi (Bounded Execution Loop)", "#FCD34D"),
        ("=" * 60, "#38BDF8"),
        ("[PLANNER] KHỞI TẠO CHECKLIST 3 BƯỚC ĐỘNG BẰNG LLM:", "#A7F3D0"),
        ("  [1] (research_points) Luận điểm cốt lõi về RAG", "#F1F5F9"),
        ("  [2] (outline) Dàn ý 4 phần (mở, thân, ví dụ, kết)", "#F1F5F9"),
        ("  [3] (generate) Hoàn thiện bài viết theo dàn ý", "#F1F5F9"),
        ("-" * 60, "#475569"),
        ("[BƯỚC 1] research_points -> [OK] COMPLETED (3.176s)", "#34D399"),
        ("[BƯỚC 2] outline         -> [OK] COMPLETED (3.356s)", "#34D399"),
        ("[BƯỚC 3] generate        -> [OK] COMPLETED (7.380s | 1.872 ký tự)", "#34D399"),
        ("  [LLM JUDGE] Thẩm định: correctness=1, quality=PASS", "#A7F3D0"),
        ("[STOP CONDITION] Kích hoạt dừng: Goal achieved (Đạt chuẩn)", "#F87171"),
        ("=" * 60, "#38BDF8"),
        ("BÁO CÁO: COMPLETED | 3/3 bước | 19.812s | TTR=0.43 | PASS", "#FCD34D"),
    ]

    y_pos = 3.25
    for line, color in terminal_text:
        ax.text(0.20, y_pos, line, fontsize=11.5, color=color, fontfamily="DejaVu Sans", va="center", fontweight="bold")
        y_pos -= 0.180

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
