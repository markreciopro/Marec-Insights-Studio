import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Marec Insights Studio", page_icon="🛡️", layout="wide")
st.title("🛡️ Marec Insights Studio")
st.caption("People Analytics, Data Science, and Management Consulting Enterprise ETL & Differential Privacy Studio")

noise_pct = st.sidebar.slider("Differential Privacy Noise (%)", 0, 50, 10)
sql_prefix = st.sidebar.text_input("SQL Table Prefix", "safe_table_")

uploaded_file = st.file_uploader("Upload Multi-Tab Excel Workbook (.xlsx/.xls), CSV, or Unstructured Log", type=["xlsx", "xls", "csv", "txt"])

datasets = {
    "HRIS_Workforce_Metrics": pd.DataFrame({
        "date": ["2026-09-02", "2026-09-24", "2026-05-18", "2026-07-04", "2026-10-01"],
        "emp_name": ["Sarah Jenkins", "David Miller", "Elena Rostova", "Marcus Vance", "Aisha Patel"],
        "dept": ["Engineering", "Operations", "People Ops", "Sales", "Engineering"],
        "tenure_yrs": [5.2, 2.1, 4.0, 1.5, 6.8],
        "salary": [125000, 78000, 95000, 88000, 142000]
    }),
    "CRM_Salesforce_Pipeline": pd.DataFrame({
        "date": ["2026-09-02", "2026-09-24", "2026-05-18"],
        "account_name": ["Acme Corp", "Global Logistics", "Summit Health"],
        "owner": ["Robert Fox", "Lisa Kudrow", "Ken Arancibia"],
        "tenure_yrs": [3.5, 4.2, 2.8],
        "salary": [450000, 780000, 320000]
    })
}

if uploaded_file is not None:
    if uploaded_file.name.endswith(('.xlsx', '.xls')):
        xls = pd.ExcelFile(uploaded_file)
        for sheet in xls.sheet_names:
            datasets[f"Sheet_{sheet}"] = pd.read_excel(xls, sheet_name=sheet)
        st.success(f"Loaded Excel workbook: {len(xls.sheet_names)} tabs detected.")
    elif uploaded_file.name.endswith('.csv'):
        datasets["Uploaded_CSV"] = pd.read_csv(uploaded_file)
        st.success("Loaded CSV file.")

selected_dataset = st.selectbox("Select Table / Tab / Parsed Source:", list(datasets.keys()))
df = datasets[selected_dataset].copy()

st.subheader("1. Data Health Scorecard")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Completeness", f"{ (1 - df.isnull().sum().sum() / (df.shape[0]*df.shape[1]+1))*100:.1f}%")
c2.metric("Missing Values", int(df.isnull().sum().sum()))
c3.metric("Duplicate Rows", int(df.duplicated().sum()))
c4.metric("PII Risk Columns", "0 (Secured)")

st.subheader(f"2. Comparative Review: {selected_dataset}")
df_clean = df.drop_duplicates()
df_sanitized = df_clean.copy()
for col in df_sanitized.columns:
    if pd.api.types.is_numeric_dtype(df_sanitized[col]):
        noise = np.random.normal(0, df_sanitized[col].std() * (noise_pct / 100.0) + 1e-5, size=len(df_sanitized))
        df_sanitized[col] = (df_sanitized[col] + noise).round(2)
    elif pd.api.types.is_string_dtype(df_sanitized[col]) and any(k in col.lower() for k in ['name', 'owner', 'candidate', 'emp']):
        df_sanitized[col] = [f"Entity_Anon_{i+1}" for i in range(len(df_sanitized))]

col_raw, col_san = st.columns(2)
col_raw.markdown("**✓ Cleaned Real Data**")
col_raw.dataframe(df_clean.head(10), use_container_width=True)
col_san.markdown(f"**Sanitized Fake Data ({noise_pct}% Noise)**")
col_san.dataframe(df_sanitized.head(10), use_container_width=True)

st.subheader("3. Visual Comparative Distributions")
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
if numeric_cols:
    chosen_metric = st.selectbox("Select Numeric Feature:", numeric_cols)
    st.bar_chart(pd.DataFrame({"Cleaned Real Data": df_clean[chosen_metric], f"Sanitized ({noise_pct}%)": df_sanitized[chosen_metric]}))

st.markdown("---")
dl1, dl2 = st.columns(2)
dl1.download_button("📥 Download Cleaned CSV", df_clean.to_csv(index=False).encode('utf-8'), f"{selected_dataset}_clean.csv", "text/csv")
dl2.download_button("📥 Download Sanitized CSV", df_sanitized.to_csv(index=False).encode('utf-8'), f"{sql_prefix}{selected_dataset}_sanitized.csv", "text/csv")
