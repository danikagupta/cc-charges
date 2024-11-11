import streamlit as st

import os

from langchain_openai import ChatOpenAI

import pandas as pd

from langchain_core.messages import SystemMessage, HumanMessage
from datetime import date
from typing import List,Tuple,Literal
from enum import Enum
from pydantic import BaseModel

os.environ["LANGCHAIN_TRACING_V2"]="false"
os.environ["LANGCHAIN_API_KEY"]=st.secrets['LANGCHAIN_API_KEY']+"XXXXXX"
os.environ["LANGCHAIN_PROJECT"]="CC_CHARGES"
os.environ['LANGCHAIN_ENDPOINT']="https://api.smith.langchain.com"

EXAMPLE_FILE="examples.txt"

#Category = Enum('Category', 'Entertainment Food Education Other')

class OneCharge(BaseModel):
    transactionDate: date
    chargeStatement: str
    chargedAmount: float
    merchant: str
    category: Literal["Entertainment", "Food", "Education", "Other"]

class OneEntity(BaseModel):
    merchant: str
    category: str
    

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
    charges_dicts = [charge.dict() for charge in llm_response.charges]
    df = pd.DataFrame(charges_dicts)
    csv_filename='datafiles/'+filename.replace('.txt','.csv')
    df.to_csv(csv_filename,index=False)
    with st.expander("Model response"):
        st.dataframe(df)
    st.success(f"SRC Finished processing {filename}")

def process_one_charging_entity(entity:str):

    with open(EXAMPLE_FILE,'r') as f:
        example_text=f.read()
    #st.write(f"Example text:\n\n{example_text}")
    model=ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=st.secrets["OPENAI_API_KEY"])
    ENTITY_PROMPT=f"""
    Here is the charging entity name for one entry on the user's credit card statement. 
    Please identify the merchant if possible. Else leave merchant as TBD.
    Classify the charge as one of the following categories: Communication, Clothing, Education, Entertainment, Delivery, Groceries, Home, Insurance, Medical, Politics, Supplies, or Other
    Classify the charge as Unknown if the merchant is Unknown.

    {example_text}
    """

    msgs=[SystemMessage(content=ENTITY_PROMPT),HumanMessage(content=entity)]
    llm_response=model.with_structured_output(OneEntity).invoke(msgs)
    merchant=llm_response.merchant
    category=llm_response.category
    return merchant,category

