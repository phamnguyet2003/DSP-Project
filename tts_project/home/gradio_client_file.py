from gradio_client import Client
import os
GRADIO_API_URL = "https://dd8b1e9afd1a6c8469.gradio.live/"
# GRADIO_API_URL = os.environ.get('model_server')
print(f"🔄 Đang khởi tạo Gradio Client: {GRADIO_API_URL}")
client = Client(GRADIO_API_URL)  # Chỉ tạo một lần duy nhất
