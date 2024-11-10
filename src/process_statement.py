import streamlit as st

import os

from langchain_openai import ChatOpenAI

from langchain_core.messages import SystemMessage, HumanMessage
from datetime import date
from typing import List,Tuple
from enum import Enum
from pydantic import BaseModel

os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_API_KEY"]=st.secrets['LANGCHAIN_API_KEY']
os.environ["LANGCHAIN_PROJECT"]="CC_CHARGES"
os.environ['LANGCHAIN_ENDPOINT']="https://api.smith.langchain.com"

Category = Enum('Category', 'Entertainment Food Education Other')

class OneCharge(BaseModel):
    transactionDate: date
    chargeStatement: str
    chargedAmount: float
    merchant: str
    category: Category
    

class ChargeList(BaseModel):
    charges: List[OneCharge]

def process_text(uploaded_text:str, filename:str):
    model=ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=st.secrets["OPENAI_API_KEY"])
    SYSTEM_PROMPT=f"""
    Here is the user's credit card statement. 
    Review each charge.
    Provide a response as a list of charges, where for each charge you provide a transaction date, charging entity, and charged amount.
    Please format the transaction date as YYYY-MM-DD.
    For each charge, identify the merchant if possible. Else leave merchant as Unknown.
    Classify the charge as one of the following four categories: Entertainment, Food, Education, Other
    """

    msgs=[SystemMessage(content=SYSTEM_PROMPT),HumanMessage(content=uploaded_text)]
    llm_response=model.with_structured_output(ChargeList).invoke(msgs)
    with st.expander("Model response"):
        st.write(f"LLM Response: {llm_response}")
        st.dataframe(llm_response)
    st.success(f"SRC Finished processing {filename}")


