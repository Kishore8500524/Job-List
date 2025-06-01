import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.title("📈 Stock Market Analysis")

ticker = st.text_input("Enter Stock Ticker", value="AAPL")
start_date = st.date_input("Start Date", pd.to_datetime("2022-01-01"))
end_date = st.date_input("End Date", pd.to_datetime("today"))

if st.button("Fetch Data"):
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        st.subheader(f"Data for {ticker}")
        st.write(data.head())

        st.subheader("Closing Price Chart")
        st.line_chart(data['Close'])

        st.subheader("Moving Average (20 days)")
        data['MA20'] = data['Close'].rolling(window=20).mean()
        st.line_chart(data[['Close', 'MA20']])

        st.subheader("Volume Traded")
        st.bar_chart(data['Volume'])

    except Exception as e:
        st.error(f"Error fetching data: {e}")