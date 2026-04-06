from src.core.gemini_provider import GeminiProvider
from src.agent.agent import ReActAgent
from src.tools.menu_search import get_price_of_food
from src.tools.shop_search import search_shop

import os

agent = ReActAgent(
    llm= GeminiProvider(api_key= os.getenv("GEMINI_API_KEY")),
    tools= [{
            "name": "search_shop",
            "description": "Tìm vị trí của một cửa hàng theo địa điểm",
            "function": search_shop
    },{
            "name": "get_price_of_food",
            "description": "tìm giá của món ăn theo địa chỉ cụ thể",
            "function": get_price_of_food
    }])



user_query = "I would like to order pho, delivered to 512 Le Duan Street"
agent.run(user_query)
