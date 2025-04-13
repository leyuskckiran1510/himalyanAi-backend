# Flask API Documentation

Welcome to the documentation for the Flask API! This API provides endpoints for user authentication, content summarization, and user history management. Below you will find detailed information about each endpoint, including the expected input and output formats.

## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [Endpoints](#endpoints)
   - [Authenticate or Identify](#authenticate-or-identify)
   - [Summarize Content](#summarize-content)
   - [Discard Summary](#discard-summary)
   - [Fetch User History](#fetch-user-history)
   - [Summary of the Day](#summary-of-the-day)
   - [Database Health Check](#database-health-check)
4. [Models](#models)
5. [Error Handling](#error-handling)

## Installation

To set up the Flask API, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the environment variables:**
   Create a `.env` file in the root directory and add the following variables:
   ```env
   GOOGLE=<your_google_api_key>
   OPEN_ROUTER=<your_open_router_api_key>
   ```

4. **Initialize the database:**
   ```bash
   flask db init
   flask db migrate -m "Initial migration."
   flask db upgrade
   ```

5. **Run the application:**
   ```bash
   flask run
   ```

## Usage

The API is designed to be used with the following base URL:
```
http://localhost:5000/api
```

## Endpoints

### Authenticate or Identify

**Endpoint:** `/authenticate_or_identify`

**Method:** `POST`

**Description:** Authenticates or identifies a user based on the provided hash. If the user does not exist, a new user is created.

**Request Body:**
```json
{
  "hash": "user_hash"
}
```

**Response:**
```json
{
  "access_token": "jwt_token"
}
```

### Summarize Content

**Endpoint:** `/summarize`

**Method:** `POST`

**Description:** Summarizes the provided content and stores the summary in the IPFS.

**Request Body:**
```json
{
  "content": "text_to_summarize",
  "url": "site_domain",
  "full": "full_url"
}
```

**Response:**
```json
{
  "summary": "summary_text",
  "notes": ["note1", "note2"],
  "references": [
    {
      "name": "Source Title",
      "link": "URL"
    }
  ]
}
```

### Discard Summary

**Endpoint:** `/discard`

**Method:** `POST`

**Description:** Discards the summary history for a specific URL.

**Request Body:**
```json
{
  "of": "full_url"
}
```

**Response:**
```json
{
  "msg": "summary history discarded."
}
```

### Fetch User History

**Endpoint:** `/fetch_user_history`

**Method:** `GET`

**Description:** Fetches the user's summary history grouped by date and domain.

**Response:**
```json
{
  "2023-10-01": {
    "example.com": {
      "http://example.com/page1": {
        "summary": "summary_text",
        "notes": ["note1", "note2"],
        "references": [
          {
            "name": "Source Title",
            "link": "URL"
          }
        ]
      }
    }
  }
}
```

### Summary of the Day

**Endpoint:** `/summary_of_day`

**Method:** `GET`

**Description:** Provides a summary of all the summaries created by the user on the current day.

**Response:**
```json
{
  "date": "2023-10-01",
  "summary": "combined_summary_text"
}
```

### Database Health Check

**Endpoint:** `/db_health`

**Method:** `GET`

**Description:** Checks the health of the database and returns the status along with user and summary counts.

**Response:**
```json
{
  "status": "healthy",
  "user_count": 10,
  "summary_count": 50,
  "database_uri": "sqlite"
}
```

## Models

### User

**Attributes:**
- `id`: Integer, primary key
- `anon_hash`: String, unique identifier for the user

### SummaryDb

**Attributes:**
- `id`: Integer, primary key
- `user_id`: Integer, foreign key referencing `User.id`
- `summary_id`: String, IPFS hash of the summary
- `full_url`: String, full URL of the summarized content
- `site_domain`: String, domain of the summarized content
- `created_at`: DateTime, timestamp of when the summary was created

## Error Handling

The API returns standard HTTP status codes and error messages in the response body. Common status codes include:

- `200 OK`: The request was successful.
- `400 Bad Request`: The request was invalid or missing required parameters.
- `404 Not Found`: The requested resource was not found.
- `500 Internal Server Error`: An error occurred on the server.

Error responses are typically in the following format:
```json
{
  "error": "error_message"
}
```

---

This documentation provides a comprehensive overview of the Flask API, including installation instructions, usage examples, and detailed information about each endpoint. If you have any questions or need further assistance, please feel free to reach out.

Happy coding! 🚀