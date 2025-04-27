{\rtf1\ansi\ansicpg1252\cocoartf2759
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import pandas as pd\
import numpy as np\
\
st.set_page_config(page_title="Trial Balance Analysis Tool", layout="wide")\
\
st.title("\uc0\u55357 \u56522  Trial Balance to Financials + Variance Analyzer")\
\
# Step 1: Upload Trial Balance Files\
st.header("1. Upload Trial Balance Files")\
\
current_file = st.file_uploader("Upload Current Month Trial Balance (.xlsx)", type=["xlsx"])\
last_file = st.file_uploader("Upload Last Month Trial Balance (.xlsx)", type=["xlsx"])\
\
if current_file and last_file:\
    # Read files\
    current_tb = pd.read_excel(current_file)\
    last_tb = pd.read_excel(last_file)\
    \
    # Preprocess: Create Balance Column\
    def preprocess_tb(df):\
        df["Balance"] = df["Debit"].fillna(0) - df["Credit"].fillna(0)\
        return df[["Account Code", "Account Name", "Balance"]]\
    \
    current_tb = preprocess_tb(current_tb)\
    last_tb = preprocess_tb(last_tb)\
    \
    # Merge for Variance Analysis\
    merged_tb = pd.merge(current_tb, last_tb, on="Account Code", how="outer", suffixes=('_Current', '_Last'))\
    merged_tb.fillna(0, inplace=True)\
    merged_tb["Variance Amount"] = merged_tb["Balance_Current"] - merged_tb["Balance_Last"]\
    merged_tb["Variance %"] = np.where(merged_tb["Balance_Last"] == 0, \
                                       np.nan, \
                                       (merged_tb["Variance Amount"] / merged_tb["Balance_Last"]) * 100)\
\
    # Step 2: Display Financial Statements\
    st.header("2. Financial Statements")\
\
    # Simple categorization (You can improve this with mappings later)\
    income_keywords = ['Revenue', 'Sales', 'Income']\
    expense_keywords = ['Expense', 'Cost', 'Salary', 'Rent', 'Depreciation']\
\
    def categorize_account(name):\
        if any(word.lower() in name.lower() for word in income_keywords):\
            return "Income"\
        elif any(word.lower() in name.lower() for word in expense_keywords):\
            return "Expense"\
        else:\
            return "Other"\
\
    current_tb["Category"] = current_tb["Account Name"].apply(categorize_account)\
    last_tb["Category"] = last_tb["Account Name"].apply(categorize_account)\
\
    # Income Statement\
    st.subheader("\uc0\u55357 \u56520  Profit & Loss Statement (Current Month)")\
    income_statement = current_tb[current_tb["Category"].isin(["Income", "Expense"])]\
    st.dataframe(income_statement.style.format(\{"Balance": "\{:,.2f\}"\}), use_container_width=True)\
    \
    total_income = income_statement[income_statement["Category"] == "Income"]["Balance"].sum()\
    total_expenses = income_statement[income_statement["Category"] == "Expense"]["Balance"].sum()\
    net_profit = total_income - total_expenses\
    \
    st.metric("Net Profit", f"$\{net_profit:,.2f\}")\
\
    # Balance Sheet\
    st.subheader("\uc0\u55357 \u56523  Balance Sheet (Current Month)")\
    balance_sheet = current_tb[current_tb["Category"] == "Other"]\
    st.dataframe(balance_sheet.style.format(\{"Balance": "\{:,.2f\}"\}), use_container_width=True)\
\
    # Step 3: Variance Analysis\
    st.header("3. Variance Analysis")\
\
    st.dataframe(merged_tb[["Account Code", "Account Name_Current", "Balance_Last", "Balance_Current", \
                            "Variance Amount", "Variance %"]].style.format(\{\
        "Balance_Last": "\{:,.2f\}",\
        "Balance_Current": "\{:,.2f\}",\
        "Variance Amount": "\{:,.2f\}",\
        "Variance %": "\{:.2f\}%"\
    \}), use_container_width=True)\
\
    # Step 4: Generate Smart Questions\
    st.header("4. Generated Questions for Team")\
    st.info("Questions are based on variances greater than 10% or $1,000 difference.")\
\
    questions = []\
\
    for idx, row in merged_tb.iterrows():\
        if abs(row["Variance Amount"]) > 1000 or (abs(row["Variance %"]) > 10):\
            account = row["Account Name_Current"]\
            variance = row["Variance Amount"]\
            percent = row["Variance %"]\
\
            if variance > 0:\
                q = f"\uc0\u55357 \u56629  \{account\} increased by \{percent:.1f\}% ($\{variance:,.0f\}) compared to last month. Please explain."\
            else:\
                q = f"\uc0\u55357 \u56628  \{account\} decreased by \{abs(percent):.1f\}% ($\{abs(variance):,.0f\}) compared to last month. Please explain."\
            questions.append(q)\
\
    if questions:\
        for q in questions:\
            st.write(q)\
    else:\
        st.success("\uc0\u9989  No significant variances found! All good.")\
\
    # Step 5: Option to download variance report\
    st.download_button(\
        "\uc0\u55357 \u56549  Download Variance Report (Excel)",\
        data=merged_tb.to_csv(index=False),\
        file_name="variance_report.csv",\
        mime="text/csv"\
    )\
\
else:\
    st.warning("\uc0\u9889  Please upload both Current Month and Last Month Trial Balances to proceed.")\
\
}