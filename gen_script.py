import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
import csv
from datetime import datetime
from google.generativeai import GenerativeModel
from google import genai

# Configure Gemini
genai_api_key = "your api key"  
client = genai.Client(api_key=genai_api_key)

# Add your website links here (either with or without https://)
WEBSITE_LINKS = [
    "https://www.apple.com/leadership/",
    "https://www.samsung.com/in/about-us/company-info/",
    "https://www.shell.com/who-we-are/our-values.html",
    "https://www.jpmorganchase.com/about/business-principles",
    "https://global.toyota/en/company/profile/overview/",
    "https://www.pfizer.com/about",
    "https://thewaltdisneycompany.com/about/",
    "https://www.nestle.com/about/management",
    "https://www.siemens.com/global/en/company/about.html",
    "https://about.nike.com/en/company"
]


def fetch_clean_text(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove unwanted elements
        for element in soup(["script", "style", "img", "a", "nav", "footer", "header", "iframe", "form"]):
            element.decompose()

        # Get clean text
        text = soup.get_text(separator='\n')
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return '\n'.join(chunk for chunk in chunks if chunk)
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return ""

def find_relevant_links(soup, base_url):
    keywords = ["about", "values", "mission", "leadership", "history", 
               "executive", "overview", "profile", "award", "team", 
               "product", "service", "innovation", "heritage", "company"]
    found_links = set()
    
    for link in soup.find_all("a", href=True):
        href = link['href'].lower()
        if any(keyword in href for keyword in keywords):
            absolute_url = urljoin(base_url, link['href'])
            if absolute_url.startswith(base_url):  # Only keep internal links
                found_links.add(absolute_url)
    return list(found_links)

def extract_company_data(base_url):
    print(f"\nProcessing: {base_url}")
    
    # Extract company name from URL
    domain = base_url.split('//')[-1].split('/')[0]
    company_name = '.'.join(domain.split('.')[-2:]).capitalize()
    
    company_data = {
        "company_name": company_name,
        "base_url": base_url,
        "mission": "",
        "products_services": "",
        "founded_year": "",
        "founders": "",
        "headquarters": "",
        "key_executives": "",
        "awards": "",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source_urls": [base_url]
    }
    
    # Get main page content
    main_text = fetch_clean_text(base_url)
    if not main_text:
        return company_data
    
    # Find and process relevant subpages
    try:
        soup = BeautifulSoup(requests.get(base_url).text, "html.parser")
        relevant_links = find_relevant_links(soup, base_url)
        
        all_text = [main_text]
        for link in relevant_links[:3]:  # Limit to 3 subpages
            time.sleep(1)
            page_text = fetch_clean_text(link)
            if page_text:
                all_text.append(page_text)
                company_data["source_urls"].append(link)
    except Exception as e:
        print(f"Error finding relevant links for {base_url}: {str(e)}")
    
    # Prepare prompt for Gemini
    prompt = f"""
    Analyze this company information and extract the following details in JSON format:
    {{
        "mission": "1-2 sentence mission statement",
        "products_services": "comma separated list of main products/services",
        "founded_year": "year the company was founded",
        "founders": "names of founders separated by commas",
        "headquarters": "city, country of headquarters",
        "key_executives": "top 3 executives in 'Name - Title' format, separated by semicolons",
        "awards": "notable awards, one per line with bullet points"
    }}
    
    If information isn't available, leave the value as an empty string.
    
    Company: {company_name}
    Website: {base_url}
    
    Content:
    {' '.join(all_text)[:20000]}  # Truncate to avoid token limits
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        
        if response.text:
            # Try to parse the response as JSON
            try:
                import json
                # Clean the response to extract just the JSON part
                json_str = response.text.strip()
                if json_str.startswith('```json'):
                    json_str = json_str[7:-3].strip()  # Remove markdown json markers
                
                gemini_data = json.loads(json_str)
                
                # Update company data with Gemini's response
                company_data.update({
                    "mission": gemini_data.get("mission", ""),
                    "products_services": gemini_data.get("products_services", ""),
                    "founded_year": gemini_data.get("founded_year", ""),
                    "founders": gemini_data.get("founders", ""),
                    "headquarters": gemini_data.get("headquarters", ""),
                    "key_executives": gemini_data.get("key_executives", ""),
                    "awards": gemini_data.get("awards", "")
                })
            except json.JSONDecodeError:
                print(f"Could not parse Gemini response as JSON for {base_url}")
                print("Response was:", response.text)
    except Exception as e:
        print(f"Gemini processing error for {base_url}: {str(e)}")
    
    return company_data

def save_to_csv(data, filename="company_data.csv"):
    fieldnames = [
        "company_name", "base_url", "mission", "products_services", 
        "founded_year", "founders", "headquarters", "key_executives", 
        "awards", "last_updated", "source_urls"
    ]
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for company in data:
            company["source_urls"] = "; ".join(company["source_urls"])
            writer.writerow(company)
    
    print(f"\nSuccessfully saved data for {len(data)} companies to {filename}")

def main():
    # Normalize all URLs
    normalized_urls = [url for url in WEBSITE_LINKS]
    
    print(f"Starting extraction for {len(normalized_urls)} websites...")
    
    all_company_data = []
    for url in normalized_urls:
        company_data = extract_company_data(url)
        all_company_data.append(company_data)
        print(f"Extracted data for {company_data['company_name']}")
        time.sleep(3)  # Be polite with delays between sites
    
    save_to_csv(all_company_data)

if __name__ == "__main__":
    main()