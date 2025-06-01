import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import re

def create_connection(server, database):
    connection_string = f"mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    engine = create_engine(connection_string)
    return engine

st.title("🛠️ Admin Portal - Upload & Manage SQL Server Data")

# --- Database Connection ---
server = st.text_input('Server', value='localhost\\SQLEXPRESS')
database = st.text_input('Database')

if st.button('Connect to Database'):
    try:
        engine = create_connection(server, database)
        st.session_state.conn = engine
        st.success("✅ Connected to the database successfully!")
    except Exception as e:
        st.error(f"❌ Connection failed: {e}")

# --- File Upload ---
uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])
df = None

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        st.write("📄 Uploaded Data Preview")
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error reading file: {e}")

# --- Upload to Database ---
if df is not None:
    table_name = st.text_input('Target Table Name')

    if st.button('Upload to Database', key='upload'):
        if table_name:
            try:
                if 'conn' in st.session_state:
                    df.to_sql(table_name, con=st.session_state.conn, if_exists='replace', index=False)
                    st.success(f"✅ Table `{table_name}` uploaded successfully.")
                else:
                    st.error("❗ Please connect to the database first.")
            except Exception as e:
                st.error(f"Upload failed: {e}")

    # --- Null & Duplicate Checks ---
    if st.button('Calculate Nulls & Duplicates', key='calculate'):
        st.write("🧮 Null Values:")
        st.write(df.isnull().sum())
        st.write("📑 Duplicate Rows:")
        st.write(df.duplicated().sum())

    if st.button('Remove Nulls & Duplicates', key='clean'):
        df_cleaned = df.dropna().drop_duplicates()
        st.dataframe(df_cleaned)
        st.success("✅ Data cleaned successfully.")

        if st.button('Upload Cleaned Data', key='upload_cleaned'):
            if table_name:
                try:
                    if 'conn' in st.session_state:
                        df_cleaned.to_sql(table_name, con=st.session_state.conn, if_exists='replace', index=False)
                        st.success(f"✅ Cleaned data uploaded to `{table_name}`.")
                    else:
                        st.error("❗ Connect to the database first.")
                except Exception as e:
                    st.error(f"Upload failed: {e}")

# --- SQL Query Execution ---
query = st.text_area("Enter your SQL query:")

if st.button("Execute Query"):
    if 'conn' in st.session_state:
        try:
            result = pd.read_sql_query(query, con=st.session_state.conn)
            st.dataframe(result)
        except Exception as e:
            st.error(f"❌ Error executing query: {e}")
    else:
        st.error("❗ Please connect to the database first.")

# --- List Tables ---
if st.button("List Tables"):
    if 'conn' in st.session_state:
        try:
            query_result = pd.read_sql_query("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'", con=st.session_state.conn)
            st.write("📋 Tables in Database:")
            st.dataframe(query_result)
        except Exception as e:
            st.error(f"❌ Error listing tables: {e}")

# --- Basic Visualization ---
if 'conn' in st.session_state:
    try:
        tables = pd.read_sql_query("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'", con=st.session_state.conn)
        table_list = tables['TABLE_NAME'].tolist()

        selected_table = st.selectbox("📊 Select a table to visualize", table_list)
        if selected_table:
            data = pd.read_sql_query(f"SELECT * FROM {selected_table}", con=st.session_state.conn)

            x_col = st.selectbox("X-axis column", data.columns)
            y_col = st.selectbox("Y-axis column", data.columns)
            chart_type = st.selectbox("Chart Type", ['Bar Chart', 'Scatter Chart', 'Histogram'])

            if st.button("Generate Chart"):
                if chart_type == 'Bar Chart':
                    st.bar_chart(data[[x_col, y_col]])
                elif chart_type == 'Scatter Chart':
                    st.write(data.plot.scatter(x=x_col, y=y_col))
                    st.pyplot()
                elif chart_type == 'Histogram':
                    st.write(data[y_col].plot.hist())
                    st.pyplot()
    except Exception as e:
        st.error(f"Error loading data for visualization: {e}")