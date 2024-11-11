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
    model=ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=st.secrets["OPENAI_API_KEY"])
    ENTITY_PROMPT=f"""
    Here is the charging entity name for one entry on the user's credit card statement. 
    Please identify the merchant if possible. Else leave merchant as TBD.
    Classify the charge as one of the following categories: Communication, Clothing, Education, Entertainment, Delivery, Groceries, Home, Insurance, Medical, Politics, Supplies, or Other
    Classify the charge as Unknown if the merchant is Unknown.

    Here are a few examples:
    For "AMAZON MKTPL*HJ5KU52R3 Amzn.com/bill WA", merchant is "Amazon Marketplace" and category is "Supplies"
    For "DD *DOORDASH BOUDINBAK 855-431-0459 CA", merchant is "Boudin" and category is "Delivery" as this is delivered by Doordash.
    For "GOOGLE *Colab cc@google.com CA", merchant is "Google" and category is "AIClub"
    For "Amazon Groce*039T59ZH3 Amzn.com/bill WA", merchant is "Amazon Groceries" and category is "Delivery"
    For "AEROGARDEN.COM AEROGARDEN.CO OH", merchant is "Aerogarden" and category is "Education"
    For "DEPOP WWW.DEPOP.COM NY", merchant is "DePop" and category is "Clothing"
    For "UNITED 0162430951543 UNITED.COM TX", merchant is "United Airlines" and category is "Education"
    For "ACTBLUE_DONATETODEMS HTTPSSECURE.A MA", merchant is "ActBlue" and category is "Politics"
    For "AJ TUTORING INC. WWW.AJTUTORIN CA", merchant is "A J Tutoring" and category is "Education"
    For "SPI*PURE 888-813-7873 NY", merchant is "Pure Insurance" and category is "Insurance"
    For "SATELLITE WORKSPACE CENTE 831-2222100 CA", merchant is "Satellite Workspace" and category is "AIClub"
    For "UNEX-UCOE/SCOUT 831-459-5294 CA", merchant is "UC Scout" and category is "Education"
    For "MILL INDUSTRIES INC. HTTPSWWW.MILL CA", merchant is "Mill industries" and category is "Home"
    For "DEMENG GIVEGREEN 202-6306597 DC", merchant is "GiveGreen" and category is "Politics"
    For "NIPS 858-453-4100 CA", merchant is "Neurips" and category is "Education"
    For "99PLEDG*MS. SUNDARAM A 650-241-2803 CA", merchant is "Sundaram" and category is "Charity"
    For "EB *2024 IIT BAY AREA 8014137200 CA", merchant is "IIT Bay Area" and category is "Misc"
    For "HOME ONLIN* INDIA CASH WWW.HOMESOME. CA", merchant is "India Cash Carry" and category is "Delivery"
    For "DR. WILLIAM CHU TCBACKOFFICE@ CA", merchant is "Dr Chu" and category is "Medical"
    For "PAYPAL *TESTLODGE 35314369001". merchant is "TestLodge" and category is "AIClub" 
    For "WEEE INC. 510-573-4967 CA", merchant is "Wee" and category is "Delivery"
    For "HAVA.CO STOCKHOLM", merchant is "Hava" and category is "Misc"
    For "DAIR.AI LIMITED LONDON", merchant is "Dair" and category is "Misc"
    """

    msgs=[SystemMessage(content=ENTITY_PROMPT),HumanMessage(content=entity)]
    llm_response=model.with_structured_output(OneEntity).invoke(msgs)
    merchant=llm_response.merchant
    category=llm_response.category
    return merchant,category

