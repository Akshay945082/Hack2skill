import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from fake_useragent import UserAgent

def scrape_companies():
    # Base URL for the target site and search category
    base_url = "https://www.yellowpages.com"
    search_url = f"{base_url}/search?search_terms=hotels&geo_location_terms=CA"

    
    # Initialize User-Agent for headers
    ua = UserAgent()
    
    # Data to collect
    data = []

    # Iterate over 2-3 pages
    for page in range(1, 5):  # Adjust page range as needed
        print(f"Scraping Page {page}...")
        url = f"{search_url}&page={page}"
        headers = {"User-Agent": ua.random}

        # Fetch the page
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch page {page}, Status Code: {response.status_code}")
            continue
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all('div', class_='result')
        #print(results)

        for result in results:
            try:
                name = result.find('a', class_='business-name').text.strip() if result.find('a', class_='business-name') else "N/A"
                website = result.find('a', class_='track-visit-website')['href'] if result.find('a', class_='track-visit-website') else "N/A"
                phone = result.find('div', class_='phones phone primary').text.strip() if result.find('div', class_='phones phone primary') else "N/A"
                
                # Get street and Locality
                street_address = result.find('div', class_='street-address')
                locality = result.find('div', class_='locality')
                address = (street_address.text.strip() + " " + locality.text.strip()) if street_address and locality else "N/A"
                
                category = result.find('div', class_='categories').text.strip() if result.find('div', class_='categories') else "N/A"
                description = result.find('div', class_='snippet').text.strip() if result.find('div', class_='snippet') else "N/A"
                email = result.find('a', class_='email').text.strip() if result.find('a', class_='email') else "N/A"

                # Full link response
                # Extract the link to the detailed page
                link = result.find('a', class_='business-name')['href'] if result.find('a', class_='business-name') else None
                full_link = f"{base_url}{link}" if link else None
    
                # Extract details from the detailed page
                if full_link:
                    detail_response = requests.get(full_link, headers={"User-Agent": ua.random})
                    if detail_response.status_code == 200:
                        detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                        results_detail = detail_soup.find_all('dl')
                        for dl in results_detail:
                            description = dl.find('dd', class_='general-info').text.strip() if detail_soup.find('dd', class_='general-info') else description
                            email = dl.find('a', class_='email-business')['href'] if detail_soup.find('a', class_='email-business') else email
                    else:  
                        pass
                # Append to data list
                data.append({
                    "Company Name": name,
                    "Website URL": website,
                    "Contact Number": phone,
                    "Location/Address": address,
                    "Industry/Category": category,
                    "Company Description": description,
                    "E Mail": email
                })
            except Exception as e:
                print(f"Error parsing a result: {e}")
                continue

        # Introduce a delay to avoid being blocked
        time.sleep(2)
    
    # Save data to CSV
    df = pd.DataFrame(data)
    df.to_csv("companies_data.csv", index=False)
    print("Data saved to companies_data.csv")

# Run the scraper
scrape_companies()