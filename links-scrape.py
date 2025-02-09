import requests
import json
from bs4 import BeautifulSoup
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
    
def scrape_page(url):
    results = []
    images = []
    names = []
    links = []

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        entries_img = soup.find_all('img', class_="aligncenter post-image entry-image")
        for img in entries_img:
            img_link = img.get('src')
            if img_link:
                images.append(img_link)
            else:
                images.append(0)
        
        entries = soup.find_all('a', class_='entry-title-link')
        for entry in entries:
            name = entry.get_text().strip()
            link = entry.get('href')
            names.append(name)
            links.append(link)
            
        
        for i in range(len(images)):
            if images[i] == 0:
                continue
            results.append([names[i], images[i], links[i]])
            
        return results
        
    except requests.RequestException as e:
        print(f"Failed to connect to {url}")
        print(e)
        return None
        
if __name__ == '__main__':
    results = []
    for i in range(2, 225):
        print(i)
        url = f"https://panlasangpinoy.com/recipes/page/{i}/"
        results.extend(scrape_page(url))

    final = []
    # Skip other content like "Top 10 Filipino Foods"
    for result in results:
        if re.search(r"[0-9?:@']", result[0], re.IGNORECASE) == None and re.search(r"What", result[0], re.IGNORECASE) == None and re.search(r"How", result[0], re.IGNORECASE) == None:
            final.append(result)
    
    print(len(final))
    print(len(results)-len(final))
    
    with open('scraped-links.json', 'w') as file:
        json.dump(final, file) 
    