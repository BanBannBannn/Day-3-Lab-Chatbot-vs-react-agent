# Group Report: Lab 3 - Production-Grade Agentic System

- **Team Name**: C401-X5
- **Team Members**: 2A202600319, 2A202600334, 2A202600446, 2A202600410, 2A202600301
- **Deployment Date**: 06/04/2026

---

## 1. Executive Summary

*Brief overview of the agent's goal and success rate compared to the baseline chatbot.*

- **Success Rate**: 80% cho 5 case chạy thử
- **Key Outcome**: Agent recommend được ít nhất 1 địa điểm kèm theo khoảng cách và thời gian ước tính di chuyển của ô tô

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation

Our agent is built upon a custom `ReActAgent` class that strictly enforces a `Thought -> Action -> Observation` reasoning cycle, capped at a maximum of 4 steps (`max_steps = 4`) to prevent infinite looping and excessive API costs.

* **Prompting Strategy**: The system prompt explicitly guides the LLM to use a multi-step approach. It uses few-shot prompting with a highly relevant local example (e.g., ordering chicken rice in Gia Lam, Hanoi) to teach the model how to sequence its actions.
* **Action Parsing**: The agent uses regular expressions (`re.search`) to extract the intended tool and its JSON-formatted arguments from the LLM's raw text output (`Action: <tool_name>: <json_args>`). 
* **Dynamic Tool Execution**: Upon extracting the action, the `_execute_tool` method safely parses the arguments using `json.loads()` and dynamically invokes the corresponding Python function. The result is then appended to the conversation history as an `Observation`.
* **Built-in Telemetry**: Crucially, the loop is integrated with a custom `tracker` (`src.telemetry.metrics`). Every LLM invocation records the provider, token usage, and latency (`latency_ms`), ensuring complete observability for performance evaluation.
* **Termination**: The loop breaks and returns a response to the user only when the LLM explicitly generates a `Final_Answer` tag, indicating it has gathered sufficient real-world data from the tools.

### 2.2 Tool Definitions

The agent interacts with the external world using two primary APIs: **Tavily** for real-time web scraping and **Vietmap** for hyper-local geospatial routing in Vietnam.

| Tool Name | Input Format | External API | Use Case |
| :--- | :--- | :--- | :--- |
| `websearch_food_locations` | `json` <br> `{"food_name": "str", "region": "str"}` | Tavily Search API | Performs a targeted web search restricted to Vietnam to find physical addresses and context snippets for specific food items in a given region. |
| `get_distance_between_two_addresses` | `json` <br> `{"addr1": "str", "addr2": "str"}` | Vietmap API (v4 & Route) | First geocodes two natural language addresses into lat/lng coordinates, then calculates the exact driving distance (km) and estimated travel time (minutes) by car. |

### 2.3 LLM Providers Used
- **Primary**: GPT-4o
- **Secondary (Backup)**: Gemini-2.5-flash

---

## 3. Telemetry & Performance Dashboard

*Analyze the industry metrics collected during the final test run (based on the multi-step food location routing trace using GPT-4o).*

- **Average Latency (P50)**: ~1,887 ms per step.
- **Max Latency (P99)**: 2,507 ms (Occurred during Step 1, when the LLM had to process a large block of scraped web data from Tavily to extract addresses).
- **Average Tokens per LLM Call**: 1,755 tokens. (Note: Token usage grew linearly from 984 up to 2,184 tokens by the final step because the `Observation` history is appended to the prompt in each loop).
- **Total Cost of Test Case**: $0.07021 (Calculated cumulatively across 4 API calls: $0.00984 + $0.01832 + $0.02021 + $0.02184).
- **Total Task Duration**: ~10.02 seconds (From `AGENT_START` at 14:29:09.409 to `AGENT_END_WITH_ANSWER` at 14:29:19.432, including LLM inference and external API network calls).
---

## 4. Root Cause Analysis (RCA) - Failure Traces

- Lí do tavily search với argument không trả về được location quán ăn và món ăn
- GPT chưa hiểu ý định của người dùng, chưa xác định được vị trí của user, điền vị trí để tìm kiếm chưa chính xác

---

## 5. Ablation Studies & Experiments

### Experiment 1: Prompt v1 vs Prompt v2
- Input 1: "Tôi cần tìm quán phở gần khu vực Trâu Quỳ, tôi đang ở tại 39 đường Thành Trung, Trâu Quỳ, Gia Lâm, Hà Nội"
-> Output 1: Agent trả về có quán ăn địa điểm và thời gian

- Input 2: "Tôi cần tìm quán phở gần khu vực Trâu Quỳ"
-> Output 2: Agent no action no answer

- Nhận xét: Agent chưa thể handle được những case bị thiếu thông tin
---

## 6. Production Readiness Review

---

> [!NOTE]
> Submit this report by renaming it to `GROUP_REPORT_[TEAM_NAME].md` and placing it in this folder.
