# Bài 44: Autonomous Systems - Xây dựng Autonomous Agent hoàn thành checklist ba bước

Tài liệu hướng dẫn và mã nguồn thực hành thuộc series chuyên sâu của **AI Guru x TiniX**.

## 1. Nội dung trọng tâm
- **Mục tiêu:** Xây dựng Autonomous Checklist Agent cho phép người dùng nhập mục tiêu nhỏ (ví dụ: *Viết bài chia sẻ giải thích RAG cho người mới bắt đầu*).
- **Cơ chế cốt lõi:**
  - Tự động phân tích mục tiêu và lập checklist tối đa 3 bước (Dynamic Planning qua LLM `tinix-lm:latest` / Ollama GPU cục bộ kết hợp Fallback an toàn).
  - Vòng lặp quan sát và thích ứng bước kế tiếp (**Observe & Adapt**): Sau mỗi bước thực thi, tác nhân quan sát kết quả trung gian để điều chỉnh chỉ dẫn thực thi cho các bước kế tiếp.
  - Thực thi tuần tự (Sequential Execution) và truyền trạng thái qua State Memory.
  - Kiểm soát giới hạn vòng lặp hữu hạn (Bounded Loop $\le$ 3 bước).
  - Đánh giá chất lượng định lượng chặt chẽ (**Automated Quality Evaluator**: TTR đa dạng từ vựng $\ge 0.35$, độ dài ký tự/từ, cấu trúc Markdown, từ khóa trọng tâm).
  - Phân định rõ ràng 3 trạng thái dừng (**Stop Condition**): `COMPLETED` (chỉ khi `QualityEvaluator.passed == True`), `BUDGET_EXHAUSTED` (hết số bước cho phép mà chưa đạt chuẩn), và `FAILED` (bước thực thi gặp ngoại lệ).
  - Xuất báo cáo kiểm toán đầy đủ: Kế hoạch ban đầu, nhật ký từng bước thực tế và báo cáo nghiệm thu cuối cùng (`agent_final_report.json`).

## 2. Cấu trúc thư mục
```text
Bai44/
├── 44_Xây autonomous agent hoàn thành checklist ba bước_Phạm Thành Thái.tex
├── 44_Xây autonomous agent hoàn thành checklist ba bước_Phạm Thành Thái.pdf
├── README.md
├── code/
│   ├── checklist_agent.py      # Mã nguồn chính của tác nhân tự hành (LLM + Quality Evaluator + Observe & Adapt)
│   ├── eval_agent.py           # Bộ 10 kịch bản kiểm thử toàn diện đánh giá năng lực tự hành
│   ├── generate_assets.py      # Script tự động tạo sơ đồ kiến trúc và nhật ký terminal thực tế
│   └── agent_final_report.json # Dữ liệu báo cáo mẫu xuất từ phiên chạy LLM thực tế (~10.25s)
└── images/
    ├── architecture_diagram.png # Sơ đồ kiến trúc tổng thể tác nhân
    ├── state_flow_diagram.png   # Sơ đồ truyền trạng thái và kiểm tra điều kiện dừng
    └── terminal_execution.png   # Nhật ký thực thi trực quan trên Terminal với LLM thật
```

## 3. Hướng dẫn chạy thử nghiệm
Chạy tác nhân tự hành:
```bash
python3 code/checklist_agent.py
```

Chạy bộ 10 kịch bản kiểm thử toàn diện:
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
