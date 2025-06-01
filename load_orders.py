import streamlit as st
import pandas as pd
from sqlalchemy import text
from datetime import datetime

def load_orders(engine, status=None, start_date=None, end_date=None):
    base_query = """
    SELECT o.OrderID, o.OrderDate, o.Status as OrderStatus, c.Name as Customer, 
           od.ProductID, p.Name as ProductName, od.Quantity, 
           s.ShipmentID, s.ShipDate, s.DeliveryDate, s.Status as ShipmentStatus, s.Notes as ShipmentNotes
    FROM Orders o
    JOIN Customers c ON o.CustomerID = c.CustomerID
    JOIN OrderDetails od ON o.OrderID = od.OrderID
    JOIN Products p ON od.ProductID = p.ProductID
    LEFT JOIN Shipments s ON o.OrderID = s.OrderID
    WHERE 1=1
    """

    filters = []
    params = {}

    if status:
        filters.append("o.Status = :status")
        params['status'] = status
    if start_date:
        filters.append("o.OrderDate >= :start_date")
        params['start_date'] = start_date
    if end_date:
        filters.append("o.OrderDate <= :end_date")
        params['end_date'] = end_date
    
    if filters:
        base_query += " AND " + " AND ".join(filters)

    base_query += " ORDER BY o.OrderDate DESC"

    df = pd.read_sql(text(base_query), engine, params=params)
    return df

def update_order_status(engine, order_id, new_status):
    with engine.begin() as conn:
        conn.execute(text("UPDATE Orders SET Status = :status WHERE OrderID = :order_id"), 
                     {"status": new_status, "order_id": order_id})

def update_shipment_status(engine, shipment_id, new_status, notes):
    with engine.begin() as conn:
        conn.execute(text("""
            UPDATE Shipments 
            SET Status = :status, Notes = :notes 
            WHERE ShipmentID = :shipment_id
        """), {"status": new_status, "notes": notes, "shipment_id": shipment_id})

# --- UI Starts Here ---
st.header("📦 Detailed Order and Shipment Tracking")

engine = st.session_state.get('engine')
if not engine:
    st.warning("Connect to database first!")
    st.stop()

# Filters
status_filter = st.selectbox("Filter Orders by Status", ["All", "Pending", "Processing", "Shipped", "Delivered", "Cancelled"])
start_date = st.date_input("Start Date", value=None)
end_date = st.date_input("End Date", value=None)

status_filter_val = None if status_filter == "All" else status_filter
start_date_val = start_date if start_date != datetime(1900,1,1).date() else None
end_date_val = end_date if end_date != datetime(1900,1,1).date() else None

orders_df = load_orders(engine, status=status_filter_val, start_date=start_date_val, end_date=end_date_val)

if orders_df.empty:
    st.info("No orders found with the given filters.")
else:
    # Display grouped orders with expandable detail
    grouped = orders_df.groupby(['OrderID', 'OrderDate', 'OrderStatus', 'Customer'])

    for (order_id, order_date, order_status, customer), group in grouped:
        with st.expander(f"Order #{order_id} | Date: {order_date} | Status: {order_status} | Customer: {customer}"):
            st.write("### Products in this order:")
            prod_df = group[['ProductID', 'ProductName', 'Quantity']].drop_duplicates()
            st.table(prod_df)

            # Update order status
            new_order_status = st.selectbox(f"Update Order #{order_id} Status", 
                                            options=["Pending", "Processing", "Shipped", "Delivered", "Cancelled"],
                                            index=["Pending", "Processing", "Shipped", "Delivered", "Cancelled"].index(order_status),
                                            key=f"order_status_{order_id}")
            if new_order_status != order_status:
                if st.button(f"Update Order #{order_id} Status", key=f"update_order_{order_id}"):
                    try:
                        update_order_status(engine, order_id, new_order_status)
                        st.success(f"Order #{order_id} status updated to {new_order_status}")
                    except Exception as e:
                        st.error(f"Error updating order status: {e}")

            # Shipment details
            shipment = group[['ShipmentID', 'ShipDate', 'DeliveryDate', 'ShipmentStatus', 'ShipmentNotes']].dropna(subset=['ShipmentID'])
            if not shipment.empty:
                st.write("### Shipment details:")
                for idx, row in shipment.iterrows():
                    st.write(f"Shipment ID: {row['ShipmentID']}")
                    st.write(f"Ship Date: {row['ShipDate']}")
                    st.write(f"Delivery Date: {row['DeliveryDate']}")
                    st.write(f"Current Status: {row['ShipmentStatus']}")
                    notes = row['ShipmentNotes'] if row['ShipmentNotes'] else ""

                    new_ship_status = st.selectbox(f"Update Shipment Status (Shipment ID {row['ShipmentID']})", 
                                                  options=["Processing", "Shipped", "Delivered"], 
                                                  index=["Processing", "Shipped", "Delivered"].index(row['ShipmentStatus']),
                                                  key=f"ship_status_{row['ShipmentID']}")

                    new_notes = st.text_area(f"Shipment Notes (Shipment ID {row['ShipmentID']})", value=notes, key=f"ship_notes_{row['ShipmentID']}")

                    if (new_ship_status != row['ShipmentStatus']) or (new_notes != notes):
                        if st.button(f"Update Shipment ID {row['ShipmentID']}", key=f"update_ship_{row['ShipmentID']}"):
                            try:
                                update_shipment_status(engine, row['ShipmentID'], new_ship_status, new_notes)
                                st.success(f"Shipment ID {row['ShipmentID']} updated!")
                            except Exception as e:
                                st.error(f"Failed to update shipment: {e}")
            else:
                st.info("No shipment info available for this order.")
