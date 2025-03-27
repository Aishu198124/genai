# import requests
# from bs4 import BeautifulSoup

# # URL of the webpage
# # base = "https://about.nike.com/en/company"
# # base = "https://thewaltdisneycompany.com/about/"
# # base = "https://global.toyota/en/company/"
# base = "https://www.pfizer.com/about"

# # Fetch the webpage
# response = requests.get(base)

# # Parse the HTML content
# soup = BeautifulSoup(response.text, "html.parser")

# # Extract all text while ignoring links and images
# for script in soup(["script", "style", "img", "a"]):  # Remove unwanted tags
#     script.extract()

# # Get the cleaned text
# clean_text = soup.get_text(separator=" ", strip=True)

# # Print the cleaned text
# # print(clean_text)

# from google import genai

# client = genai.Client(api_key="AIzaSyDa3giOkK9xlwIiP7h0lsuT80ekPiuX7rc")

# response = client.models.generate_content(
#     model="gemini-2.0-flash", contents= ( "find the mission, "
#     "products/services offered, company founded year, "
#     "founders, headquarters location, key executives, "
#     "awards and recognitions of the company from this text and what company this paragraph is talking about. "
#     "If the information is not explicitely stated in the text, use your knowledge and give the facts you already know  and refer the internet. "
#     "If you couldn't find the details, use the keywords in the text given and then give answers: " + clean_text )
# )
# print(response.text)

import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
from google import genai

# Base URL of the company page
base_url = "https://global.toyota/en/company/"

# Function to fetch and clean text from a given URL
def fetch_clean_text(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove unwanted tags (scripts, styles, images, links)
        for script in soup(["script", "style", "img", "a"]):
            script.extract()

        # Get the cleaned text
        return soup.get_text(separator=" ", strip=True)
    except requests.RequestException:
        return ""

# Fetch and clean text from the base page
clean_text = fetch_clean_text(base_url)

# Find relevant internal links for additional information
soup = BeautifulSoup(requests.get(base_url).text, "html.parser")
relevant_keywords = ["about", "mission", "leadership", "history", "executives", "overview", "profile", "awards"]
found_links = []

for link in soup.find_all("a", href=True):
    href = link["href"]
    full_url = urljoin(base_url, href)  # Convert relative URLs to absolute
    if any(keyword in href.lower() for keyword in relevant_keywords):
        found_links.append(full_url)

# Fetch and append text from relevant links
for link in found_links[:3]:  # Limit to avoid too many requests
    time.sleep(1)  # Respectful scraping delay
    clean_text += "\n" + fetch_clean_text(link)

# Initialize Gemini AI client
client = genai.Client(api_key="AIzaSyDa3giOkK9xlwIiP7h0lsuT80ekPiuX7rc")

# Prepare and send the request to Gemini AI
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=(
        "Find the name, mission, products/services offered, company founded year, "
        "founders, headquarters location, key executives, awards, and recognitions of the company. "
        "If the information is not explicitly stated in the text, analyze related links and infer details. "
        "If details are not found, use the keywords in the text given to provide answers. "
        "Give Objective answer rather than a subjective one. "
        "Extracted Text: " + clean_text
    )
)

# Print the AI's response
print(response.text)
