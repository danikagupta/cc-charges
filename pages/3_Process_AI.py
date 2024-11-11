import streamlit as st

import os
import streamlit as st
from datetime import datetime
import pandas as pd

from src.process_statement import process_one_charging_entity

def work_with_file(filepath):
    st.write(f"Working with file {filepath}")
    df=pd.read_csv(filepath)
    if 'Use' not in df.columns:
        df['Use']=True
    if 'Merchant' not in df.columns:
        df['Merchant']='Unknown'
    if 'Category' not in df.columns:
        df['Category']='Unknown'
    df['Amount'] = pd.to_numeric(df['Amount'].astype(str).str.replace(',', ''), errors='coerce')
    df = df.loc[:, ~df.columns.str.startswith('Unnamed')]
    filtered_df = df[df["Merchant"] == "Unknown"]
    print(f"Filtered count is {filtered_df.shape[0]}")
    random_row = filtered_df.sample(n=1) if not filtered_df.empty else None

# Display the random row
    if random_row is not None:
        entity=random_row.iloc[0]['ChargedBy']
        print(entity)
        merchant,category=process_one_charging_entity(entity)
        random_row.at[random_row.index[0], 'Merchant']=merchant
        random_row.at[random_row.index[0], 'Category']=category
        st.write(f"Entity={entity} merchant={merchant},category={category}")
        df.loc[random_row.index[0]] = random_row.iloc[0]
        #st.dataframe(df)
        df.to_csv(filepath,index=False)
    else:
        print("No matching rows found.")


def pick_file(directory_path):
    file_details = []
    if os.path.exists(directory_path):
        for file_name in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file_name)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)  # Get file size in bytes
                file_date = datetime.fromtimestamp(os.path.getmtime(file_path))  # Get last modified date
                file_details.append((file_name, file_size, file_date))
    else:
        st.error("Directory not found. Please check the path.")

    # Display files and allow the user to select one
    if file_details:
        # Create a dictionary for displaying formatted info
        file_display = {f"{name} - {size/1024:.2f} KB - {date}": name for name, size, date in file_details}
        selected_file = st.selectbox("Select a file", list(file_display.keys()))

        # Show the selected file's details
        if selected_file:
            chosen_file_name = file_display[selected_file]
            st.write(f"You selected: {chosen_file_name}")
            chosen_file_path = os.path.join(directory_path, chosen_file_name)
            record_count=st.number_input("How many records",value=10)
            if st.button("Process records"):
                for i in range(record_count):
                    work_with_file(chosen_file_path)

    else:
        st.write("No files found in the directory.")


pick_file('datafiles')