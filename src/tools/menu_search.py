from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()
search_engine = TavilyClient(api_key= os.getenv("TAVILY_API_KEY"))

def get_price_of_food(food_name: str, shop_address:str):
    r"""
    Tìm giá tham khảo của món ăn tại khu vực
    Args:
        food_name: Tên món ăn muốn tìm kiếm
        shop_address: Địa chỉ của cửa hàng
    Returns:
        List of a dictionary item of reference url and content
    """
    results = search_engine.search(
        f"Giá chi tiết món {food_name} tại khu vực {shop_address}",
        include_raw_content=False,
        include_answer=True,
        country = "vietnam",
    )

    return [{
        "reference": ele['url'],
        "content": ele['content']
    } 
    for ele in results['results']
    ]
