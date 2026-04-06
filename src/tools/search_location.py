
from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()
search_engine = TavilyClient(api_key= os.getenv("TAVILY_API_KEY"))


def websearch_food_locations(food_name:str, region:str)->list[str]:
    r"""Tìm địa chỉ của các quán ăn theo khu vực trên internet
    Args:
        food_name: món ăn cần tìm
        region: khu vực quận/huyện/thị trấn cần tìm
    Returns:
        a list of string: chứa địa chỉ các quán ăn từ internet
    """
    results = search_engine.search(
            f"Địa chỉ quán {food_name} tại {region}",
            include_raw_content=False,
            include_answer=False,
            country = "vietnam",
    )

    return [ele['content'] for ele in results['results'] if float(ele['score']) > 0.5]

