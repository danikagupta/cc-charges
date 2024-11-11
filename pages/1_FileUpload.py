import streamlit as st
import PyPDF2
from io import BytesIO
from src.process_statement import process_text

import pandas as pd
import re 


st.title("File Upload")

def pdf_to_text(uploaded_file):
    try:
        # Create a bytes buffer from the uploaded file
        bytes_data = BytesIO(uploaded_file.getvalue())
        
        try:
            pdfReader = PyPDF2.PdfReader(bytes_data)
            count = len(pdfReader.pages)
            st.write(f"Page count: {count}")
            
            text = ""
            for i in range(count):
                try:
                    page = pdfReader.pages[i]
                    page_content = page.extract_text()
                    text = text + page_content
                    st.write(f"# PAGE {i}\n{page_content}\n\n\n")
                    st.divider()
                except Exception as e:
                    st.error(f"Error processing page {i}: {str(e)}")
                    continue
                    
            return text
            
        except PyPDF2.PdfReadError as e:
            st.error(f"Error reading PDF: {str(e)}")
            st.warning("The PDF file may be corrupted or password protected.")
            return None
            
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

def process_text_direct(text_content,filename):
    pattern = r'^\d{2}/\d{2}'

    full_list=[]
    for i,li in enumerate(text_content):
        li = li.strip()
        if re.match(pattern,li):
            split_result = li.split(' ', 1)  # Split once at the first space to separate the date
            split_result.extend(split_result.pop().rsplit(' ', 1))
            if len(split_result)==3:
                print(f"I={i},LI={li},SR={split_result}")
                full_list.append({"Date":split_result[0],"ChargedBy":split_result[1],"Amount":split_result[2]})
            else:
                print(f"{i}, DATE ONLY FOR {li}, split result len = {len(split_result)}")
        else:
            print(f"{i}, NO MATCH FOR {li}")
    df=pd.DataFrame(full_list)
    df.to_csv('datafiles/'+filename.replace('.txt','-direct.csv'),index=False)

#
# Direcly access Text Input    
#
st.markdown("Upload text directly")
uploaded_text = st.text_area("Enter Text","")
if st.button('Process Text'):
    process_text(uploaded_text,"Anonymous")
#
# Accept a PDF file using Streamlit
#
st.markdown("# Upload file: PDF")
uploaded_file=st.file_uploader("Upload PDF file",type="pdf")
if uploaded_file is not None:
    if st.button('Process PDF File'):
        pdf_text = pdf_to_text(uploaded_file)
        process_text(pdf_text,uploaded_file.name)
#
# Accept a Text file using Streamlit
#
st.markdown("# Upload file: Text")
uploaded_file=st.file_uploader("Upload text file",type="txt")
if uploaded_file is not None:
    if st.button('Process Text File'):
        file_text = uploaded_file.getvalue().decode("utf-8")
        with st.sidebar.expander("File contents"):
            st.write(file_text)
        process_text(file_text,uploaded_file.name)

#
# Accept a Text file using Streamlit
#
st.markdown("# Upload file DIRECT CODE: Text")
uploaded_file=st.file_uploader("Upload DIRECT file",type="txt")
if uploaded_file is not None:
    if st.button('Process DIRECT File'):
        filecontent=[]
        for line in uploaded_file:
            filecontent.append(line.decode('utf-8').strip())
        with st.sidebar.expander("File contents"):
            st.write(filecontent)
        process_text_direct(filecontent,uploaded_file.name)