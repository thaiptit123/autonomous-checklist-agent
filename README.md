# Bài 44: Autonomous Systems - Xây dựng Autonomous Agent hoàn thành checklist ba bước

Tài liệu hướng dẫn và mã nguồn thực hành thuộc series chuyên sâu của **AI Guru x TiniX**.

## 1. Nội dung trọng tâm
- **Mục tiêu:** Xây dựng Autonomous Checklist Agent cho phép người dùng nhập mục tiêu nhỏ (ví dụ: *Viết bài chia sẻ giải thích RAG cho người mới bắt đầu*).
- **Cơ chế cốt lõi:**
  - Tự động phân tích mục tiêu và lập checklist tối đa 3 bước (Dynamic Planning qua LLM `tinix-lm:latest` / Ollama cục bộ kết hợp Fallback an toàn).
  - Thực thi tuần tự (Sequential Execution) và truyền trạng thái qua State Memory.
  - Kiểm soát giới hạn vòng lặp hữu hạn (Bounded Loop $\le$ 3 bước).
  - Đánh giá chất lượng định lượng (Automated Quality Evaluator: TTR, độ dài, cấu trúc Markdown, từ khóa trọng tâm).
  - Phân định rõ ràng 3 trạng thái dừng (Stop Condition): `COMPLETED` (Goal achieved), `BUDGET_EXHAUSTED` (Max steps reached mà chưa thỏa mục tiêu), và `FAILED` (Bước thực thi gặp lỗi).
  - Xuất báo cáo đầy đủ: Kế hoạch ban đầu, nhật ký từng bước và báo cáo nghiệm thu cuối cùng (`agent_final_report.json`).

## 2. Cấu trúc thư mục
```text
Bai44/
├── 44_Xây autonomous agent hoàn thành checklist ba bước_Phạm Thành Thái.tex
├── 44_Xây autonomous agent hoàn thành checklist ba bước_Phạm Thành Thái.pdf
├── README.md
├── code/
│   ├── checklist_agent.py      # Mã nguồn chính của tác nhân tự hành (LLM + Quality Evaluator)
│   ├── eval_agent.py           # Bộ 7 kịch bản kiểm thử toàn diện và đánh giá điều kiện dừng
│   ├── generate_assets.py      # Script tự động tạo sơ đồ kiến trúc và luồng dữ liệu
│   └── agent_final_report.json # Dữ liệu báo cáo mẫu xuất từ Agent
└── images/
    ├── architecture_diagram.png # Sơ đồ kiến trúc tổng thể tác nhân
    ├── state_flow_diagram.png   # Sơ đồ truyền trạng thái và kiểm tra điều kiện dừng
    └── terminal_execution.png   # Nhật ký thực thi trực quan trên Terminal
```

## 3. Hướng dẫn chạy thử nghiệm
Chạy tác nhân tự hành:
```bash
python3 code/checklist_agent.py
```

Chạy bộ 7 kịch bản kiểm thử:
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
