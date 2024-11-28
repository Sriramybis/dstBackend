---

### Backend (FastAPI) `README.md`

```md
# Backend - Dataset Search API

This is the backend for the Dataset Search Application, built using FastAPI. It processes search queries from the frontend and returns dataset information.

## Technologies Used
- Python 3.7+
- FastAPI
- Pydantic
- Uvicorn (ASGI server)
- CORS Middleware

## Prerequisites

Before running this project, ensure you have the following installed:

- [Python](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/) (Python package installer)

## Getting Started

Follow the steps below to get the backend API up and running.

### 1. Clone the Repository

```bash
git clone https://github.com/iamevs/Dataset-searcher.git
cd Dataset-searcher/server
```
### 2. Create and Activate Virtual Environment (Optional)
It is recommended to create a virtual environment to manage dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Start the Backend Server

Use Uvicorn to run the FastAPI application:

```bash
uvicorn main:app --reload
```

This will start the backend server at `http://localhost:8000`.

### 5. CORS Configuration

The backend includes CORS middleware to allow requests from the frontend:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 6. API Endpoints

`POST /search`
This endpoint accepts a search query and returns dataset results.

- Request Body:

```json
{
  "query": "your search term"
}
```
- Response:

```json
{
  "results": [
    {
      "Dataset Category": "Example Category",
      "Vendor": "Example Vendor",
      "Dataset Name": "Example Dataset",
      "Description": "Example Description",
      "Therapeutic coverage": "Example Therapeutic Coverage",
      "Geographic coverage": "Example Geographic Coverage"
    }
  ]
}
```

### 7. Project Structure

```bash
├── main.py             # Main FastAPI application
├── requirements.txt    # Dependencies
└── .env                # Environment variables (optional)
```

### 8. Testing the API
You can use a tool like Postman or curl to test the API:

```bash
curl -X POST http://localhost:8000/search -H "Content-Type: application/json" -d '{"query": "example"}'
```

### 9. Environment Variables

You can define environment variables in a .env file to configure the API (e.g., database URLs, API keys).

### 10. Deployment

You can deploy this API to services like Heroku, AWS, or any cloud platform that supports Python and ASGI applications.

