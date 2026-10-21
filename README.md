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
- Phân định rõ ràng các trạng thái dừng (**Stop Condition**):
    - `COMPLETED`: Ở chế độ LLM (`use_llm=True`), chỉ được cấp khi đạt toàn bộ tiêu chí định lượng VÀ thẩm định ngữ nghĩa thành công (`semantic_verified=True` bởi LLM Judge); ở chế độ offline (`use_llm=False`), chỉ nghiệm thu ở mức logic cấu trúc kiểm thử và ghi rõ ràng chưa qua thẩm định ngữ nghĩa.
    - `BUDGET_EXHAUSTED`: Hết số bước cho phép mà chưa đạt chuẩn nghiệm thu (hoặc thiếu xác minh ngữ nghĩa của LLM Judge).
    - `FAILED`: Bước thực thi gặp ngoại lệ hoặc thiếu tài liệu nguồn bắt buộc đối với tác vụ tóm tắt (Test 9).
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
│   ├── agent_final_report.json # Dữ liệu báo cáo mẫu xuất từ phiên chạy LLM benchmark thực tế (19.8s / 19.812s)
│   └── test_execution_ollama.log # Nhật ký chạy thực tế toàn bộ 18/18 tests với Ollama thật (29.811s)
└── images/
    ├── architecture_diagram.png    # Sơ đồ kiến trúc tổng thể tác nhân
    ├── state_flow_diagram.png      # Sơ đồ truyền trạng thái và kiểm tra điều kiện dừng
    ├── terminal_execution.png      # Nhật ký thực thi trực quan trên Terminal với LLM thật
    └── terminal_eval_18_pass.png   # Ảnh chụp terminal chạy 18/18 PASS test suite (29.811s)
```

### Bảng đối chiếu số liệu thời gian và kết quả thực nghiệm (Benchmark Summary)

| Hạng mục thực nghiệm | Thời gian đo được | Mô hình & Môi trường | Ý nghĩa & Nguồn dữ liệu |
|---|---|---|---|
| **Phiên chạy Agent mẫu (RAG Article)** | **19.812s** (làm tròn **19.8s**) | `tinix-lm:latest` (Ollama GPU) | Bài viết RAG hoàn chỉnh (1.872 ký tự, 391 từ, TTR 0.427, 3/3 bước `COMPLETED`, LLM Judge Verified). Lưu tại `code/agent_final_report.json` và minh họa ở PDF Trang 14, 18. |
| **Suite 18 Tests (Khi có Ollama)** | **29.811s** | `tinix-lm:latest` (Ollama GPU) | 13 Offline Unit Tests PASS + 5 Real LLM Integration Tests PASS (18/18 PASS, gồm 4 kịch bản kiểm thử đối kháng). Nhật ký thực nghiệm lưu tại `code/test_execution_ollama.log` và minh họa ở PDF Trang 17. |
| **Suite 18 Tests (Chế độ Offline)** | **0.045s** | Deterministic Fallback (Không có Ollama) | 13 Offline Unit Tests PASS, 5 Integration Tests tự động bỏ qua (`skipped=5`). Minh họa ở PDF Trang 17. |
| *Lưu ý về các lần đo cũ* | *~35.6s / 21.5s* | *Môi trường thử nghiệm ban đầu* | *Các con số ước lượng trên phần cứng cũ trong quá trình phát triển ban đầu đã được thay thế hoàn toàn bằng bộ số liệu benchmark chuẩn 19.812s.* |

> **Phân định ranh giới ý nghĩa của trạng thái `COMPLETED`:**
> - **Trong chế độ LLM (`use_llm=True`):** `COMPLETED` là sự nghiệm thu chất lượng kép (**Dual-Gate Verified**): bắt buộc phải thỏa mãn cả tiêu chuẩn định lượng lẫn xác thực ngữ nghĩa thành công từ LLM Judge (`semantic_verified=True`, `judge_status="VERIFIED_SUCCESS"`). Nếu LLM Judge từ chối (correctness/groundedness/completeness = 0) hoặc gặp lỗi kết nối/JSON, hệ thống kích hoạt Fail-Closed: tuyệt đối không cho phép dừng ở `COMPLETED` mà chuyển sang `BUDGET_EXHAUSTED` khi hết bước.
> - **Trong chế độ Offline Heuristic (`use_llm=False`):** `COMPLETED` chỉ đại diện cho việc thỏa mãn bộ lọc logic định lượng (độ dài, đề mục Markdown, đa dạng từ vựng TTR, từ khóa) phục vụ kiểm thử đơn vị độc lập (Unit Test) không phụ thuộc GPU/Ollama. Hệ thống ghi nhận tường minh trong `stop_reason` và nhật ký kiểm toán: `(Chế độ offline heuristic: Chưa xác minh ngữ nghĩa bởi LLM Judge)` với `semantic_verified=False`. Trạng thái này không đồng nghĩa với việc nội dung đã được LLM thẩm định ngữ nghĩa.

### Đánh giá khách quan về phạm vi tự hành và ranh giới nghiên cứu (Scope of Autonomy & Research Boundary)
Nhằm phản ánh trung thực bản chất kỹ thuật theo đúng phạm vi thực nghiệm:
1. **Lập kế hoạch động (Dynamic Planning):** LLM tự động phân rã mục tiêu thành checklist hành động JSON (ví dụ: `research_points` $\rightarrow$ `outline` $\rightarrow$ `generate`), khác biệt bản chất so với pipeline cố định hardcoded.
2. **Quan sát, thích ứng và lập lại kế hoạch (Observe, Adapt & REPLAN):** Sau mỗi bước, Agent quan sát độ dài, cấu trúc và chèn chỉ dẫn thích ứng vào prompt bước sau; khi gặp trở ngại, kích hoạt REPLAN để sinh kế hoạch mới với ngân sách còn lại.
3. **Giới hạn an toàn kép (Bounded Loop & Fail-Closed Guardrails):** Khóa trần thực thi $\le 3$ bước (`steps_executed`), tự động hạ cấp trạng thái về `BUDGET_EXHAUSTED` nếu kiểm định cuối thất bại.
4. **Ranh giới thực nghiệm (Research Sandbox):** Hệ thống được thiết kế như một mô hình nghiên cứu/thử nghiệm sandbox nhằm kiểm chứng logic điều khiển khép kín và cơ chế an toàn. Các công cụ trong `ToolRegistry` hiện tại là mô phỏng (mock tools), và cơ chế fallback khi LLM ngoại tuyến dựa trên luật xác định. Đây là bước đệm kiến trúc vững chắc trước khi tích hợp API thực tế và phát triển các hệ thống Multi-Agent phức tạp hơn.

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

> **Nhật ký chạy thực tế với LLM thật:** Toàn bộ kết quả đầu ra thực tế của phiên chạy 18 test suite với mô hình Ollama (18/18 PASS trong 29.811s, bao gồm log chi tiết của 4 bài kiểm thử đối kháng Adversarial LLM Tests) được lưu trữ nguyên bản tại [`code/test_execution_ollama.log`](code/test_execution_ollama.log) và ảnh chụp terminal tại [`images/terminal_eval_18_pass.png`](images/terminal_eval_18_pass.png) để phục vụ thẩm định độc lập.

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
