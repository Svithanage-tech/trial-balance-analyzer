import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Trial Balance Analysis Tool", layout="wide")

st.title("📊 Trial Balance to Financials + Variance Analyzer")

# Step 1: Upload Trial Balance Files
st.header("1. Upload Trial Balance Files")

current_file = st.file_uploader("Upload Current Month Trial Balance (.xlsx)", type=["xlsx"])
last_file = st.file_uploader("Upload Last Month Trial Balance (.xlsx)", type=["xlsx"])

if current_file and last_file:
    # Read files
    current_tb = pd.read_excel(current_file)
    last_tb = pd.read_excel(last_file)
    
    # Preprocess: Create Balance Column
    def preprocess_tb(df):
        df.columns = df.columns.str.strip().str.lower()  # Clean column names to lower case
        if 'debit' not in df.columns or 'credit' not in df.columns:
            st.error("❌ Missing 'Debit' or 'Credit' columns in your uploaded file. Please check and upload the correct format.")
            st.stop()
        df["balance"] = df["debit"].fillna(0) - df["credit"].fillna(0)
        return df.rename(columns={"account code": "Account Code", "account name": "Account Name", "balance": "Balance"})

    current_tb = preprocess_tb(current_tb)
    last_tb = preprocess_tb(last_tb)
    
    # Merge for Variance Analysis
    merged_tb = pd.merge(current_tb, last_tb, on="Account Code", how="outer", suffixes=('_Current', '_Last'))
    merged_tb.fillna(0, inplace=True)
    merged_tb["Variance Amount"] = merged_tb["Balance_Current"] - merged_tb["Balance_Last"]
    merged_tb["Variance %"] = np.where(merged_tb["Balance_Last"] == 0, 
                                       np.nan, 
                                       (merged_tb["Variance Amount"] / merged_tb["Balance_Last"]) * 100)

    # Step 2: Display Financial Statements
    st.header("2. Financial Statements")

    # Simple categorization (You can improve this with mappings later)
    income_keywords = ['Revenue', 'Sales', 'Income']
    expense_keywords = ['Expense', 'Cost', 'Salary', 'Rent', 'Depreciation']

    def categorize_account(name):
        # Ensure name is a string and handle NaN values
        name = str(name) if name is not np.nan else ""
        if any(word.lower() in name.lower() for word in income_keywords):
            return "Income"
        elif any(word.lower() in name.lower() for word in expense_keywords):
            return "Expense"
        else:
            return "Other"

    current_tb["Category"] = current_tb["Account Name"].apply(categorize_account)
    last_tb["Category"] = last_tb["Account Name"].apply(categorize_account)

    # Income Statement
    st.subheader("📈 Profit & Loss Statement (Current Month)")
    income_statement = current_tb[current_tb["Category"].isin(["Income", "Expense"])]
    st.dataframe(income_statement.style.format({"Balance": "{:,.2f}"}), use_container_width=True)
    
    total_income = income_statement[income_statement["Category"] == "Income"]["Balance"].sum()
    total_expenses = income_statement[income_statement["Category"] == "Expense"]["Balance"].sum()
    net_profit = total_income - total_expenses
    
    st.metric("Net Profit", f"${net_profit:,.2f}")

    # Balance Sheet
    st.subheader("📋 Balance Sheet (Current Month)")
    balance_sheet = current_tb[current_tb["Category"] == "Other"]
    st.dataframe(balance_sheet.style.format({"Balance": "{:,.2f}"}), use_container_width=True)

    # Step 3: Variance Analysis
    st.header("3. Variance Analysis")

    # Add slider for users to choose the variance percentage threshold
    variance_threshold = st.slider(
        "Set Variance Percentage Threshold",
        min_value=0,
        max_value=50,
        value=10,  # default value
        step=1,
        help="Select the minimum percentage variance for highlighting"
    )
    st.write(f"Variance Threshold Set to: {variance_threshold}%")

    # Apply variance threshold logic for both positive and negative variances
    merged_tb["Variance Highlighted"] = merged_tb["Variance %"].apply(
        lambda x: abs(x) >= variance_threshold if pd.notnull(x) else False
    )

    st.dataframe(merged_tb[["Account Code", "Account Name_Current", "Balance_Last", "Balance_Current", 
                            "Variance Amount", "Variance %", "Variance Highlighted"]].style.format({
        "Balance_Last": "{:,.2f}",
        "Balance_Current": "{:,.2f}",
        "Variance Amount": "{:,.2f}",
        "Variance %": "{:.2f}%",
        "Variance Highlighted": lambda v: "✅" if v else "❌"
    }), use_container_width=True)

    # Step 4: Generate Smart Questions
    st.header("4. Generated Questions for Team")
    st.info("Questions are based on variances greater than or equal to the selected percentage threshold.")

    questions = []

    for idx, row in merged_tb.iterrows():
        if row["Variance Highlighted"]:
            account = row["Account Name_Current"]
            variance = row["Variance Amount"]
            percent = row["Variance %"]

            if variance > 0:
                q = f"🔵 {account} increased by {percent:.1f}% (${variance:,.0f}) compared to last month. Please explain."
            else:
                q = f"🔴 {account} decreased by {abs(percent):.1f}% (${abs(variance):,.0f}) compared to last month. Please explain."
            questions.append(q)

    if questions:
        for q in questions:
            st.write(q)
    else:
        st.success("✅ No significant variances found! All good.")

    # Step 5: Option to download variance report
    st.download_button(
        "📥 Download Variance Report (Excel)",
        data=merged_tb.to_csv(index=False),
        file_name="variance_report.csv",
        mime="text/csv"
    )

else:
    st.warning("⚡ Please upload both Current Month and Last Month Trial Balances to proceed.")
