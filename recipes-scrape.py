import requests
import json
from bs4 import BeautifulSoup
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}   
    
def get_ingredients(soup):
    ingredient_elements = soup.find_all('li', class_='wprm-recipe-ingredient')

    # individual ingredient item
    items = []
    # ingredient with amount, unit, name, and notes
    formatted_ingredients = []
    
    for element in ingredient_elements:
        amount = element.find('span', class_='wprm-recipe-ingredient-amount')
        unit = element.find('span', class_='wprm-recipe-ingredient-unit')
        name = element.find('span', class_='wprm-recipe-ingredient-name')
        notes = element.find('span', class_='wprm-recipe-ingredient-notes')
        
        # build the ingredient string
        parts = []
        if amount and amount.text.strip():
            parts.append(amount.text.strip())
        if unit and unit.text.strip():
            parts.append(unit.text.strip())
        if name and name.text.strip():
            parts.append(name.text.strip())
            
            # handling ingredients with 'and' in the name
            item = name.text.strip()
            if item.find(' and ') != 1:
                items.extend(item.lower().split(' and '))
            else:
                items.lower().append(item)
                
        if notes and notes.text.strip():
            notes_text = notes.text.strip()
            if notes_text != "see notes":  # Fixed the comparison
                parts.append(f"({notes_text})")
        
        # combine the parts for display
        formatted_ingredients.append(" ".join(parts))
    
    return formatted_ingredients, items

def get_instructions(soup):
    instructions = []
    for div in soup.find_all('div', class_='wprm-recipe-instruction-text'):
        instructions.append(div.text.strip())
    return instructions

def get_prep_time(soup):
    try:
        prep_container = soup.find(lambda tag: tag.name == 'div' and 'wprm-recipe-prep-time-container' in tag.get('class', []))
        
        if not prep_container:
            return 0
            
        time_value = prep_container.find(lambda tag: tag.name == 'span' and 'wprm-recipe-prep_time' in tag.get('class', []))
        prep_time = time_value.text.strip()
        number_match = re.search(r'\d+',    prep_time)
            
        return  prep_time
        
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
    
def get_cook_time(soup):
    try:
        cook_container = soup.find(lambda tag: tag.name == 'div' and 'wprm-recipe-cook-time-container' in tag.get('class', []))
        
        if not cook_container:
            return 0
            
        time_value = cook_container.find(lambda tag: tag.name == 'span' and 'wprm-recipe-cook_time' in tag.get('class', []))
        cook_time = time_value.text.strip()
        number_match = re.search(r'\d+', cook_time)
            
        return cook_time
        
    except ValueError as e:
        return {"error": f"Error parsing time value: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
    
def scrape_recipe(url):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        prep_time = get_prep_time(soup)
        cook_time = get_cook_time(soup)
        ingredients, items = get_ingredients(soup)
        instructions = get_instructions(soup)
        
        return [prep_time, cook_time, ingredients, instructions, items]
    except requests.RequestException as e:
        print(f"Error fetching the recipe: {e}")
        return None, None

if __name__ == '__main__':
    
    with open('scraped-links.json', 'r') as file:
        json_links = json.load(file)
    
    json_recipes = []
    num = len(json_links)

    for i in range(len(json_links)):
        result = scrape_recipe(json_links[i][2])
        if result[0] == 0:
            continue
        
        json_recipes.append({
            "name": json_links[i][0],
            "image": json_links[i][1],
            "link": json_links[i][2],
            "prep_time": result[0],
            "cook_time": result[1],
            "ingredients": result[2],
            "instructions": result[3],
            "ingredient_item": result[4]})
        
        print(i)

    with open('scraped-recipes.json', 'w') as file:
        json.dump(json_recipes, file)