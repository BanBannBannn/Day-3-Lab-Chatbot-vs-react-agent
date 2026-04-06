import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Lỗi: Không tìm thấy GEMINI_API_KEY trong file .env hoặc biến môi trường!")
else:
    genai.configure(api_key=api_key)

def simple_chatbot(user_query):
    """
    Chatbot Baseline: Dùng để so sánh hiệu năng với Agent ở Phase 3.
    """
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-lastest",
        system_instruction="You are a helpful e-commerce assistant. Answer the user's questions to the best of your knowledge."
    )

    print(f"\n--- [Chatbot Baseline] Đang xử lý: {user_query} ---")
    
    try:
        response = model.generate_content(user_query)
        return response.text
    except Exception as e:
        return f"Lỗi kết nối API: {e}"

if __name__ == "__main__":
    # Test case gây khó cho Chatbot truyền thống (theo Instructor Guide)
    test_query = "I want to buy 2 iPhones using code 'WINNER' and ship to Hanoi. What is the total price?"
    
    result = simple_chatbot(test_query)
    
    print("\n--- PHẢN HỒI ---")
    print(result)