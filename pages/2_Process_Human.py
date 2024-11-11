import streamlit as st

import os
import streamlit as st
from datetime import datetime
import pandas as pd

def table_change_handler():
    print("Invoked table change handler")
    edits=st.session_state.get("edited_data")
    if edits and edits["edited_rows"]:
        edited_rows=edits["edited_rows"]
        for edit_records in edited_rows:
            print(f"Edit record: {edit_records}, Change={edited_rows[edit_records]}")

        #print(f"Edited rows is {edited_rows}")

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
    edited_table=st.data_editor(df,disabled=("Date","ChargedBy","Amount"),on_change=table_change_handler, key="edited_data",hide_index=True)
    if edited_table is not None:
        edited_table.to_csv(filepath,index=False)

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
            work_with_file(chosen_file_path)
    else:
        st.write("No files found in the directory.")


pick_file('datafiles')