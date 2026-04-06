import os
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
import json
from src.telemetry.metrics import tracker

class ReActAgent:
    """
    SKELETON: A ReAct-style Agent that follows the Thought-Action-Observation loop.
    Students should implement the core loop logic and tool execution.
    """
    
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 4):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self) -> str:
        """
        TODO: Implement the system prompt that instructs the agent to follow ReAct.
        Should include:
        1.  Available tools and their descriptions.
        2.  Format instructions: Thought, Action, Observation.
        """
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])
        return f"""
You are an helpfull assitant in food location recommdation base on distance
You run follow a Thought, Action, Observation loop.
At the end of the loop, you provide the Answer.

Use Thought to describe your thoughts on the request.
Use Action to call one of the available tools - then return PAUSE.
`Observation` is the result returned after calling that tool.
Use `Final_Answer` to show your recommendation for food location to user if you have enough data from `Observation`

Your available tools:

{tool_descriptions}

Example:

Question: Tôi cần order cơm gà tại khu vực Gia Lâm, tôi đang ở tại 38 đường Thành Trung, Trâu Quỳ, Gia Lâm, Hà Nội

Thought: Tôi cần tìm các quán cơm gà tại khu vực Gia Lâm, Hà Nội
Action: get_food_locations: {{"food_name": "cơm gà", "region": "Gia Lâm, Hà Nội"}}
Observation: [
    '... quán e ủng hộ nhaaaa Địa chỉ: số nhà 131 cửu việt 2- Trâu Quỳ- Gia Lâm- Hà Nội. Log in · Quán CƠM GÀ XỐI MỠ GIA LÂM xin thông báo!!! Chính', 
    'Địa chỉ: Số 9 ngõ 113 – Trâu Quỳ – Gia Lâm – Hà Nội Hotline: 0347528596 Dolphin Bakery – Gửi trọn yêu thương trong từng chiếc bánh.', 
    '131 Cửu Việt 2, Thị Trấn Trâu Quỳ, Gia Lâm, Hà Nội. Mở cửa. Quán được gắn nhãn Yêu thích là Quán Yêu Thích, gồm những quán đạt chất lượng dịch vụ vượt trội', 
    '131 Cửu Việt 2, Thị Trấn Trâu Quỳ , Huyện Gia Lâm , Hà Nội. Café/Dessert, Quán ăn. 20,000đ - 50,000đ. Thực đơn. Xem tất cả thông tin.', 
    'Địa chỉ: Số 14 Ngách 215/11 Trâu Quỳ, TT. Trâu Quỳ, Huyện Gia Lâm, Hà Nội - Điện thoại: Đang cập nhật.']


Thought: Tìm thấy 5 địa điểm nhưng chỉ có địa điểm tại 131 cửu việt 2- Trâu Quỳ- Gia Lâm- Hà Nội là liên quan đến cơm gà, cần
tìm khoảng cách từ địa chỉ này đến địa chỉ hiện tại của người dùng
Action: get_distance_between_two_addresses: {{"addr1": "131 cửu việt 2- Trâu Quỳ- Gia Lâm- Hà Nội", "addr1":"38 đường Thành Trung, Trâu Quỳ, Gia Lâm, Hà Nội"}},
Observation: {{'distance_km': 0.4126, 'time_mins': 1.5316666666666667}}

Final_Answer: Dựa vào thông tin có được, tôi gợi ý cho bạn đến quán CƠM GÀ XỐI MỠ GIA LÂM tại dịa chỉ 131 cửu việt 2- Trâu Quỳ- Gia Lâm- Hà Nội,
cách vị trị của bạn chỉ có 0.4 km, đi ô tô chỉ tốn 1.5 phút
"""

    def run(self, user_input: str) -> str:
        """
        TODO: Implement the ReAct loop logic.
        1. Generate Thought + Action.
        2. Parse Action and execute Tool.
        3. Append Observation to prompt and repeat until Final Answer.
        """
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})
        
        current_prompt = user_input
        steps = 0

        while steps < self.max_steps:
            # TODO: Generate LLM response
            result = self.llm.generate(current_prompt, system_prompt=self.get_system_prompt())
            logger.log_event("LLM_RESPONSE", {"step": steps, "response": result})

            tracker.track_request(
                model= self.llm.model_name,
                provider = result['provider'],
                usage=result['usage'], 
                latency_ms=result['latency_ms']
            )
            # TODO: Parse Thought/Action from result            
            action_match = re.search(r"Action:\s*(\w+):\s*(.+)", result['content'])
            answer_match = re.search(r"Final_Answer:\s*(.+)", result['content'], re.DOTALL)
            # TODO: If Action found -> Call tool -> Append Observation
            if action_match:
                tool_name = action_match.group(1).strip()
                tool_input = action_match.group(2).strip()

                logger.log_event("ACTION_CALL", {"tool": tool_name, "input": tool_input})
                observation = self._execute_tool(tool_name= tool_name, args= tool_input)
                
                logger.log_event("OBSERVATION", {"result": observation})

                # Nối Observation vào prompt để vòng sau LLM biết
                current_prompt += f"\n{result}\nObservation: {observation}"
            
            # TODO: If Final Answer found -> Break loop
            elif answer_match:
                final_answer = answer_match.group(1).strip()
                logger.log_event("AGENT_END_WITH_ANSWER", {"steps": steps, "answer": final_answer})
                return final_answer

            else:
                # LLM không trả về Action lẫn Answer → thoát tránh lặp vô ích
                logger.log_event("AGENT_END", {"steps": steps, "reason": "no_action_no_answer"})
                break

            
            steps += 1
            
        logger.log_event("AGENT_END", {"steps": steps})
        return "Not implemented. Fill in the TODOs!"

    def _execute_tool(self, tool_name: str, args: Any) -> str:
        """
        Helper method to execute tools by name.
        """
        for tool in self.tools:
            if tool['name'] == tool_name:
                # TODO: Implement dynamic function calling or simple if/else        
                try:
                    args = json.loads(args)
                    return tool['function'](**args)
                except Exception as e:
                    return f"Lỗi: run tool error'{tool_name}', error: {e}"
        
        return f"Tool {tool_name} not found."
