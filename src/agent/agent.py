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
You run a Thought, Action, Observation loop.
At the end of the loop, you provide the Answer.

Use Thought to describe your thoughts on the request.
Use Action to call one of the available tools - then return PAUSE.
Observation is the result returned after calling that tool.
Output Answer to show your recommendation for lunch to user if you have enough data from Observation

Your available tools:

{tool_descriptions}

Example usecase:

Question: I would like to order 2 bowls of pho, delivered to 123 Le Loi Street.
Thought: Need to check if pho is still available and get the order code.
Action: search_shop: {{user_location: 123 Le Loi Street}}

Observation: [
    {{
        "name": "Phở Bò Hồ Lợi",
        "address": "209 An Vương, Phú Thượng, Hà Nội"
    }},{{
        "name": "Phở gà Phương",
        "address": "123 P. Hàng Buồm, Hàng Buồm, Hoàn Kiếm, Hà Nội"
    }},
]

Thought: Found 2 shops which sell pho in the address, i need to find details in the menu

Action: get_price_of_food: {{food_name: "Phở Bò", shop_address:"209 An Vương, Phú Thượng, Hà Nội"}},

Observation: [
{{
    'reference': 'www.someurl.com', 
    'content': 'Ở hà nội muốn ăn phở vừa ngon bổ rẻ thì đến đầu đường tam trinh phở bò tươi roi rói 30k còn phở tái chỉ có 25k 1 bát mỗi tội ngồi hơi đông.'
    }},{{
    'reference': 'www.example.com', 
    'content': 'Phở Bò Gia Truyền 2 Đời Giá Chỉ Từ 35K Rất Chất Lượng Phở Bò Nguyên Ký 1009 Đường Hồng Hà. ... hà nội hay sài gòn ? 15w. Minh Quân. Hà Nội ma gia'
}}
]

Answer: Để có thể ăn phở với vị trí gần với vị trí 123 Le Loi Street, bạn có thể tham khảo một số lựa chọn
như sau:
    - đường tam trinh phở bò tươi roi rói 30k còn phở tái chỉ có 25k 1 bát mỗi tội ngồi hơi đông
    - Phở Bò Gia Truyền 2 Đời, Đường Hồng Hà, Giá Chỉ Từ 35K Chất Lượng

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
            # print(result, type(result))
            action_match = re.search(r"Action:\s*(\w+):\s*(.+)", result['content'])
            answer_match = re.search(r"Answer:\s*(.+)", result['content'], re.DOTALL)
            # TODO: If Action found -> Call tool -> Append Observation
            if action_match:
                tool_name = action_match.group(1).strip()
                tool_input = action_match.group(2).strip()

                logger.log_event("ACTION_CALL", {"tool": tool_name, "input": tool_input})
                tool_input = json.loads(tool_input)

                observation = self._execute_tool(tool_name= tool_name, args= tool_input)
                
                logger.log_event("OBSERVATION", {"result": observation})

                # Nối Observation vào prompt để vòng sau LLM biết
                current_prompt += f"\n{result}\nObservation: {observation}"
            # TODO: If Final Answer found -> Break loop
            elif answer_match:
                final_answer = answer_match.group(1).strip()
                print('final_answer: ',final_answer)
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
                    return tool['function'](**args)
                except Exception as e:
                    return f"Lỗi: Không tìm thấy tool '{tool_name}'"
        
        return f"Tool {tool_name} not found."
