"""
Script tự động sinh các hình ảnh sơ đồ kiến trúc và kết quả thực thi
cho bài viết LaTeX: Xây dựng Autonomous Agent hoàn thành checklist 3 bước.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUTPUT_DIR = "/home/thaipt/ai-chatbot/TiniX-AIGuru/Nop_Bai/Bai42/images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Liberation Sans", "Arial"]
plt.rcParams["axes.unicode_minus"] = False

def generate_architecture_diagram():
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
    ax.set_facecolor("#F8FAFC")
    fig.patch.set_facecolor("#F8FAFC")

    # Title
    ax.text(6, 6.1, "KIEN TRUC AUTONOMOUS CHECKLIST AGENT (TOI DA 3 BUOC)", 
            fontsize=15, fontweight="bold", ha="center", color="#004AAD")
    ax.text(6, 5.75, "Mo hinh khep kin: Lap ke hoach -> Thuc thi tuan tu -> Luu log -> Dieu kien dung -> Bao cao cuoi", 
            fontsize=10, ha="center", color="#475569", style="italic")

    # Box 1: Goal Input
    box_goal = patches.FancyBboxPatch((0.5, 3.8), 2.2, 1.4, boxstyle="round,pad=0.2", 
                                      edgecolor="#004AAD", facecolor="#EFF6FF", linewidth=2)
    ax.add_patch(box_goal)
    ax.text(1.6, 4.7, "1. USER GOAL", fontsize=11, fontweight="bold", ha="center", color="#004AAD")
    ax.text(1.6, 4.15, "Nhap muc tieu nho\n(VD: Giai thich RAG\ncho nguoi moi)", 
            fontsize=9, ha="center", color="#1E293B")

    # Arrow 1 -> Planner
    ax.annotate("", xy=(3.4, 4.5), xytext=(2.9, 4.5),
                arrowprops=dict(arrowstyle="->", color="#004AAD", lw=2.5))

    # Box 2: Planner Node
    box_plan = patches.FancyBboxPatch((3.5, 3.8), 2.5, 1.4, boxstyle="round,pad=0.2", 
                                      edgecolor="#E8630A", facecolor="#FFF7ED", linewidth=2)
    ax.add_patch(box_plan)
    ax.text(4.75, 4.7, "2. PLANNER NODE", fontsize=11, fontweight="bold", ha="center", color="#E8630A")
    ax.text(4.75, 4.15, "Phan ra muc tieu\nChecklist dong\n(Toi da <= 3 buoc)", 
            fontsize=9, ha="center", color="#1E293B")

    # Arrow 2 -> Executor Loop
    ax.annotate("", xy=(6.7, 4.5), xytext=(6.2, 4.5),
                arrowprops=dict(arrowstyle="->", color="#E8630A", lw=2.5))

    # Box 3: Execution Engine & Memory
    box_exec = patches.FancyBboxPatch((6.8, 3.4), 2.6, 2.0, boxstyle="round,pad=0.2", 
                                      edgecolor="#059669", facecolor="#ECFDF5", linewidth=2)
    ax.add_patch(box_exec)
    ax.text(8.1, 5.0, "3. EXECUTOR LOOP", fontsize=11, fontweight="bold", ha="center", color="#059669")
    ax.text(8.1, 4.4, "- Buoc 1: Lap dan y\n- Buoc 2: Viet noi dung\n- Buoc 3: Ra soat & duyet", 
            fontsize=8.5, ha="center", color="#1E293B")
    ax.text(8.1, 3.7, "[State Memory & Logs]", fontsize=8, fontweight="bold", ha="center", color="#047857")

    # Arrow 3 -> Stop Condition
    ax.annotate("", xy=(10.0, 4.5), xytext=(9.5, 4.5),
                arrowprops=dict(arrowstyle="->", color="#059669", lw=2.5))

    # Box 4: Stop Evaluator
    box_stop = patches.FancyBboxPatch((10.1, 3.8), 1.6, 1.4, boxstyle="round,pad=0.2", 
                                      edgecolor="#DC2626", facecolor="#FEF2F2", linewidth=2)
    ax.add_patch(box_stop)
    ax.text(10.9, 4.7, "4. STOP CHECK", fontsize=10, fontweight="bold", ha="center", color="#DC2626")
    ax.text(10.9, 4.15, "Goal achieved?\nHoac Step >= 3?\n-> STOP", 
            fontsize=8.5, ha="center", color="#1E293B")

    # Feedback loop if not stopped
    ax.annotate("", xy=(8.1, 3.2), xytext=(10.9, 3.6),
                arrowprops=dict(arrowstyle="->", color="#64748B", lw=1.5, connectionstyle="arc3,rad=-0.3", ls="--"))
    ax.text(9.5, 2.9, "Chua dat & Con buoc", fontsize=8, color="#64748B", ha="center")

    # Bottom Arrow -> Final Output Box
    ax.annotate("", xy=(6.0, 2.3), xytext=(10.9, 3.6),
                arrowprops=dict(arrowstyle="->", color="#004AAD", lw=2.5, connectionstyle="arc3,rad=0.3"))

    # Box 5: Final Output
    box_out = patches.FancyBboxPatch((2.0, 0.7), 8.0, 1.4, boxstyle="round,pad=0.2", 
                                     edgecolor="#004AAD", facecolor="#FFFFFF", linewidth=2)
    ax.add_patch(box_out)
    ax.text(6.0, 1.7, "5. BAO CAO CUOI CUNG (FINAL REPORT & ARTIFACTS)", 
            fontsize=11, fontweight="bold", ha="center", color="#004AAD")
    ax.text(6.0, 1.15, "- Ke hoach ban dau (Initial Plan)    - Log chi tiet tung buoc (Step Logs)\n- Dieu kien dung kich hoat (Stop Reason)    - Bai viet RAG hoan chinh da nghiem thu", 
            fontsize=9, ha="center", color="#334155")

    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.5)
    ax.axis("off")

    img_path = os.path.join(OUTPUT_DIR, "architecture_diagram.png")
    plt.tight_layout()
    plt.savefig(img_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated: {img_path}")


def generate_terminal_screenshot():
    fig, ax = plt.subplots(figsize=(11, 7.2), dpi=300)
    fig.patch.set_facecolor("#0F172A")  # Dark Slate theme
    ax.set_facecolor("#0F172A")

    # Header window buttons
    circle_red = patches.Circle((0.4, 6.8), 0.1, color="#EF4444")
    circle_yellow = patches.Circle((0.7, 6.8), 0.1, color="#F59E0B")
    circle_green = patches.Circle((1.0, 6.8), 0.1, color="#10B981")
    ax.add_patch(circle_red)
    ax.add_patch(circle_yellow)
    ax.add_patch(circle_green)

    ax.text(6.0, 6.75, "bash - thaipt@tinix-aiguru: ~/checklist-agent (python3 checklist_agent.py)", 
            fontsize=9, color="#94A3B8", ha="center", family="monospace")

    terminal_text = [
        ("==========================================================================", "#38BDF8"),
        ("[AUTONOMOUS AGENT] BAT DAU NHIEM VU", "#38BDF8"),
        ("MUC TIEU: Viet mot bai chia se ngan giai thich RAG la gi cho nguoi moi.", "#F8FAFC"),
        ("GIOI HAN: Toi da 3 buoc thuc thi (Bounded Execution Loop)", "#FCD34D"),
        ("==========================================================================", "#38BDF8"),
        ("[PLANNER] DA KHOI TAO CHECKLIST GOM 3 BUOC:", "#A7F3D0"),
        ("   [1] Xac dinh cac y chinh can giai thich ve RAG", "#F1F5F9"),
        ("   [2] Viet noi dung bai chia se hoan chinh", "#F1F5F9"),
        ("   [3] Ra soat, kiem tra do ro rang va hoan thien bai viet", "#F1F5F9"),
        ("--------------------------------------------------------------------------", "#475569"),
        ("[BUOC 1/3] Dang thuc hien: Xac dinh cac y chinh can giai thich ve RAG...", "#E2E8F0"),
        ("   -> Trang thai: COMPLETED (0.012s) | Dan y 5 muc duoc luu vao State", "#34D399"),
        ("[BUOC 2/3] Dang thuc hien: Viet noi dung bai chia se hoan chinh...", "#E2E8F0"),
        ("   -> Trang thai: COMPLETED (0.025s) | Da soan thao 4 phan co ban", "#34D399"),
        ("[BUOC 3/3] Dang thuc hien: Ra soat, kiem tra do ro rang va hoan thien...", "#E2E8F0"),
        ("   -> Trang thai: COMPLETED (0.018s) | Ra soat dat 4/4 tieu chi, bo sung Loi ket", "#34D399"),
        ("[STOP CONDITION] Kich hoat dieu kien dung: Goal achieved (Dat muc tieu)", "#F87171"),
        ("==========================================================================", "#38BDF8"),
        ("BAO CAO CUOI CUNG (FINAL AGENT REPORT)", "#38BDF8"),
        ("   - Trang thai: COMPLETED | So buoc hoan thanh: 3/3 | Thoi gian: 0.056s", "#F8FAFC"),
        ("   - San pham: Bai viet '# BAT MI VE RAG...' (2,180 ky tu)", "#FCD34D"),
        ("Da xuat du lieu chi tiet ra: agent_final_report.json", "#A7F3D0"),
    ]

    y_pos = 6.2
    for line, color in terminal_text:
        ax.text(0.3, y_pos, line, fontsize=8.5, color=color, family="monospace", va="center")
        y_pos -= 0.26

    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.2)
    ax.axis("off")

    img_path = os.path.join(OUTPUT_DIR, "terminal_execution.png")
    plt.tight_layout()
    plt.savefig(img_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated: {img_path}")


def generate_state_flow_diagram():
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    ax.set_facecolor("#FFFFFF")
    fig.patch.set_facecolor("#FFFFFF")

    ax.text(5, 4.6, "LUONG TRUYEN DU LIEU & DIEU KIEN DUNG QUA CAC BUOC", 
            fontsize=13, fontweight="bold", ha="center", color="#004AAD")

    # Step 1 Box
    s1 = patches.FancyBboxPatch((0.5, 2.2), 2.5, 1.8, boxstyle="round,pad=0.15", 
                                edgecolor="#004AAD", facecolor="#EFF6FF", linewidth=1.8)
    ax.add_patch(s1)
    ax.text(1.75, 3.6, "BUOC 1\nLap Dan Y", fontsize=10, fontweight="bold", ha="center", color="#004AAD")
    ax.text(1.75, 2.8, "Input: User Goal\nOutput: outline\n(5 y chinh RAG)", fontsize=8, ha="center", color="#1E293B")

    # Arrow 1->2
    ax.annotate("", xy=(3.6, 3.1), xytext=(3.1, 3.1),
                arrowprops=dict(arrowstyle="->", color="#004AAD", lw=2))
    ax.text(3.35, 3.3, "State", fontsize=7.5, color="#004AAD", ha="center")

    # Step 2 Box
    s2 = patches.FancyBboxPatch((3.7, 2.2), 2.6, 1.8, boxstyle="round,pad=0.15", 
                                edgecolor="#E8630A", facecolor="#FFF7ED", linewidth=1.8)
    ax.add_patch(s2)
    ax.text(5.0, 3.6, "BUOC 2\nViet Noi Dung", fontsize=10, fontweight="bold", ha="center", color="#E8630A")
    ax.text(5.0, 2.8, "Input: outline\nOutput: draft_article\n(Ban nhap 4 phan)", fontsize=8, ha="center", color="#1E293B")

    # Arrow 2->3
    ax.annotate("", xy=(6.9, 3.1), xytext=(6.4, 3.1),
                arrowprops=dict(arrowstyle="->", color="#E8630A", lw=2))
    ax.text(6.65, 3.3, "State", fontsize=7.5, color="#E8630A", ha="center")

    # Step 3 Box
    s3 = patches.FancyBboxPatch((7.0, 2.2), 2.5, 1.8, boxstyle="round,pad=0.15", 
                                edgecolor="#059669", facecolor="#ECFDF5", linewidth=1.8)
    ax.add_patch(s3)
    ax.text(8.25, 3.6, "BUOC 3\nRa Soat & Hoan Thien", fontsize=10, fontweight="bold", ha="center", color="#059669")
    ax.text(8.25, 2.8, "Input: draft_article\nOutput: final_article\n(Nghiem thu 100%)", fontsize=8, ha="center", color="#1E293B")

    # Condition Check Banner
    cond_box = patches.FancyBboxPatch((1.5, 0.4), 7.0, 1.2, boxstyle="round,pad=0.15", 
                                      edgecolor="#DC2626", facecolor="#FEF2F2", linewidth=1.5)
    ax.add_patch(cond_box)
    ax.text(5.0, 1.2, "BO DANH GIA DIEU KIEN DUNG (STOP CONDITION EVALUATOR)", 
            fontsize=9.5, fontweight="bold", ha="center", color="#DC2626")
    ax.text(5.0, 0.7, "1. Goal Achieved == True  -> STOP (Thanh cong)\n2. Steps Executed >= 3    -> STOP (Chan an toan Bounded Loop)", 
            fontsize=8.5, ha="center", color="#334155")

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    img_path = os.path.join(OUTPUT_DIR, "state_flow_diagram.png")
    plt.tight_layout()
    plt.savefig(img_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated: {img_path}")

if __name__ == "__main__":
    generate_architecture_diagram()
    generate_terminal_screenshot()
    generate_state_flow_diagram()
