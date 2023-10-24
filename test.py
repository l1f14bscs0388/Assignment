import streamlit as st
import pandas as pd
from pandasai.llm import OpenAI
from pandasai import SmartDatalake
from dotenv import load_dotenv
import os
load_dotenv()

# Initialize OpenAI
llm = OpenAI()

# Create a sidebar for a more organized layout
st.sidebar.header("Upload Data", divider="rainbow")
with st.sidebar.form("my_form"):
    Table1 = st.file_uploader("Upload table1", type=["csv"])
    Table2 = st.file_uploader("Upload table2", type=["csv"])
    Table3 = st.file_uploader("Upload template table", type=["csv"])
    user_input1=st.text_input('Write the columns names you want to extract from Table-A and Table-B')
    submitted = st.form_submit_button("Submit")


# Function to preprocess data
def preprocessing(df_A, df_B):
    # ... [same preprocessing code] ...
    df_A.drop(["Policy_Start","FullName","Insurance_Plan","Policy_Num","Monthly_Premium"],axis=1,inplace=True)
    df_A["Date_of_Policy"]=pd.to_datetime(df_A["Date_of_Policy"].str.strip(),format='%d/%m/%Y')
    df_A["Policy_No"]=df_A["Policy_No"].str.replace("-","")
    df_A.rename(columns={"Employee_Name":"EmployeeName","Policy_ID":"PolicyNumber","Date_of_Policy":"Date","Insurance_Type":"Plan","Monthly_Cost":"Premium"},inplace=True)
    df_A.rename(columns={"Full_Name":"EmployeeName","Policy_No":"PolicyNumber","Date_of_Policy":"Date","Insurance_Type":"Plan","Monthly_Cost":"Premium"},inplace=True)
    df_B.drop(["StartDate","Name","PlanType","Policy_ID","PremiumAmount"],axis=1,inplace=True)
    df_B["PolicyDate"]=pd.to_datetime(df_B["PolicyDate"].str.strip(),format='%Y-%m-%d')
    df_B.rename(columns={"PolicyDate":"Date_of_Policy","Plan_Name":"Insurance_Type","Cost":"Monthly_Cost","PolicyID":"Policy_ID"},inplace=True)
    df_B.rename(columns={"Date_of_Policy":"Date","Employee_Name":"EmployeeName","Insurance_Type":"Plan","Policy_ID":"PolicyNumber","Monthly_Cost":"Premium"},inplace=True)
    return df_A,df_B

# Main app
st.title("Data Tables Processing with Chat")

# Rainbow lines for aesthetics
st.markdown("<hr style='border:1px solid rgba(255,0,0,0.5);'>", unsafe_allow_html=True)
if submitted:
    with st.spinner('Preprocessing data...'):
        df_A = pd.read_csv(Table1)
        df_B = pd.read_csv(Table2)
        if Table3:
            df_template = pd.read_csv(Table3)
        else:
            df_template=pd.DataFrame()
        df_A, df_B = preprocessing(df_A, df_B)
    
    lake = SmartDatalake([df_A, df_B, df_template], config={"llm": llm})
    
    # st.subheader("Enter Your Query", divider="rainbow")
    prompt_temp = 'Please combine the data frames df_A and df_B using a shared column. Convert the date column to the format "%d-%m-%Y". Extract and display the columns mentioned below in the output.:\n'
    with st.spinner('Processing your query...'):
        Answer_table = lake.chat(prompt_temp + user_input1)
    st.subheader("Answer table", divider="rainbow")
    st.write(Answer_table)
    st.subheader("Last Executed Code", divider="rainbow")
    st.code(lake.last_code_executed)

    # # Convert the Answer_table to CSV and provide a download button
    # try:
    #     csv = Answer_table.to_csv(index=False)
    #     st.download_button(
    #     label="Download Answer Table as CSV",
    #     data=csv,
    #     file_name="download.csv",
    #     mime="text/csv"
    # )
    # except:
    #     st.write("File not Downloaded")