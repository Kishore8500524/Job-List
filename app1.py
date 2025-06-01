import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import plotly.express as px

# ------------------- Database Connection -------------------
def create_connection(server, database):
    connection_string = f"mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    engine = create_engine(connection_string)
    return engine

# ------------------- Streamlit UI -------------------
st.title("📦 Supply Chain Management System")

server = st.text_input('Server')
database = st.text_input('Database')

if st.button('Connect to Database'):
    try:
        engine = create_connection(server, database)
        st.session_state.engine = engine
        st.success("Connected to Database ✅")
    except Exception as e:
        st.error(f"Connection failed ❌: {e}")

# ------------------- Product & Inventory -------------------
st.header("🧾 Product Management")

if 'engine' in st.session_state:
    with st.expander("➕ Add New Product"):
        name = st.text_input("Product Name")
        category = st.text_input("Category")
        quantity = st.number_input("Quantity", min_value=0, value=0)

        if st.button("Add Product"):
            query = f"""
                INSERT INTO Products (Name, Category, Quantity)
                VALUES ('{name}', '{category}', {quantity})
            """
            with st.session_state.engine.begin() as conn:
                conn.execute(query)
            st.success("Product added successfully!")

    st.subheader("📋 Product Inventory")
    df_products = pd.read_sql("SELECT * FROM Products", st.session_state.engine)
    st.dataframe(df_products)

# ------------------- Customer & Order -------------------
st.header("📑 Customer Orders")

if 'engine' in st.session_state:
    with st.expander("➕ New Customer Order"):
        customer_name = st.text_input("Customer Name")
        contact = st.text_input("Contact")
        product_id = st.number_input("Product ID", min_value=1)
        order_quantity = st.number_input("Quantity", min_value=1)

        if st.button("Place Order"):
            with st.session_state.engine.begin() as conn:
                conn.execute(f"INSERT INTO Customers (Name, Contact) VALUES ('{customer_name}', '{contact}')")
                customer_id = pd.read_sql("SELECT MAX(CustomerID) AS id FROM Customers", conn).iloc[0]['id']
                conn.execute(f"INSERT INTO Orders (CustomerID) VALUES ({customer_id})")
                order_id = pd.read_sql("SELECT MAX(OrderID) AS id FROM Orders", conn).iloc[0]['id']
                conn.execute(f"INSERT INTO OrderDetails (OrderID, ProductID, Quantity) VALUES ({order_id}, {product_id}, {order_quantity})")
            st.success("Order placed successfully!")

    st.subheader("📦 Orders List")
    df_orders = pd.read_sql("""
        SELECT o.OrderID, c.Name AS Customer, o.OrderDate, p.Name AS Product, d.Quantity
        FROM Orders o
        JOIN Customers c ON o.CustomerID = c.CustomerID
        JOIN OrderDetails d ON o.OrderID = d.OrderID
        JOIN Products p ON d.ProductID = p.ProductID
    """, st.session_state.engine)
    st.dataframe(df_orders)

# ------------------- Shipment Tracking -------------------
st.header("🚚 Shipment Tracking")

if 'engine' in st.session_state:
    with st.expander("📤 Add Shipment Info"):
        order_id = st.number_input("Order ID", min_value=1)
        ship_date = st.date_input("Ship Date")
        delivery_date = st.date_input("Delivery Date")
        status = st.selectbox("Status", ["Processing", "Shipped", "Delivered"])

        if st.button("Add Shipment"):
            with st.session_state.engine.begin() as conn:
                conn.execute(f"""
                    INSERT INTO Shipments (OrderID, ShipDate, DeliveryDate, Status)
                    VALUES ({order_id}, '{ship_date}', '{delivery_date}', '{status}')
                """)
            st.success("Shipment added successfully")

    st.subheader("📍 Shipment Status")
    df_ship = pd.read_sql("SELECT * FROM Shipments", st.session_state.engine)
    st.dataframe(df_ship)
	with st.expander("Manage Suppliers"):
    supplier_name = st.text_input("Supplier Name")
    contact_info = st.text_input("Contact Info")
    if st.button("Add Supplier"):
        # Add supplier to DB
        st.success("Supplier added successfully!")
	
	
	
	

# ------------------- Visualizations -------------------
st.header("📊 Analytics")

if 'engine' in st.session_state:
    df_chart = pd.read_sql("SELECT Category, SUM(Quantity) AS Total FROM Products GROUP BY Category", st.session_state.engine)

    fig, ax = plt.subplots()
    ax.bar(df_chart['Category'], df_chart['Total'])
    ax.set_xlabel("Category")
    ax.set_ylabel("Total Quantity")
    ax.set_title("Inventory by Category")
    st.pyplot(fig)
else:
    st.warning("⚠️ Connect to the database to view data.")
	

    if st.checkbox("View Suppliers"):
        # Fetch and display suppliers
        st.write(pd.read_sql("SELECT * FROM Suppliers", conn))
		
    # Bar chart: Product inventory levels
     df = pd.read_sql("SELECT Name, Quantity FROM Products", conn)
     fig = px.bar(df, x="Name", y="Quantity", title="Product Inventory")
     st.plotly_chart(fig)

if "authenticated" not in st.session_state:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login") and username == "admin" and password == "admin123":
        st.session_state.authenticated = True
    else:
        st.warning("Incorrect credentials.")
        st.stop()
