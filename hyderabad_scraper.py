"""
Project 1 — Hyderabad Real Estate Price Intelligence
Step 1: Live Scraping from 99acres using requests + BeautifulSoup

IMPORTANT NOTES BEFORE RUNNING:
- 99acres has strong anti-bot protection (CAPTCHA, rate limiting, IP blocking).
- This code attempts to scrape but may trigger CAPTCHA after a few requests.
- For live demo/portfolio, run with small number of pages (e.g., 2-3) and add proxies or use residential proxies in production.
- Always respect robots.txt and site's terms. This is for educational/portfolio purposes.
- Add User-Agent rotation and delays as shown.
- If blocked, fall back to using a pre-scraped sample CSV or use Selenium with undetected-chromedriver.

Run this script: python hyderabad_scraper.py
It will save 'hyderabad_properties.csv'
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from urllib.parse import urljoin
import random

# Headers to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

def get_soup(url):
    """Fetch page and return BeautifulSoup object. Handles basic errors."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            return BeautifulSoup(response.content, 'html.parser')
        else:
            print(f"Status code {response.status_code} for {url}")
            return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_price(price_text):
    """Convert '₹45 Lac' or '₹1.2 Cr' to numeric value in Rupees."""
    if not price_text or pd.isna(price_text):
        return None
    price_text = price_text.replace('₹', '').replace(',', '').strip().lower()
    
    if 'cr' in price_text:
        num = re.search(r'[\d.]+', price_text)
        if num:
            return float(num.group()) * 10000000  # 1 Cr = 10 million
    elif 'lac' in price_text or 'lakh' in price_text:
        num = re.search(r'[\d.]+', price_text)
        if num:
            return float(num.group()) * 100000  # 1 Lac = 100,000
    else:
        # Try direct number
        num = re.search(r'[\d,]+', price_text)
        if num:
            return float(num.group().replace(',', ''))
    return None

def parse_sqft(sqft_text):
    """Extract numeric sqft from text like '1,200 sqft' or '1200 sq.ft'."""
    if not sqft_text:
        return None
    match = re.search(r'([\d,]+)', sqft_text.replace(',', ''))
    if match:
        return int(match.group(1))
    return None

def extract_amenities(amenity_list):
    """Create binary flags for common amenities."""
    amenities_str = ' '.join(amenity_list).lower() if amenity_list else ''
    return {
        'has_gym': 1 if 'gym' in amenities_str or 'fitness' in amenities_str else 0,
        'has_pool': 1 if 'pool' in amenities_str or 'swimming' in amenities_str else 0,
        'has_parking': 1 if 'parking' in amenities_str else 0,
        'has_clubhouse': 1 if 'club' in amenities_str else 0,
        'has_security': 1 if 'security' in amenities_str else 0,
    }

def scrape_hyderabad_properties(max_pages=5):
    """
    Main scraping function.
    Scrapes multiple pages from 99acres Hyderabad apartments for sale.
    """
    base_url = "https://www.99acres.com"
    # Starting URL for Hyderabad residential apartments (sale)
    start_url = "https://www.99acres.com/residential-apartments-in-hyderabad-ffid"
    
    all_listings = []
    
    current_url = start_url
    page_num = 1
    
    while page_num <= max_pages and current_url:
        print(f"\n=== Scraping Page {page_num} ===")
        print(f"URL: {current_url}")
        
        soup = get_soup(current_url)
        if not soup:
            print("Failed to get page. Stopping.")
            break
        
        # 99acres typically uses divs with class containing 'srpTuple' or similar for listings
        # We look for common patterns (these classes change often - inspect page to update)
        listings = soup.find_all('div', class_=re.compile(r'srpTuple|propertyCard|listingCard', re.I))
        
        if not listings:
            # Fallback: try finding any article or div with price
            listings = soup.find_all('div', attrs={'data-label': re.compile(r'property', re.I)})
        
        print(f"Found {len(listings)} potential listings on page {page_num}")
        
        for listing in listings:
            try:
                # Extract locality / project name
                locality_elem = listing.find(['a', 'span', 'h2'], class_=re.compile(r'locality|projectName|srpTupleProjectName', re.I))
                locality = locality_elem.get_text(strip=True) if locality_elem else None
                
                # Price
                price_elem = listing.find(['span', 'div'], class_=re.compile(r'price|srpTuplePrice', re.I))
                price_text = price_elem.get_text(strip=True) if price_elem else None
                price = parse_price(price_text)
                
                # BHK / Configuration
                bhk_elem = listing.find(['span', 'div'], class_=re.compile(r'bhk|configuration|srpTupleBhk', re.I))
                bhk_text = bhk_elem.get_text(strip=True) if bhk_elem else None
                # Extract BHK number
                bhk_match = re.search(r'(\d+)\s*BHK', bhk_text or '', re.I)
                bhk = int(bhk_match.group(1)) if bhk_match else None
                
                # Area / sqft
                area_elem = listing.find(['span', 'div'], class_=re.compile(r'area|superArea|carpetArea|srpTupleArea', re.I))
                area_text = area_elem.get_text(strip=True) if area_elem else None
                sqft = parse_sqft(area_text)
                
                # Amenities (often in a list or icons)
                amenities = []
                amenity_elems = listing.find_all(['span', 'div', 'li'], class_=re.compile(r'amenity|feature|icon', re.I))
                for elem in amenity_elems:
                    text = elem.get_text(strip=True).lower()
                    if text:
                        amenities.append(text)
                
                # Sometimes amenities are in data attributes or separate section
                amenity_container = listing.find('div', class_=re.compile(r'amenities', re.I))
                if amenity_container:
                    amenities.extend([a.get_text(strip=True) for a in amenity_container.find_all(['span', 'div'])])
                
                amenity_flags = extract_amenities(amenities)
                
                # Property link for more details if needed
                link_elem = listing.find('a', href=True)
                detail_url = urljoin(base_url, link_elem['href']) if link_elem else None
                
                if price and sqft and locality:  # Only keep valid entries
                    listing_data = {
                        'locality': locality,
                        'price': price,
                        'bhk': bhk,
                        'sqft': sqft,
                        'price_per_sqft': round(price / sqft, 2) if sqft else None,
                        'detail_url': detail_url,
                        **amenity_flags
                    }
                    all_listings.append(listing_data)
                    print(f"  ✓ Extracted: {locality} | {bhk}BHK | ₹{price:,.0f} | {sqft} sqft")
                
            except Exception as e:
                print(f"  Error parsing listing: {e}")
                continue
        
        # Find next page link
        next_page = soup.find('a', string=re.compile(r'Next|»|next page', re.I))
        if next_page and 'href' in next_page.attrs:
            current_url = urljoin(base_url, next_page['href'])
        else:
            # Alternative pagination pattern used by 99acres
            pagination = soup.find('a', class_=re.compile(r'pageLink|pagination', re.I))
            if pagination:
                current_url = urljoin(base_url, pagination.get('href', ''))
            else:
                current_url = None
        
        # Polite delay (2 seconds as requested + random jitter)
        delay = 2 + random.uniform(0, 1)
        print(f"Waiting {delay:.1f} seconds before next page...")
        time.sleep(delay)
        
        page_num += 1
    
    # Create DataFrame
    df = pd.DataFrame(all_listings)
    
    if not df.empty:
        # Remove duplicates
        df = df.drop_duplicates(subset=['locality', 'bhk', 'sqft', 'price'], keep='first')
        print(f"\n=== Scraping Complete ===")
        print(f"Total listings scraped: {len(df)}")
        df.to_csv('hyderabad_properties.csv', index=False)
        print("Data saved to hyderabad_properties.csv")
    else:
        print("No data scraped. Possible CAPTCHA or page structure change.")
        # Create empty file with headers for downstream steps
        pd.DataFrame(columns=['locality', 'price', 'bhk', 'sqft', 'price_per_sqft', 
                              'has_gym', 'has_pool', 'has_parking', 'has_clubhouse', 'has_security']).to_csv('hyderabad_properties.csv', index=False)
    
    return df

if __name__ == "__main__":
    # Start with small number of pages for testing (increase later)
    df = scrape_hyderabad_properties(max_pages=3)
    print("\nFirst 5 rows preview:")
    print(df.head() if not df.empty else "No data")