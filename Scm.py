import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd

# Create DB connection
def create_connection(server, database):
    conn_str = f"mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    engine = create_engine(conn_str)
    return engine

st.title("📦 Supply Chain Management System")

server = st.text_input("SQL Server", "localhost")
database = st.text_input("Database Name", "SCM_DB")

if st.button("Connect to Database"):
    try:
        engine = create_connection(server, database)
        st.success("Connected to DB!")
        st.session_state.engine = engine
    except Exception as e:
        st.error(f"Connection error: {e}")

if 'engine' in st.session_state:
    engine = st.session_state.engine
    
    menu = st.sidebar.selectbox("Menu", ["View Products", "Add Product", "View Customers", "Add Customer", "Create Order", "Inventory Dashboard"])

    if menu == "View Products":
        df = pd.read_sql("SELECT * FROM Products", engine)
        st.write(df)

    elif menu == "Add Product":
        name = st.text_input("Product Name")
        category = st.text_input("Category")
        qty = st.number_input("Quantity", min_value=0)

        if st.button("Add Product"):
            query = text("INSERT INTO Products (Name, Category, Quantity) VALUES (:name, :category, :qty)")
            try:
                with engine.begin() as conn:
                    conn.execute(query, {"name": name, "category": category, "qty": qty})
                st.success("Product added successfully!")
            except Exception as e:
                st.error(f"Failed to add product: {e}")

    elif menu == "View Customers":
        df = pd.read_sql("SELECT * FROM Customers", engine)
        st.write(df)

    elif menu == "Add Customer":
        name = st.text_input("Customer Name")
        contact = st.text_input("Contact Info")

        if st.button("Add Customer"):
            query = text("INSERT INTO Customers (Name, Contact) VALUES (:name, :contact)")
            try:
                with engine.begin() as conn:
                    conn.execute(query, {"name": name, "contact": contact})
                st.success("Customer added successfully!")
            except Exception as e:
                st.error(f"Failed to add customer: {e}")

    elif menu == "Create Order":
        customer_id = st.number_input("Customer ID", min_value=1)
        product_id = st.number_input("Product ID", min_value=1)
        order_qty = st.number_input("Order Quantity", min_value=1)

        if st.button("Place Order"):
            try:
                with engine.begin() as conn:
                    # Insert order
                    order_res = conn.execute(text("INSERT INTO Orders (CustomerID) VALUES (:cust_id); SELECT SCOPE_IDENTITY()"), {"cust_id": customer_id})
                    order_id = order_res.scalar()  # Get last inserted OrderID
                    
                    # Insert order details
                    conn.execute(text("INSERT INTO OrderDetails (OrderID, ProductID, Quantity) VALUES (:order_id, :prod_id, :qty)"),
                                 {"order_id": order_id, "prod_id": product_id, "qty": order_qty})

                    # Update Product Quantity
                    conn.execute(text("UPDATE Products SET Quantity = Quantity - :qty WHERE ProductID = :prod_id"),
                                 {"qty": order_qty, "prod_id": product_id})

                st.success(f"Order #{order_id} placed successfully!")

            except Exception as e:
                st.error(f"Failed to place order: {e}")

    elif menu == "Inventory Dashboard":
        df = pd.read_sql("SELECT ProductID, Name, Category, Quantity FROM Products", engine)
        st.write("### Current Inventory Levels")
        st.dataframe(df)
        low_stock = df[df['Quantity'] < 10]
        if not low_stock.empty:
            st.warning("⚠️ Low stock alert for following products:")
            st.write(low_stock)

