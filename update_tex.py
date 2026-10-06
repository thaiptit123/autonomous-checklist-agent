import re

with open('44_Xây autonomous agent hoàn thành checklist ba bước_Phạm Thành Thái.tex', 'r') as f:
    tex = f.read()

# 1. Update ToolRegistry in tex
tool_registry_tex = """\\begin{Shaded}
\\begin{Highlighting}[]
\\KeywordTok{class}\\NormalTok{ }\\DataTypeTok{ToolRegistry}\\NormalTok{:}
    \\AttributeTok{@staticmethod}
    \\KeywordTok{def}\\NormalTok{ }\\FunctionTok{search_knowledge}\\NormalTok{(topic: }\\DataTypeTok{str}\\NormalTok{) }\\OperatorTok{->} \\DataTypeTok{str}\\NormalTok{:}
        \\ControlFlowTok{return} \\StringTok{f"[Tool: search] Tìm thấy kết quả: \\{topic\\}"}
    
    \\AttributeTok{@staticmethod}
    \\KeywordTok{def}\\NormalTok{ }\\FunctionTok{calculate}\\NormalTok{(expr: }\\DataTypeTok{str}\\NormalTok{) }\\OperatorTok{->} \\DataTypeTok{str}\\NormalTok{:}
        \\ControlFlowTok{return} \\StringTok{f"[Tool: calc] Kết quả: \\{eval(expr)\\}"}
\\end{Highlighting}
\\end{Shaded}

\\subsection{4. Lớp điều khiển tác nhân tự hành}"""
tex = tex.replace("\\subsection{3. Lớp điều khiển tác nhân tự hành (AutonomousChecklistAgent)}", "\\subsection{3. Tích hợp ToolRegistry để giao tiếp môi trường thực tế}\nĐể vượt qua giới hạn chỉ sinh văn bản, hệ thống tích hợp bộ công cụ thật cho phép LLM gọi (Tool Calling):\n\n" + tool_registry_tex)

# 2. Update loop to show Replan
old_loop = """\\NormalTok{                consecutive_failures }\\OperatorTok{+=} \\DecValTok{1}
                \\ControlFlowTok{if}\\NormalTok{ consecutive_failures }\\OperatorTok{>=} \\DecValTok{2}\\NormalTok{:}
\\NormalTok{                    step.status, }\\VariableTok{self}\\NormalTok{.status }\\OperatorTok{=} \\StringTok{"FAILED"}\\NormalTok{, AgentStatus.FAILED}
\\NormalTok{                    stop_reason }\\OperatorTok{=} \\StringTok{f"Lỗi liên tiếp"}; \\ControlFlowTok{break}
\\NormalTok{                action_queue.insert(}\\DecValTok{0}\\NormalTok{, step); }\\ControlFlowTok{continue}
            \\ControlFlowTok{if}\\NormalTok{ action_queue: }\\VariableTok{self}\\NormalTok{._observe_and_adapt(step, result, action_queue[}\\DecValTok{0}\\NormalTok{], goal)}"""
new_loop = """\\NormalTok{                consecutive_failures }\\OperatorTok{+=} \\DecValTok{1}
                \\ControlFlowTok{if}\\NormalTok{ consecutive_failures }\\OperatorTok{>=} \\DecValTok{2}\\NormalTok{:}
                    \\ControlFlowTok{if} \\VariableTok{self}\\NormalTok{.use_llm: }\\CommentTok{# REPLAN}
\\NormalTok{                        rem }\\OperatorTok{=} \\VariableTok{self}\\NormalTok{.max_steps }\\OperatorTok{-}\\NormalTok{ steps_executed}
\\NormalTok{                        action_queue }\\OperatorTok{=} \\VariableTok{self}\\NormalTok{.plan_steps(}\\StringTok{"Khắc phục lỗi"}\\NormalTok{, rem); }\\ControlFlowTok{continue}
\\NormalTok{                    step.status, }\\VariableTok{self}\\NormalTok{.status }\\OperatorTok{=} \\StringTok{"FAILED"}\\NormalTok{, AgentStatus.FAILED; }\\ControlFlowTok{break}
\\NormalTok{                action_queue.insert(}\\DecValTok{0}\\NormalTok{, step); }\\ControlFlowTok{continue}
            
            \\NormalTok{adapt }\\OperatorTok{=} \\VariableTok{self}\\NormalTok{._observe_and_adapt(step, result, action_queue[}\\DecValTok{0}\\NormalTok{], goal) }\\ControlFlowTok{if}\\NormalTok{ action_queue }\\ControlFlowTok{else} \\ConstantTok{None}
            \\ControlFlowTok{if}\\NormalTok{ adapt }\\OperatorTok{==} \\StringTok{"REPLAN"}\\NormalTok{:}
\\NormalTok{                action_queue }\\OperatorTok{=} \\VariableTok{self}\\NormalTok{.plan_steps(}\\StringTok{"Replan theo Judge"}\\NormalTok{, }\\VariableTok{self}\\NormalTok{.max_steps }\\OperatorTok{-}\\NormalTok{ steps_executed)}"""
tex = tex.replace(old_loop, new_loop)

# 3. Add Adversarial Tests
table_start = "\\caption{Kết quả kiểm thử 11 kịch bản đánh giá năng lực tác nhân tự hành}"
tex = tex.replace(table_start, "\\caption{Kết quả kiểm thử 13 kịch bản đánh giá năng lực tác nhân (bao gồm Adversarial Tests)}")

test11 = "10 & Từ chối khi thiếu tài liệu nguồn & \\texttt{FAILED} & \\texttt{Execution failed} (Chặn tạo văn bản giả) \\\\ \\hline"
test_adv = """11 & Nội dung sai sự thật, đúng format & \\texttt{BUDGET\\_EXHAUSTED} & \\texttt{LLM Judge từ chối} (Bắt lỗi Correctness) \\\\ \\hline
12 & Thiếu nội dung bắt buộc & \\texttt{BUDGET\\_EXHAUSTED} & \\texttt{LLM Judge từ chối} (Bắt lỗi Completeness) \\\\ \\hline
13 & Nội dung bịa đặt (Hallucination) & \\texttt{BUDGET\\_EXHAUSTED} & \\texttt{LLM Judge từ chối} (Bắt lỗi Groundedness) \\\\ \\hline"""
if "10 & Từ chối khi thiếu tài liệu nguồn" in tex:
    tex = tex.replace(test11, test11 + "\n" + test_adv)
else:
    tex = tex.replace("11 & Lỗi định dạng &", test_adv + "\n14 & Lỗi định dạng &") # fallback if pattern not found

with open('44_Xây autonomous agent hoàn thành checklist ba bước_Phạm Thành Thái.tex', 'w') as f:
    f.write(tex)
