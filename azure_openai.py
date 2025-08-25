# azure_openai.py
import requests

# Azure OpenAI details
AZURE_OPENAI_ENDPOINT = "https://mymaai-rmeq147sa-eastus2.services.ai.azure.com"
AZURE_OPENAI_KEY = "YOUR_KEY_HERE"
DEPLOYMENT_NAME = "gpt-35-turbo"

# Mapping of common airline codes to full names
AIRLINE_CODES = {
    "UA": "United Airlines",
    "DL": "Delta Airlines",
    "AA": "American Airlines",
    "SW": "Southwest Airlines",
    "JB": "JetBlue"
}

def nlp_to_sql(user_query: str) -> str:
    """
    Send natural language query to Azure OpenAI and get SQL query back.
    """

    # Replace airline codes in user input with full names
    for code, full_name in AIRLINE_CODES.items():
        if f" {code} " in f" {user_query} " or user_query.startswith(code):
            user_query = user_query.replace(code, full_name)

    system_prompt = """
    You are an assistant that converts natural language queries into SQL queries
    for a PostgreSQL database in an airline system.

    Database Schema:
    - flight_details(flight_id, airline, flight_number, origin, destination, departure_time, arrival_time, status, gate, seat_capacity)
    - passenger_details(passenger_id, name, email, phone, flight_id, seat_number, booking_status)

    Rules:
    - Only generate SQL, no explanation text.
    - Always output valid SQL for PostgreSQL.
    - Always use exact airline names as stored in the database:
      'United Airlines', 'Delta Airlines', 'American Airlines', 'Southwest Airlines', 'JetBlue'.
    - Use the correct flight_number format as stored in the database, e.g., 'UA123', 'AA789'.
    - Make queries case-insensitive for string matches using ILIKE.
    """

    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version=2024-02-15-preview"

    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_KEY,
    }

    body = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        "temperature": 0,
        "max_tokens": 250
    }

    try:
        response = requests.post(url, headers=headers, json=body, timeout=30)
        response.raise_for_status()
        result = response.json()

        # Validate the response
        choices = result.get("choices")
        if not choices or "message" not in choices[0] or "content" not in choices[0]["message"]:
            raise ValueError("Azure OpenAI did not return a valid SQL response.")

        sql_code = choices[0]["message"]["content"].strip()
        return sql_code

    except requests.exceptions.Timeout:
        raise Exception("The AI server took too long to respond. Please try again.")
    except requests.exceptions.ConnectionError:
        raise Exception("Cannot connect to the AI server. Check your internet or endpoint.")
    except Exception as e:
        raise Exception(f"Received an unexpected response from the AI. Details: {e}")