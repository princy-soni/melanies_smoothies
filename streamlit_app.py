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
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
# External API call to fruityvice (this returns JSON)
ingredients_list = st.multiselect('Choose 5 ingredients:', my_dataframe, max_selections =5 )


if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + 'Nutrition Information')
        smoothiefroot_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)


# Check for valid response
# if smoothiefroot_response.status_code == 200:
#     fruit_json = smoothiefroot_response.json()
#     fruit_df_display = pd.json_normalize(fruit_json)  # Convert nested JSON to flat DataFrame
#     st.dataframe(fruit_df_display, use_container_width=True)
# else:
#     st.error("Failed to fetch data from Fruityvice API. Please try again later.")

# Multiselect for ingredients

# Submit button with validation
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
