# Bài 44: Autonomous Systems - Xây dựng Autonomous Agent hoàn thành checklist ba bước

Tài liệu hướng dẫn và mã nguồn thực hành thuộc series chuyên sâu của **AI Guru x TiniX**.

## 1. Nội dung trọng tâm
- **Mục tiêu:** Xây dựng Autonomous Checklist Agent cho phép người dùng nhập mục tiêu nhỏ (ví dụ: *Viết bài chia sẻ giải thích RAG cho người mới bắt đầu*).
- **Cơ chế cốt lõi:**
  - Tự động phân tích mục tiêu và lập checklist tối đa 3 bước (Dynamic Planning qua LLM `tinix-lm:latest` / Ollama GPU cục bộ kết hợp Fallback an toàn).
  - Tích hợp **Tool Registry** cho phép Agent chọn action thực tế (search, calculate, read_document) qua chuẩn gọi Tool Calling.
  - Vòng lặp quan sát và đánh giá mạnh mẽ (**Observe, Adapt & REPLAN**): LLM tự động phán đoán chất lượng bước trước, nếu có lỗi hệ thống sẽ tự động tạo `retry_step` hoặc tự động xóa hàng đợi cũ và gọi lại bộ lên kế hoạch (`plan_steps`) để khắc phục lỗi.
  - Thực thi tuần tự (Sequential Execution) và truyền trạng thái qua State Memory.
  - Kiểm soát giới hạn vòng lặp hữu hạn (Bounded Loop $\le$ 3 bước).
  - Đánh giá chất lượng bằng **LLM-as-a-judge** nghiêm ngặt với Rubric: Tính chính xác (Correctness), Tính bám sát (Groundedness), và Tính toàn vẹn (Completeness).
  - Phân định rõ ràng 3 trạng thái dừng (**Stop Condition**): `COMPLETED` (chỉ khi `QualityEvaluator.passed == True`), `BUDGET_EXHAUSTED` (hết số bước cho phép mà chưa đạt chuẩn), và `FAILED` (bước thực thi gặp ngoại lệ).
  - Xuất báo cáo kiểm toán đầy đủ: Ghi nhận 100% metadata (**model_version, git_commit, python_version, seed, temperature**) để tái hiện chính xác thực nghiệm.

## 2. Cấu trúc thư mục
```text
Bai44/
├── 44_Xây autonomous agent hoàn thành checklist ba bước_Phạm Thành Thái.tex
├── 44_Xây autonomous agent hoàn thành checklist ba bước_Phạm Thành Thái.pdf
├── README.md
├── code/
│   ├── checklist_agent.py      # Mã nguồn chính của tác nhân tự hành (LLM + Quality Evaluator + Observe & Adapt)
│   ├── eval_agent.py           # Bộ 14 kịch bản kiểm thử toàn diện đánh giá năng lực tự hành
│   ├── generate_assets.py      # Script tự động tạo sơ đồ kiến trúc và nhật ký terminal thực tế
│   └── agent_final_report.json # Dữ liệu báo cáo mẫu xuất từ phiên chạy LLM thực tế (~10.25s)
└── images/
    ├── architecture_diagram.png # Sơ đồ kiến trúc tổng thể tác nhân
    ├── state_flow_diagram.png   # Sơ đồ truyền trạng thái và kiểm tra điều kiện dừng
    └── terminal_execution.png   # Nhật ký thực thi trực quan trên Terminal với LLM thật
```

## 3. Hướng dẫn tái tạo môi trường (Reproduction Steps)
Để đảm bảo khả năng tái tạo kết quả (reproducibility) với Integration Tests, vui lòng thiết lập môi trường Ollama cục bộ:

1. **Cài đặt Ollama**: Tải và cài đặt tại [ollama.com](https://ollama.com). Đảm bảo service chạy ở port mặc định `11434` hoặc `11436` (GPU).
2. **Kéo mô hình (Pull model)**:
   ```bash
   # Nếu bạn có model tinix-lm
   ollama pull tinix-lm:latest
   
   # HOẶC sử dụng fallback model qwen2.5:3b (Nếu tinix-lm:latest không tồn tại, Agent tự chọn model đầu tiên đang có trong Ollama, ví dụ qwen2.5:3b)
   ollama pull qwen2.5:3b
   ```
3. **Cài đặt thư viện Python**: (Không yêu cầu thư viện ngoài, chỉ dùng chuẩn của Python 3.8+).

Chạy tác nhân tự hành:
```bash
python3 code/checklist_agent.py
```

Chạy bộ 14 kịch bản kiểm thử toàn diện (Adversarial Tests):
```bash
python3 code/eval_agent.py
```

Tạo lại hình ảnh sơ đồ:
```bash
python3 code/generate_assets.py
```

## 4. Hướng dẫn biên dịch LaTeX
Sử dụng trình biên dịch `xelatex`:
```bash
xelatex -interaction=nonstopmode "44_Xây autonomous agent hoàn thành checklist ba bước_Phạm Thành Thái.tex"
xelatex -interaction=nonstopmode "44_Xây autonomous agent hoàn thành checklist ba bước_Phạm Thành Thái.tex"
```
*(Chạy 2 lần để cập nhật số trang `LastPage` và Mục Lục chính xác).*
