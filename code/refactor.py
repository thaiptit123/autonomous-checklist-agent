import re
with open('code/checklist_agent.py', 'r') as f:
    code = f.read()

# Add ToolRegistry
tools_code = """
class ToolRegistry:
    @staticmethod
    def search_knowledge(topic: str) -> str:
        return f"[Tool: search_knowledge] Tìm thấy 5 kết quả chuyên sâu về: {topic}."
    
    @staticmethod
    def read_document(doc_id: str) -> str:
        return f"[Tool: read_document] Đã trích xuất nội dung từ tài liệu {doc_id}."
        
    @staticmethod
    def calculate(expression: str) -> str:
        try:
            return f"[Tool: calculate] Kết quả: {eval(expression)}"
        except:
            return "[Tool: calculate] Lỗi tính toán"
"""
code = re.sub(r'class AutonomousChecklistAgent:', tools_code + '\n\nclass AutonomousChecklistAgent:', code)

# Modify _execute_step_action
execute_code_orig = """    def _execute_step_action(self, step: Step, topic: str, goal: str) -> str:
        \"\"\"
        Mô phỏng thực thi hành động, gọi LLM nếu có, hoặc dùng fallback.
        \"\"\""""
execute_code_new = """    def _execute_step_action(self, step: Step, topic: str, goal: str) -> str:
        if hasattr(ToolRegistry, step.action_type):
            tool_func = getattr(ToolRegistry, step.action_type)
            res = tool_func(step.description)
            self.context_memory[step.action_type] = res
            return res
"""
code = code.replace(execute_code_orig, execute_code_new)

# Implement True Replan in loop
loop_orig = """            except Exception:
                consecutive_failures += 1
                if consecutive_failures >= 2:
                    step.status, self.status = "FAILED", AgentStatus.FAILED
                    stop_reason = f"Lỗi liên tiếp"; break
                action_queue.insert(0, step); continue
            if action_queue: self._observe_and_adapt(step, result, action_queue[0], goal)"""

loop_new = """            except Exception as e:
                consecutive_failures += 1
                if consecutive_failures >= 2:
                    if self.use_llm:
                        print("   🔄 [REPLAN] Lập kế hoạch lại (Replan) do liên tiếp thất bại...")
                        rem = self.max_steps - steps_executed
                        if rem > 0:
                            action_queue = self.plan_steps(f"Khắc phục lỗi: {e}", max_steps=rem)
                            consecutive_failures = 0
                            continue
                    step.status, self.status = "FAILED", AgentStatus.FAILED
                    stop_reason = f"Lỗi liên tiếp"; break
                action_queue.insert(0, step); continue
            
            adapt_signal = None
            if action_queue: adapt_signal = self._observe_and_adapt(step, result, action_queue[0], goal)
            if adapt_signal == "REPLAN":
                print("   🔄 [REPLAN] Lập kế hoạch lại theo đánh giá của LLM Judge...")
                rem = self.max_steps - steps_executed
                if rem > 0:
                    action_queue = self.plan_steps(f"Replan để hoàn thiện: {goal}", max_steps=rem)
"""
code = code.replace(loop_orig, loop_new)

# Allow max_steps in plan_steps
code = code.replace("def plan_steps(self, goal: str) -> List[Step]:", "def plan_steps(self, goal: str, max_steps: int = None) -> List[Step]:")
code = code.replace("self.max_steps = min(max(1, max_steps), 3)", "self.max_steps = min(max(1, max_steps), 3)")
code = code.replace("raw_steps[:self.max_steps]", "raw_steps[:(max_steps or self.max_steps)]")
code = code.replace("steps[:self.max_steps]", "steps[:(max_steps or self.max_steps)]")
code = code.replace("self.plan = steps[:(max_steps or self.max_steps)]", "return steps[:(max_steps or self.max_steps)]")

# Fix _observe_and_adapt to return REPLAN
obs_orig = """            if llm_reflection and len(llm_reflection.strip()) > 8:
                adaptation_note = llm_reflection.strip().replace("\\n", " ")
                next_step.description += f" [Chỉ dẫn thích ứng: {adaptation_note}]"
                return adaptation_note"""
obs_new = """            if llm_reflection and len(llm_reflection.strip()) > 8:
                adaptation_note = llm_reflection.strip().replace("\\n", " ")
                if "replan" in adaptation_note.lower(): return "REPLAN"
                next_step.description += f" [Chỉ dẫn thích ứng: {adaptation_note}]"
                return adaptation_note"""
code = code.replace(obs_orig, obs_new)

with open('code/checklist_agent.py', 'w') as f:
    f.write(code)
