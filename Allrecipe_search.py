from bs4 import BeautifulSoup
import re
import pandas as pd
import requests

import json
from ingreedypy import Ingreedy as Ingreedy



from gensim.models import Word2Vec
from gensim.parsing.preprocessing import remove_stopwords

from IPython.display import IFrame

def scrape_serving_size_allrecipes(soup):
    
    try: 
        soup_labels=soup.find_all('div',attrs={'class':"mntl-recipe-details__label"})
        labels=[label.contents[0] for label in soup_labels]
        soup_values=soup.find_all('div',attrs={'class':"mntl-recipe-details__value"})
        values=[value.contents[0] for value in soup_values]

        serv_size=float(values[labels.index('Servings:')])
    except: 
        serv_size=1
        
    return serv_size

def scrape_ingredients_allrecipes(soup):
    
    soup_item=soup.find('script',id="allrecipes-schema_1-0")
    contents=json.loads(soup_item.string)[0]
    #print(contents.keys())
    ingredients=contents['recipeIngredient']
    
    return ingredients

def parse_ingredients(ingred_string,serving_size):
    ingred_string=ingred_string.lower().strip()
    ing_dict={}
    ing_parse=Ingreedy().parse(ingred_string)
    
    try:
        ing_dict['ingredient']=ing_parse['ingredient']
    except:
        return None
    try:
        ing_dict['amount per serving']=ing_parse['quantity'][0]['amount']/serving_size
    except:
        ing_dict['amount per serving']=None
        
    try:
        ing_dict['unit']=ing_parse['quantity'][0]['unit']
    except:
        ing_dict['unit'] = None
    
    ing_dict['serving size']=serving_size
    
    return ing_dict

def Get_recipe_names(search_item):
    
    search_url='https://www.allrecipes.com/search?q='+search_item+' recipe'
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # now we extract hyperlinks to all search results for this item
    hrefs=[cards['href'] for cards in soup.find_all('a',id=re.compile('^mntl-card-list-items_'))]
    
    # filter only the hyperlinks that give recipe 
    regex=re.compile('^https:\/\/www\.allrecipes\.com\/recipe\/')
    hrefs_recipe=[i for i in hrefs if regex.match(i)]
    
    # get food item name from the hrefs
    regex=re.compile('(?<=\/)[^\/]*?(?=\/$)')
    names=[regex.findall(i)[0].replace('-',' ') for i in hrefs_recipe]
    
    
    n_recipes =len(names)
    if n_recipes>0 :
        return (names,hrefs_recipe)
    else:
        return None
       
def Get_recipe_ingreds(href_recipe):
    # go to webpage to extract ingredients
    response = requests.get(href_recipe)
    soup = BeautifulSoup(response.text, "html.parser")

    # get serving size
    serv_size=scrape_serving_size_allrecipes(soup)
    
    # get ingredients, and amount
    ingred_list=scrape_ingredients_allrecipes(soup)
    ingredients=[parse_ingredients(ing,serv_size) for ing in ingred_list]
    
    spoon_units=['teaspoon','tablespoon','pinch']
    spoon_ingreds =[item['ingredient'] for item in ingredients if item['unit'] in spoon_units]
    cup_ingreds =[item['ingredient'] for item in ingredients if item['unit'] not in spoon_units]
    
    
    return (ingredients,cup_ingreds,spoon_ingreds)
    

    
def Get_recipe_image(href_recipe):
    # go to webpage to extract url for recipe image
    try:
        response = requests.get(href_recipe)
        soup = BeautifulSoup(response.text, "html.parser")
        soup_item=soup.find_all('div',attrs={'class':'img-placeholder'})
        li=[]
        for i in soup_item:
            try:
                li.append(i.find('img')['data-hi-res-src'])
            except:
                continue

        for i in soup_item:
            try:
                li.append(i.find('img')['src'])
            except:
                continue
        p = re.compile('step|Step|steps|Steps|STEP|STEPS')
        image_url=[i for i in li if not p.search(i) if i != ''][0]
    except:
        image_url=None
    return image_url
        
        
    
    