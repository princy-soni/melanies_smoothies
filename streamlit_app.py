import streamlit as st
# from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col


# Title
st.title(":cup_with_straw: Customize Your Smoothie!:cup_with_straw:")
st.write("Choose the fruit you want in your custom smoothie")

# Input: Smoothie name
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on smoothie will be:', name_on_order)

# Get Snowflake session and fruit list
cnx = st.connection("snowflake")
session = cnx.session()
fruit_df = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
fruit_list = [row['FRUIT_NAME'] for row in fruit_df.collect()]

# Multiselect for ingredients
ingredients_list = st.multiselect('Choose 5 ingredients:', fruit_list)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(name_on_order, ingredients)
        VALUES ('{name_on_order}', '{ingredients_string}')
    """

    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
        st.write(my_insert_stmt)
        st.stop()
# import requests
# smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
# st.text(smoothiefroot_response.json())
# External API call

