# Agentic Financial Assistant

This is a simple text-based AI assistant for the financial sector, built with LangGraph and FastAPI.

## Setup

1.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Set up your environment variables:**

    Create a `.env` file in the root of the project and add your OpenAI API key:

    ```
    OPENAI_API_KEY="your_openai_api_key_here"
    ```

## Running the Application

1.  **Start the FastAPI server:**

    ```bash
    uvicorn app.main:app --reload
    ```

2.  **Send a query:**

    You can use `curl` to send a POST request to the `/query/` endpoint:

    ```bash
    curl -X POST "http://127.0.0.1:8000/query/" -H "Content-Type: application/json" -d '{"text": "What is the current stock price of AAPL?"}'
    ```

    **Blocked query:**

    ```bash
    curl -X POST "http://127.0.0.1:8000/query/" -H "Content-Type: application/json" -d '{"text": "I want to transfer funds"}'
    ```
