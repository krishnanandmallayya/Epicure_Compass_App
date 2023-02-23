
import streamlit as st

from Allrecipe_search import *  
from Find_Match import *

st.markdown("<h1 style='text-align: left; color: DarkRed;font-family:Cursive;'>Epicure's Compass</h1>", unsafe_allow_html=True)
st.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
#import random
#st.sidebar.image(random.choice(['Images/compass_image.png','Images/compass_image2.png']))
st.sidebar.markdown("<h2 style='text-align: left; color: DarkRed;font-family:Cursive;'>A compass for your food journey</h2>", unsafe_allow_html=True)

st.sidebar.image('Images/compass_image.png',caption='(AI generated image, by Dalle-2)')
st.sidebar.title('Are you hungry?')


search_item=None   
names_list=None
search_item=st.sidebar.text_area('Enter your favorate dish (any cuisine)')

if(search_item):
    try:
        (names_list,hrefs_list) =Get_recipe_names(search_item)
        fav_item=st.sidebar.radio('Pick your fav item',names_list)
        href_item=hrefs_list[names_list.index(fav_item)]
        
        st.subheader('You selected '+ fav_item)
        image_url=Get_recipe_image(href_item)
        if(image_url):
            placeholder_im=st.image(image_url,width=400)
        st.text(href_item)
        st.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

    
    except:
        st.sidebar.error('Item not found. Reword your input')

show_map=False
button_match=False




if(names_list):  
    destination=st.sidebar.multiselect('Select Your Food Destination',['India'])
    if(destination==['India']):
        direction=st.sidebar.radio('Pick your region',['North','South','East','West'])
        show_map=True

        
        
        
if (show_map):
    if direction=='North':
        placeholder_txt=st.subheader('Exploring cuisines of North India')
        placeholder_im=st.image('Images/North_India.png',width=300)
        input_cuisine='north'
        placeholder_bar=st.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

    if direction=='South':
        placeholder_txt=st.subheader('Exploring cuisines of South India')
        placeholder_im=st.image('Images/South_India.png',width=300)
        input_cuisine='south'
        placeholder_bar=st.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

    if direction=='East':
        placeholder_txt=st.subheader('Exploring cuisines of East India')
        placeholder_im=st.image('Images/East_India.png',width=300)
        input_cuisine='east'
        placeholder_bar=st.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

    if direction=='West':
        placeholder_txt=st.subheader('Exploring cuisines of West India')
        placeholder_im=st.image('Images/West_India.png',width=300)
        input_cuisine='west'
        placeholder_bar=st.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
        
    level=st.sidebar.select_slider('How far out of your comfort food?', ['Play Safe', 'Somewhat Similar', 'Surprise Me'])
    button_match=st.sidebar.button('What\'s my recommendation ?')
    
if (button_match):
    (input_ingreds, input_cups, input_spoons)=Get_recipe_ingreds(href_item)
    with st.spinner('Finding your food...'): 
        target_foods=find_matches(input_cuisine,input_cups,input_spoons,level)   
        if (target_foods):
            st.header('The compass suggests ' + str(len(target_foods))+' items:')
            for i,food in enumerate(target_foods):
                (recipe_url,image_url)=Get_Archanas_food_image(food)
                st.subheader(str(i+1)+'. '+food)
                try:
                    st.image(image_url,width=400)
                except:
                    continue
                st.write("check out this [link](%s) for details:" % recipe_url)
        else:
            st.srror('Food not found')

        
