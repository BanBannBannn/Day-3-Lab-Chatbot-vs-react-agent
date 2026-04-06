from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()
search_engine = TavilyClient(api_key= os.getenv("TAVILY_API_KEY"))

def get_menu_of_shop(shop_name: str, shop_address:str):
    r"""
    Tìm menu của cửa hàng
    Args:
        shop_name: Tên cửa hàng
        shop_address: Địa chỉ của cửa hàng
    Returns:
        List of a dictionary item of url and content
    """
    results = search_engine.search(
        f"Menu và giá tại {shop_name} tại địa chỉ {shop_address}",
        include_raw_content=False,
        include_answer=False,
        country = "vietnam",
        # include_domains=['https://shopeefood.vn/']
    )

    
    return [{
        "url": ele['url'],
        "content": ele['content']
    } 
    for ele in results['results']
    ]
