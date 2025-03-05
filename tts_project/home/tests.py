from gradio_client import Client

client = Client("https://561b9e7602b44cd7b6.gradio.live/")
result = client.predict(
		prompt="Xin chào, tôi là một mô hình chuyển đổi văn bản thành giọng nói tiếng Việt.",
		language="vi",
		audio_file_pth="/content/model/samples/nu-luu-loat.wav", # tạo list
		normalize_text=True,
		target_language=None,   # đoạn này trong html thì tạo check list các support language cho user
		api_name="/predict"
)
print(result)