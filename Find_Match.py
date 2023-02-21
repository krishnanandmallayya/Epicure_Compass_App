from bs4 import BeautifulSoup
import re
import pandas as pd
import requests

import json
from ingreedypy import Ingreedy as Ingreedy
from collections import defaultdict

from gensim.models import Word2Vec
from gensim.parsing.preprocessing import remove_stopwords
from gensim.models import KeyedVectors

import pickle

import spacy
nlp = spacy.load("en_core_web_sm")

import numpy as np 

    

def get_Archanas_cuisine_sentences(input_cuisine):
    with open( "Capstone_Data/Indian_regional_cuisines_raw_data.pkl",'rb') as f:
        Archanas_data=pickle.load(f)

    (cup_sents,spoon_sents,Indian_cup_sents,Indian_spoon_sents,Indian_recipe_list)=Archanas_data
    
    cuisine_cup_sents=Indian_cup_sents[input_cuisine]
    cuisine_spoon_sents=Indian_spoon_sents[input_cuisine]
    cuisine_recipe_list=Indian_recipe_list[input_cuisine]
        
    return(cuisine_cup_sents,cuisine_spoon_sents,cuisine_recipe_list)



def find_matches(input_cuisine,input_cup_ingreds, input_spoon_ingreds,level):
    
    def parse_names(name_list):
        parsed_list=[]
        for name in name_list:
            try:
                name=re.sub('[^a-zA-Z]+', ' ', name).strip().lower()   # replace any non alphabet with space
                name=re.sub('^salt', ' ', name).strip().lower()   # remove salt
                parsed_name=[w.lemma_ for w in nlp(name)]
                parsed_list+=parsed_name
            except:
                continue
        return parsed_list

    
    
    def get_similarity(input_ingred, target_ingred, w2v_model,cutoff):
        
        vocab_input=[i for i in input_ingred if i in w2v_model.wv]
        vocab_target=[i for i in target_ingred if i in w2v_model.wv]
    
        if (vocab_input==[] or vocab_target==[]):
            return (0,0,0)
    
        overlap=[]
        for i in vocab_input:
            overlap.append(max([w2v_model.wv.similarity(i,j) for j in vocab_target]))
        match=[i for i in overlap if i>cutoff]
        s1=sum(match)/(len(vocab_input)+len(vocab_target))
        s2=sum(match)/(len(vocab_input))
        s3=sum(match)/(np.sqrt(len(vocab_input)*len(vocab_target)))
        
        similarity=(s1,s2,s3)
        
    
        return similarity
    
    

    def get_similar_cuisine(input_cup_list,input_spoon_list,level):
        
        if(level=='Play Safe'):
            
            with open('Capstone_Data/Archana_ingredients_w2v_cup_sg.model', 'rb') as f:
                w2v_cup = pickle.load(f)
            with open('Capstone_Data/Archana_ingredients_w2v_spoon_sg.model', 'rb') as f:
                w2v_spoon = pickle.load(f)
            cutoff=0.9
            spoon_weight=1/4
        if(level=='Somewhat Similar'):
            with open('Capstone_Data/One_million_ingredients_w2v_sg.model', 'rb') as f:
                w2v_model = pickle.load(f)
            
            w2v_cup=w2v_model
            w2v_spoon=w2v_model
            cutoff=0.8
            spoon_weight=1/4

        if(level=='Surprise Me'):
            with open('Capstone_Data/One_million_ingredients_w2v_sg.model', 'rb') as f:
                w2v_model = pickle.load(f)
            
            w2v_cup=w2v_model
            w2v_spoon=w2v_model
            cutoff=0.6
            spoon_weight=1/2
            
        cup_similarity_list=[get_similarity(input_cup_list,items,w2v_cup,cutoff) for items in cuisine_cup_sents]
        spoon_similarity_list=[get_similarity(input_spoon_list,items,w2v_spoon,cutoff) for items in cuisine_spoon_sents]
        similarity_list=np.array(cup_similarity_list)+spoon_weight*np.array(spoon_similarity_list)
        most_similar_arg=np.argmax(similarity_list,axis=0)
        most_similar_cuisine=list(set([cuisine_recipe_list[i] for i in most_similar_arg]))
        return most_similar_cuisine
    
    
    
    
    
    
    Archanas_data=get_Archanas_cuisine_sentences(input_cuisine)
    (cuisine_cup_sents,cuisine_spoon_sents,cuisine_recipe_list)= Archanas_data
    
    
    input_cup_list=parse_names(input_cup_ingreds)
    input_spoon_list=parse_names(input_spoon_ingreds)
    similar_foods=get_similar_cuisine(input_cup_list,input_spoon_list, level)
        
    return similar_foods


def Get_Archanas_food_image(recipe_name):
    with open("Capstone_Data/Archanas_recipe_url.json", "r") as infile:
        url_dict=json.load(infile)
        
    recipe_url=url_dict[recipe_name]
    try:
        response = requests.get(recipe_url)
        soup = BeautifulSoup(response.text)
        image_url=soup.find_all('div',attrs={'class':'recipe-image'})[0].find('img')['src']
        image_url='https://www.archanaskitchen.com'+image_url
    except:
        image_url=None
    return (recipe_url,image_url)
    
