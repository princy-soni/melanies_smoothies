import streamlit as st
from snowflake.snowpark.functions import col
# Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie.")

# Input: Smoothie name
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on smoothie will be:', name_on_order)

# Get Snowflake session and fruit list
cnx = st.connection("snowflake")
session = cnx.session()

fruit_df = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
fruit_list = [row['FRUIT_NAME'] for row in fruit_df.collect()]
smoothiefroot_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
sf_df = st.dataframe(data = smoothiefroot_response.json(), use_container_width = True)

# Multiselect for ingredients
ingredients_list = st.multiselect('Choose 5 ingredients:', fruit_list)

# Check for valid input
if st.button('Submit Order'):
    if not name_on_order.strip():
        st.warning("Please enter a name for your smoothie.")
    elif not ingredients_list:
        st.warning("Please select at least one ingredient.")
    elif len(ingredients_list) > 5:
        st.warning("Please select **up to 5 ingredients only**.")
    else:
        ingredients_string = ' '.join(ingredients_list)
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders(name_on_order, ingredients)
            VALUES ('{name_on_order}', '{ingredients_string}')
        """
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")
        # Optional: Show the SQL query (for debugging)
        # st.write(my_insert_stmt)
        st.stop()
import requests
