from google import genai

client = genai.Client(api_key="your api key")

response = client.models.generate_content(
    model="gemini-2.0-flash", contents="give me uses of apple")
print(response.text)