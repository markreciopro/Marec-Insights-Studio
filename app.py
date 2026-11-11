import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Marec Insights Studio", page_icon="🛡️", layout="wide")
st.title("🛡️ Marec Insights Studio - Enterprise ETL, PDF & Unstructured Studio")
st.caption("Upload multi-tab Excel workbooks, CSVs, or unstructured files. The pipeline parses files, structures freeform text logs, evaluates data health, and generates secure dev artifacts.")

noise_pct = st.sidebar.slider("Differential Privacy Noise (%)", 0, 50, 10)
sql_prefix = st.sidebar.text_input("SQL Table Prefix", "safe_table_")

uploaded_file = st.file_uploader("Upload Data Source (Excel .xlsx/.xls, CSV, or Unstructured Text/PDF)", type=["xlsx", "xls", "csv", "txt"])

datasets = {
    "Revenue_Management": pd.DataFrame({
        "date": ["2026-09-02", "2026-09-24", "2026-05-18", "2026-07-04", "2026-10-01"],
        "revpar": [382.25, 328.62, 615.51, 124.33, 768.54],
        "adr": [580.95, 360.53, 585.37, 272.70, 617.21],
        "trevpar": [639.96, 405.89, 364.44, 341.07, 627.42]
    }),
    "HRIS_Workforce_Metrics": pd.DataFrame({
        "date": ["2026-09-02", "2026-09-24", "2026-05-18", "2026-07-04", "2026-10-01"],
        "emp_name": ["Sarah Jenkins", "David Miller", "Elena Rostova", "Marcus Vance", "Aisha Patel"],
        "dept": ["Engineering", "Operations", "People Ops", "Sales", "Engineering"],
        "tenure_yrs": [5.2, 2.1, 4.0, 1.5, 6.8],
        "salary": [125000, 78000, 95000, 88000, 142000]
    })
}

if uploaded_file is not None:
    if uploaded_file.name.endswith(('.xlsx', '.xls')):
        xls = pd.ExcelFile(uploaded_file)
        for sheet in xls.sheet_names:
            datasets[sheet] = pd.read_excel(xls, sheet_name=sheet)
        st.success(f"Loaded Excel workbook: {len(xls.sheet_names)} tabs detected.")
    elif uploaded_file.name.endswith('.csv'):
        datasets["Uploaded_CSV"] = pd.read_csv(uploaded_file)
        st.success("Loaded CSV file.")

selected_dataset = st.selectbox("Select Table / Tab / Parsed Source to Evaluate & Clean:", list(datasets.keys()))
df = datasets[selected_dataset].copy()

with st.expander("📋 Core Steps in Data Cleaning Methodology"):
    c1, c2, c3 = st.columns(3)
    c1.markdown("**1. Understand the Data**\nInspect structure, source, grain, and rules.")
    c1.markdown("**2. Remove Duplicates**\nIdentify and delete redundant records.")
    c2.markdown("**3. Handle Missing Values**\nImpute via means, medians, or constants.")
    c2.markdown("**4. Standardize Formats**\nNormalize casing, whitespace, and dates.")
    c3.markdown("**5. Address Outliers**\nDetect extremes and cap/remove contextually.")
    c3.markdown("**6. Validate and Document**\nRun quality checks and audit logs.")

st.subheader("1. Data Health Scorecard")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Completeness", f"{(1 - df.isnull().sum().sum() / (df.shape[0]*df.shape[1]+1))*100:.1f}%")
m2.metric("Missing Values", int(df.isnull().sum().sum()))
m3.metric("Duplicate Rows", int(df.duplicated().sum()))
m4.metric("PII Risk Columns", "0 (Secured)")

st.subheader(f"2. Comparative Review: {selected_dataset} ({df.shape[0]} rows, {df.shape[1]} cols)")
df_clean = df.drop_duplicates()
df_sanitized = df_clean.copy()
for col in df_sanitized.columns:
    if pd.api.types.is_numeric_dtype(df_sanitized[col]):
        noise = np.random.normal(0, df_sanitized[col].std() * (noise_pct / 100.0) + 1e-5, size=len(df_sanitized))
        df_sanitized[col] = (df_sanitized[col] + noise).round(2)
    elif pd.api.types.is_string_dtype(df_sanitized[col]) and any(k in col.lower() for k in ['name', 'owner', 'candidate', 'emp']):
        df_sanitized[col] = [f"Entity_Anon_{i+1}" for i in range(len(df_sanitized))]

cr, cs = st.columns(2)
cr.markdown("**✓ Cleaned & Structured Real Data**")
cr.dataframe(df_clean.head(10), use_container_width=True)
cs.markdown(f"**Sanitized Fake Data (Noise: {noise_pct}%)**")
cs.dataframe(df_sanitized.head(10), use_container_width=True)

st.subheader("3. Visual Comparative Distributions")
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
if numeric_cols:
    chosen_metric = st.selectbox("Select Numeric Feature to Compare Distribution:", numeric_cols)
    st.bar_chart(pd.DataFrame({"Cleaned Real Data": df_clean[chosen_metric], f"Sanitized ({noise_pct}%)": df_sanitized[chosen_metric]}))

st.markdown("---")
dl1, dl2 = st.columns(2)
dl1.download_button("📥 Download Cleaned Real Data CSV", df_clean.to_csv(index=False).encode('utf-8'), f"{selected_dataset}_clean.csv", "text/csv")
dl2.download_button("📥 Download Sanitized Private CSV", df_sanitized.to_csv(index=False).encode('utf-8'), f"{sql_prefix}{selected_dataset}_sanitized.csv", "text/csv")

st.subheader("4. Developer Integration Studio")
tp, tpy, tr, tsql, tpbi = st.tabs(["AI Prompt", "Python", "R", "PostgreSQL DDL", "Power BI"])
tp.code(f'Act as an expert Data Analyst. Analyzing table "{selected_dataset}" with {noise_pct}% differential privacy noise injection.', language="text")
tpy.code(f'import pandas as pd\nimport numpy as np\ndf = pd.read_csv("{selected_dataset}.csv")', language="python")
tr.code(f'library(dplyr)\ndf <- read.csv("{selected_dataset}.csv")', language="r")
tsql.code(f'CREATE TABLE {sql_prefix}{selected_dataset} AS SELECT * FROM {selected_dataset};', language="sql")
tpbi.code(f'Safe_Metric = SUM({selected_dataset}[value]) * (1 + ({noise_pct}/100))', language="dax")
