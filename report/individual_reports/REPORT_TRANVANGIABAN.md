Individual Report: Lab 3 - Chatbot vs ReAct Agent
Student Name: Trần Văn Gia Bân

Student ID: 2A202600319

Date: 06/04/2026

I. Technical Contribution (15 Points)
Mô tả đóng góp cụ thể vào mã nguồn dựa trên file chatbot.py và phần mở rộng Agent.

Modules Implemented: chatbot.py (Baseline) và src/tools/shop_search.py (Dành cho Agent).

Code Highlights:
Trong file chatbot.py, tôi đã triển khai cấu hình kết nối trực tiếp với Gemini API để tạo ra một thực thể Chatbot cơ bản phục vụ việc đối chứng:

```
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction="You are a helpful e-commerce assistant..."
)
```
Ngoài ra, để nâng cấp lên Agent, tôi đã triển khai công cụ thực tế hỗ trợ tìm kiếm địa điểm (dựa trên Geoapify API) giúp Agent có khả năng tính toán phí ship dựa trên vị trí chính xác:

```
# Logic lấy tọa độ từ user_location và tìm shop gần nhất
api_location_url = f"https://api.geoapify.com/v1/geocode/search?text={user_location}&apiKey={shop_api}"
```
II. Debugging Case Study (10 Points)
Problem Description: Với test_query = "buy 2 iPhones using code 'WINNER' and ship to Hanoi", Chatbot Baseline trong file chatbot.py gặp hiện tượng Hallucination (Ảo giác).

Log Source: Output từ print(result) trong file chatbot.py.

Diagnosis: Chatbot không có quyền truy cập vào Database sản phẩm hay API tính phí ship. Do đó, nó tự "bịa" ra một mức giá hoặc trả lời chung chung rằng nó không biết giá cụ thể, thay vì thực hiện tính toán.

Solution: Chuyển đổi sang mô hình ReAct Agent. Bằng cách cung cấp công cụ search_shop và calculate_price, Agent sẽ biết dừng lại (Thought) để gọi công cụ (Action) thay vì trả lời ngay lập tức như Chatbot Baseline.

III. Personal Insights: Chatbot vs ReAct (10 Points)
Reasoning: Trong file chatbot.py, quy trình chỉ là Input -> Output. Trong khi đó, ở ReAct Agent, quy trình là Input -> Thought -> Action -> Observation -> Output. Khối Thought giúp lập trình viên kiểm soát được bước đi của AI, đảm bảo nó kiểm tra mã giảm giá trước khi tính tiền.

Reliability: Chatbot Baseline thường "tự tin thái quá" và trả lời sai về dữ liệu thực tế (như giá iPhone hiện tại). Agent có độ tin cậy cao hơn vì dữ liệu đầu ra được căn cứ (grounded) trên kết quả trả về từ API thực tế (Observation).

Observation: Trong quá trình test, tôi nhận thấy nếu API trả về lỗi 401 (API Key hết hạn), Chatbot Baseline sẽ hoàn toàn bất lực. Nhưng với Agent, nếu ta cấu hình tốt, nó có thể báo lại: "Hiện tại tôi không thể truy cập dữ liệu giá, vui lòng thử lại sau".

IV. Future Improvements (5 Points)
Scalability: Hiện tại API Key đang được lưu trong .env. Trong môi trường Production (như tại VinUni), tôi sẽ chuyển sang sử dụng Azure Key Vault để bảo mật thông tin tốt hơn.

Safety: Bổ sung cơ chế Rate Limiting trong file Python để ngăn chặn việc người dùng spam liên tục khiến tài khoản Gemini API bị khóa hoặc tốn quá nhiều chi phí.

Performance: Nâng cấp simple_chatbot bằng cách thêm Conversation Buffer Memory, giúp chatbot nhớ được các câu thoại trước đó thay vì chỉ xử lý từng câu đơn lẻ (Stateless) như hiện tại.