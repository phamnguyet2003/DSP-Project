from gradio_client import Client, handle_file

client_path = "None" # link colab
client = Client(client_path)
speaker = client.predict(
		prompt="Xin chào, tôi là một mô hình chuyển đổi văn bản thành giọng nói tiếng Việt.",
		language="vi",
		audio_file_pth="/content/model/samples/nu-luu-loat.wav", # tạo list
		normalize_text=True,
		target_language=None,   # đoạn này trong html thì tạo check list các support language cho user
  		username_gr= "user123",
		api_name="/predict",
  
)
print(speaker)

process_voice_clone = client.predict(
		audio_path=handle_file('https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav'),
		name="Hello!!",
		api_name="/process_voice_clone"
)
print(process_voice_clone)

test_cloned_voice = client.predict(
		text="Xin chào, đây là giọng nói được nhân bản của tôi.",
		status="Hello!!",
		api_name="/test_cloned_voice"
)
print(test_cloned_voice)


