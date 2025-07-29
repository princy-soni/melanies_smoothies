import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie.")

# Input: Smoothie name
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on smoothie will be:', name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit list from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Multiselect for ingredients
fruit_list = pd_df['FRUIT_NAME'].tolist()
ingredients_list = st.multiselect('Choose up to 5 ingredients:', fruit_list, max_selections=5)

# Show API data
if ingredients_list:
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        # st.write(f"The search value for {fruit_chosen} is {search_on}")
        st.subheader(f"{fruit_chosen} Nutrition Information")

        response = requests.get(f"https://fruityvice.com/api/fruit/" + search_on)
        if response.status_code == 200:
            fruit_json = response.json()
            fruit_df_display = pd.json_normalize(fruit_json)
            st.dataframe(fruit_df_display, use_container_width=True)
        else:
            st.warning(f"Nutrition info for {fruit_chosen} not found.")

# Submit order
if st.button('Submit Order'):
    if not name_on_order.strip():
        st.warning("Please enter a name for your smoothie.")
    elif not ingredients_list:
        st.warning("Please select at least one ingredient.")
    elif len(ingredients_list) > 5:
        st.warning("Please select up to 5 ingredients only.")
    else:
        ingredients_string = ', '.join(ingredients_list)
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders(name_on_order, ingredients)
            VALUES ('{name_on_order}', '{ingredients_string}')
        """
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")
        st.stop()
