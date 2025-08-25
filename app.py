# app.py
import streamlit as st
from azure_openai import nlp_to_sql
from sqlalchemy import create_engine
import requests
import psycopg2
import pandas as pd

# -------------------------------
# PostgreSQL connection details
# -------------------------------
DB_HOST = "localhost"   # e.g., localhost or AWS RDS endpoint
DB_NAME = "airlinesdb"
DB_USER = "prashanthsapple"
DB_PASS = ""
DB_PORT = "5432"  # default PostgreSQL port

def run_sql_query(sql: str):
    """Run SQL query on PostgreSQL and return results as DataFrame."""
    try:
        engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        df = pd.read_sql(sql, engine)
        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        print("DEBUG: Database error:", e)
        return None

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="✈️ Airline Chatbot", layout="centered")
st.title("✈️ Airline Flight Status Chatbot")
st.markdown("Ask me about flights using **Flight number** or **PNR**.")

user_input = st.text_input("Your question (e.g., 'What is the status of flight UA123?'):")

if st.button("Ask") and user_input:
    with st.spinner("Processing your request..."):
        try:
            # Convert NLP → SQL using Azure OpenAI
            sql_query = nlp_to_sql(user_input)

            # Show generated SQL
            st.subheader("Generated SQL Query:")
            st.code(sql_query, language="sql")

            # Run SQL on PostgreSQL
            df = run_sql_query(sql_query)

            if df is not None and not df.empty:
                st.subheader("Results:")
                st.dataframe(df)
            else:
                st.info("No results found for your query.")

        except requests.exceptions.Timeout:
            st.error("The AI server took too long to respond. Please try again shortly.")
            print("DEBUG: Timeout occurred while contacting Azure OpenAI.")

        except requests.exceptions.ConnectionError:
            st.error("Cannot reach the AI server. Check your internet or Azure OpenAI endpoint.")
            print("DEBUG: Connection error to Azure OpenAI.")

        except requests.exceptions.HTTPError as http_err:
            st.error("The AI server returned an error. Please try again later.")
            print(f"DEBUG: HTTP error from Azure OpenAI: {http_err}")

        except ValueError as val_err:
            st.error("The AI returned an unexpected response. Try rephrasing your question.")
            print(f"DEBUG: ValueError: {val_err}")

        except Exception as e:
            st.error("Oops! Something went wrong. Please try again or contact support.")
            print(f"DEBUG: Unexpected error: {e}")