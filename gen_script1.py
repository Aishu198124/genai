import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
from google import genai

# Base URL of the company page
base_url = "https://www.shell.com/who-we-are.html"

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
relevant_keywords = ["about", "values", "mission", "leadership", "history", "executives", "overview", "profile", "awards"]
found_links = []

for link in soup.find_all("a", href=True):
    href = link["href"]
    full_url = urljoin(base_url, href)  # Convert relative URLs to absolute
    if any(keyword in href.lower() for keyword in relevant_keywords):
        found_links.append(full_url)

# List to store visited links
visited_links = []

# Fetch and append text from relevant links
for link in found_links[:3]:  # Limit requests
    time.sleep(1)  # Respectful scraping delay
    page_text = fetch_clean_text(link)

    if page_text.strip():  # Only add non-empty pages
        clean_text += "\n" + page_text
        visited_links.append(link)

# Initialize Gemini AI client
client = genai.Client(api_key="AIzaSyDa3giOkK9xlwIiP7h0lsuT80ekPiuX7rc")

# Prepare and send the request to Gemini AI
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=(
        "Find the name, mission, products/services offered, company founded year, "
        "founders, headquarters location, key executives, awards, and recognitions of the company. "
        "If the information is not explicitly stated in the text, use the keywords in the text given to provide answers. "
        "Give Objective answer rather than a subjective one. "
        "Extracted Text: " + clean_text
    )
)

# Print visited links if additional pages were accessed
if visited_links:
    print("\nAdditional pages visited for more information:")
    for link in visited_links:
        print(link)

# Print the AI's response
print("\nGenerated Response:\n")
print(response.text)

#####
# import requests
# from bs4 import BeautifulSoup
# import time
# import csv
# from google import genai

# # List of 10 company-related URLs to scrape
# urls = [
#     "https://www.apple.com/about/",
#     "https://global.toyota/en/company/",
#     "https://www.jpmorganchase.com/about",
#     "https://www.pfizer.com/about",
#     "https://thewaltdisneycompany.com/about/",
#     "https://about.nike.com/en/company",
    
    
    
# ]

# # Function to fetch and clean text from a given URL
# def fetch_clean_text(url):
#     try:
#         response = requests.get(url, timeout=10)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.text, "html.parser")

#         # Remove unwanted tags (scripts, styles, images, links)
#         for script in soup(["script", "style", "img", "a"]):
#             script.extract()

#         # Get the cleaned text
#         return soup.get_text(separator=" ", strip=True)
#     except requests.RequestException:
#         return ""

# # Initialize Gemini AI client
# client = genai.Client(api_key="YOUR_GEMINI_API_KEY")  # Replace with your actual API key

# # CSV file setup
# csv_filename = "company_details.csv"
# fieldnames = ["Company Name", "Mission", "Products/Services", "Founded Year", "Founders",
#               "Headquarters", "Key Executives", "Awards", "Recognitions", "Source URL"]

# with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
#     writer = csv.DictWriter(file, fieldnames=fieldnames)
#     writer.writeheader()

#     for url in urls:
#         print(f"Scraping: {url}")  # Display which URL is being processed
#         time.sleep(1)  # Respectful delay

#         # Fetch text content
#         clean_text = fetch_clean_text(url)

#         # Request AI processing
#         response = client.models.generate_content(
#             model="gemini-2.0-flash",
#             contents=(
#                 "Find the name, mission, products/services offered, company founded year, "
#                 "founders, headquarters location, key executives, awards, and recognitions of the company. "
#                 "If the information is not explicitly stated in the text, infer details based on available content. "
#                 "Extracted Text: " + clean_text
#             )
#         )

#         # Extracted company details from AI response
#         ai_response = response.text if response.text else "No data found"

#         # Save results to CSV
#         writer.writerow({
#             "Company Name": ai_response.get("Company Name", "N/A"),
#             "Mission": ai_response.get("Mission", "N/A"),
#             "Products/Services": ai_response.get("Products/Services", "N/A"),
#             "Founded Year": ai_response.get("Founded Year", "N/A"),
#             "Founders": ai_response.get("Founders", "N/A"),
#             "Headquarters": ai_response.get("Headquarters", "N/A"),
#             "Key Executives": ai_response.get("Key Executives", "N/A"),
#             "Awards": ai_response.get("Awards", "N/A"),
#             "Recognitions": ai_response.get("Recognitions", "N/A"),
#             "Source URL": url
#         })

# print(f"\nCompany details saved to {csv_filename}")
