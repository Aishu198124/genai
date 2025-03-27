import os
import time
import json
import csv
import requests
import pandas as pd
import google.generativeai as genai
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Google Gemini API Key
GEMINI_API_KEY = "AIzaSyDa3giOkK9xlwIiP7h0lsuT80ekPiuX7rc"
genai.configure(api_key=GEMINI_API_KEY)

# Function to scrape website content (Handles dynamic and static content)
def scrape_website(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            time.sleep(5)  # Allow time for JavaScript to load
            content = page.content()
            browser.close()
        
        soup = BeautifulSoup(content, "html.parser")

        # Remove scripts, styles, and irrelevant elements
        for script in soup(["script", "style", "header", "footer", "nav"]):
            script.decompose()

        return soup.get_text(separator=" ", strip=True)
    
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

# Function to extract structured information using Gemini LLM
def extract_information(text):
    prompt = f"""
    Extract the following details from the provided website content:

    1. Company's mission statement or core values
    2. Products or services offered
    3. Founding year and founders
    4. Headquarters location
    5. Key executives or leadership team
    6. Any notable awards or recognitions

    Given content: {text}
    
    Provide the response in JSON format with keys: mission, products, founded, headquarters, executives, awards.
    """

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    
    try:
        data = json.loads(response.text)  # Convert response to JSON
    except json.JSONDecodeError:
        data = {
            "mission": "Not found",
            "products": "Not found",
            "founded": "Not found",
            "headquarters": "Not found",
            "executives": "Not found",
            "awards": "Not found"
        }
    
    return data

# Function to process URLs and save results to CSV
def process_websites(urls, output_file="company_details.csv"):
    data_list = []

    for url in urls:
        print(f"Processing: {url}")
        text = scrape_website(url)

        if text:
            extracted_data = extract_information(text)
            extracted_data["URL"] = url
            data_list.append(extracted_data)

    # Save results to CSV
    df = pd.DataFrame(data_list)
    df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")

# List of websites to scrape
websites = [
    "https://www.microsoft.com",
    "https://www.apple.com",
    "https://www.tesla.com"
]

# Run the script
process_websites(websites)
