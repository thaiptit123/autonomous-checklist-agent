# Bài 44: Autonomous Systems - Xây dựng Autonomous Agent hoàn thành checklist ba bước

Tài liệu hướng dẫn và mã nguồn thực hành thuộc series chuyên sâu của **AI Guru x TiniX**.

## 1. Nội dung trọng tâm
- **Mục tiêu:** Xây dựng Autonomous Checklist Agent cho phép người dùng nhập mục tiêu nhỏ (ví dụ: *Viết bài chia sẻ giải thích RAG cho người mới bắt đầu*).
- **Cơ chế cốt lõi:**
  - Tự động phân tích mục tiêu và lập checklist tối đa 3 bước (Dynamic Planning qua LLM `tinix-lm:latest` / Ollama GPU cục bộ kết hợp Fallback an toàn).
  - Tích hợp **ToolRegistry** mô phỏng giao tiếp với công cụ (search, calculate, read_document), được thiết kế làm điểm mở rộng cho Tool Calling thực tế.
  - Vòng lặp quan sát và đánh giá mạnh mẽ (**Observe, Adapt & REPLAN**): LLM tự động phán đoán chất lượng bước trước, nếu có lỗi hệ thống sẽ tự động tạo `retry_step` hoặc tự động xóa hàng đợi cũ và gọi lại bộ lên kế hoạch (`plan_steps`) để khắc phục lỗi.
  - Thực thi tuần tự (Sequential Execution) và truyền trạng thái qua State Memory.
  - Kiểm soát giới hạn vòng lặp hữu hạn (Bounded Loop $\le$ 3 bước).
  - Đánh giá chất lượng bằng **LLM-as-a-judge** nghiêm ngặt với Rubric: Tính chính xác (Correctness), Tính bám sát (Groundedness), và Tính toàn vẹn (Completeness).
  - Phân định rõ ràng 3 trạng thái dừng (**Stop Condition**): `COMPLETED` (chỉ khi `QualityEvaluator.passed == True`), `BUDGET_EXHAUSTED` (hết số bước cho phép mà chưa đạt chuẩn), và `FAILED` (bước thực thi gặp ngoại lệ).
  - Xuất báo cáo kiểm toán đầy đủ: Ghi nhận metadata cần thiết (**model_version, git_commit, python_version, seed, temperature**) để truy vết và hỗ trợ tái lập thực nghiệm.

## 2. Cấu trúc thư mục
```text
Bai44/
├── 44_Xây autonomous agent hoàn thành checklist ba bước_Phạm Thành Thái.tex
├── 44_Xây autonomous agent hoàn thành checklist ba bước_Phạm Thành Thái.pdf
├── README.md
├── code/
│   ├── checklist_agent.py      # Mã nguồn chính của tác nhân tự hành (LLM + Quality Evaluator + Observe & Adapt)
│   ├── eval_agent.py           # Bộ 18 kịch bản kiểm thử toàn diện đánh giá năng lực tự hành
│   ├── generate_assets.py      # Script tự động tạo sơ đồ kiến trúc và nhật ký terminal thực tế
│   └── agent_final_report.json # Dữ liệu báo cáo mẫu xuất từ phiên chạy LLM benchmark thực tế (19.8s / 19.812s)
└── images/
    ├── architecture_diagram.png # Sơ đồ kiến trúc tổng thể tác nhân
    ├── state_flow_diagram.png   # Sơ đồ truyền trạng thái và kiểm tra điều kiện dừng
    └── terminal_execution.png   # Nhật ký thực thi trực quan trên Terminal với LLM thật
```

> **Ghi chú về tính nhất quán thời gian thực thi:** Báo cáo kiểm toán mẫu `agent_final_report.json`, hình ảnh minh họa terminal và tài liệu PDF ghi nhận thời gian thực thi là **19.8s** (chính xác: **19.812s**) từ phiên chạy benchmark chuẩn với mô hình `tinix-lm:latest` (1.872 ký tự, 391 từ, TTR 0.427). Toàn bộ dữ liệu báo cáo kiểm toán, nhật ký terminal và tài liệu PDF hiện đã được đồng bộ chuẩn xác 100% theo phiên chạy 19.8s này (thay thế cho số liệu ước lượng ~35.6s ở các phiên chạy thử nghiệm ban đầu trên cấu hình cũ).

## 3. Hướng dẫn thiết lập môi trường và mô hình (Setup & Model Access)

Để đảm bảo khả năng tái lập kết quả (reproducibility), hệ thống hỗ trợ 2 phương án thiết lập mô hình độc lập:

### Trường hợp 1: Sử dụng mô hình nội bộ `tinix-lm:latest` (Dành cho thành viên nội bộ / tác giả)
- `tinix-lm:latest` là mô hình tinh chỉnh nội bộ chuyên biệt, **không phát hành công khai** trên Ollama Library (vì vậy **không thể tải bằng lệnh `ollama pull`**).
- Để sử dụng mô hình này, người dùng cần có quyền truy cập tệp `Modelfile` và checkpoint trọng số (liên hệ trực tiếp qua email: `admin@tinix.io` hoặc `thaiptit123@gmail.com` để nhận quyền).
- Sau khi có `Modelfile`, khởi tạo mô hình vào Ollama bằng lệnh:
  ```bash
  ollama create tinix-lm:latest -f Modelfile
  ```

### Trường hợp 2: Sử dụng mô hình nguồn mở thay thế khi không có quyền truy cập `tinix-lm:latest` (Dành cho người thẩm định / cộng đồng kiểm thử)
- Người thẩm định hoặc người dùng thông thường không có `Modelfile` nội bộ có thể chạy và tái lập toàn bộ quy trình của Agent bằng mô hình thay thế tiêu chuẩn:
  ```bash
  ollama pull qwen2.5:3b
  ```
- Hệ thống tác nhân tự động nhận diện và tương thích hoàn toàn với `qwen2.5:3b` (cũng như bất kỳ mô hình nào có sẵn trong Ollama qua cơ chế tự động khám phá mô hình tại cổng `11436` / `11434`).
- Nếu môi trường không khởi chạy Ollama, hệ thống tự động kích hoạt chế độ **Deterministic Fallback** để kiểm thử logic cục bộ mà không gặp sự cố gián đoạn.

## 4. Chạy tác nhân và bộ kiểm thử (Execution & Evaluation)

### Chạy tác nhân tự hành:
```bash
python3 code/checklist_agent.py
```

### Chạy bộ 18 kịch bản kiểm thử toàn diện:
Bộ kiểm thử `code/eval_agent.py` bao gồm tổng cộng **18 kịch bản kiểm thử**, được phân định minh bạch thành 2 nhóm độc lập:
1. **13 Offline Unit Tests (Plumbing & Core Logic)**:
   - Kiểm thử toàn diện cơ chế điều phối tuần tự, rào chắn Bounded Loop, khả năng tự phục hồi (Retry/Replan), và các bài test đường ống kiểm duyệt (Judge Plumbing Tests).
   - Chạy hoàn toàn offline trong môi trường Deterministic Fallback, **kết quả luôn đạt 13/13 PASS** mà không phụ thuộc vào Ollama hay mạng ngoài.
2. **5 Real LLM Integration Tests (Adversarial Semantic Evaluation)**:
   - Kiểm thử tương tác ngữ nghĩa thực tế với LLM Judge cục bộ để thẩm định năng lực phát hiện nội dung sai sự thật, thiếu yêu cầu, hoặc bịa đặt (hallucination).
   - Được gắn cờ an toàn `@unittest.skipUnless(is_ollama_available(), ...)`:
     - Khi có Ollama chạy cục bộ: Thực thi đầy đủ và **đạt 5/5 PASS**.
     - Khi không có Ollama: Tự động **SKIPPED (5 tests)** một cách minh bạch, hoàn toàn không suy diễn hoặc báo cáo sai lệch kết quả.

```bash
python3 code/eval_agent.py
```

### Tạo lại hình ảnh sơ đồ kiến trúc:
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
