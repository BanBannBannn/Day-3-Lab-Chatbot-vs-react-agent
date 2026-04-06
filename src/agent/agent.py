import os
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger

class ReActAgent:
    """
    SKELETON: A ReAct-style Agent that follows the Thought-Action-Observation loop.
    Students should implement the core loop logic and tool execution.
    """
    
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
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
You run a Thought, Action, PAUSE, Observation loop.
At the end of the loop, you provide the Answer.

Use Thought to describe your thoughts on the request.
Use Action to call one of the available tools - then return PAUSE.
Observation is the result returned after calling that tool.

Your available tools:

{tool_descriptions}

Important Note:
- ALWAYS call get_menu() first to confirm availability.
- ALWAYS call calculate_total() and inform the customer of the price before ordering.
- DO NOT call place_order() if you do not have the full name, phone number, and address.

Example session:

Question: I would like to order 2 bowls of beef pho, delivered to 123 Le Loi Street.
Thought: Need to check if beef pho is still available and get the order code.
Action: get_menu: mon_chinh
PAUSE

Observation: [{{"id": "PHO_001", "name": "Phở bò", "price": 55000, "available": True}}]

Thought: Items are still available. Calculate the total for 2 bowls before ordering.

Action: calculate_total: PHO_001,2
PAUSE

Observation: {{"subtotal": 110000, "vat": 8800, "total": 118800}}

Thought: Need to provide a price quote and ask for the customer's name and phone number before ordering.

Answer: Pho bò x2 = 118,800 VND (including VAT). Please provide the name and phone number to confirm the order!

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
            # TODO: Parse Thought/Action from result
            action_match = re.search(r"Action:\s*(\w+):\s*(.+)", result)
            answer_match = re.search(r"Answer:\s*(.+)", result, re.DOTALL)
            # TODO: If Action found -> Call tool -> Append Observation
            if action_match:
                tool_name = action_match.group(1).strip()
                tool_input = action_match.group(2).strip()

                logger.log_event("ACTION_CALL", {"tool": tool_name, "input": tool_input})

                # Tìm tool phù hợp trong self.tools
                tool_fn = next(
                    (t["function"] for t in self.tools if t["name"] == tool_name),
                    None
                )

                if tool_fn:
                    observation = tool_fn(tool_input)
                else:
                    observation = f"Lỗi: Không tìm thấy tool '{tool_name}'"

                logger.log_event("OBSERVATION", {"result": observation})

                # Nối Observation vào prompt để vòng sau LLM biết
                current_prompt += f"\n{result}\nObservation: {observation}"
            # TODO: If Final Answer found -> Break loop
            elif answer_match:
                final_answer = answer_match.group(1).strip()
                logger.log_event("AGENT_END", {"steps": steps, "answer": final_answer})
                return final_answer

            else:
                # LLM không trả về Action lẫn Answer → thoát tránh lặp vô ích
                logger.log_event("AGENT_END", {"steps": steps, "reason": "no_action_no_answer"})
                break

            
            steps += 1
            
        logger.log_event("AGENT_END", {"steps": steps})
        return "Not implemented. Fill in the TODOs!"

    def _execute_tool(self, tool_name: str, args: str) -> str:
        """
        Helper method to execute tools by name.
        """
        for tool in self.tools:
            if tool['name'] == tool_name:
                # TODO: Implement dynamic function calling or simple if/else

                return f"Result of {tool_name}"
        return f"Tool {tool_name} not found."
