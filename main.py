from src.core.openai_provider import OpenAIProvider
from src.agent.agent import ReActAgent
# from src.tools.menu_search import get_price_of_food
# from src.tools.shop_search import search_shop
from src.tools.get_distance import get_distance_between_two_addresses
from src.tools.search_location import websearch_food_locations

import os

agent = ReActAgent(
    llm= OpenAIProvider(api_key= os.getenv("OPENAI_API_KEY")),
    tools= [{
            "name": "websearch_food_locations",
            "description": websearch_food_locations.__doc__,
            "function": websearch_food_locations
    },{
            "name": "get_distance_between_two_addresses",
            "description": get_distance_between_two_addresses.__doc__,
            "function": get_distance_between_two_addresses
    }])



user_query = "Tôi cần tìm quán phở gần khu vực Trâu Quỳ, tôi đang ở tại 39 đường Thành Trung, Trâu Quỳ, Gia Lâm, Hà Nội"
agent.run(user_query)
