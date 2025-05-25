# RUMORS: Restful Utilities for Movies Online Recommender System

## Project Description
RUMORS is a comprehensive web service that implements RESTful APIs for an intelligent movie recommendation platform built on the MovieLens dataset. The system delivers tailored movie suggestions by analyzing user preferences and viewing patterns.

## Core Capabilities
- Intelligent movie recommendation engine with detailed explanations
- Comprehensive user rating and feedback management
- Modern RESTful API design
- Advanced movie search with multiple filters
- User profile management including OCEAN personality assessment
- Secure JWT authentication system

## Getting Started

### Prerequisites
- Python 3.8+
- pip package manager
- Docker (optional)

### Installation Steps

1. **Clone the project:**
   ```bash
   git clone https://github.com/bianccc01/rumors.git
   cd rumors
   ```

2. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the application:**
   ```bash
   python run.py
   ```

The server will start at `http://localhost:5000`.

### Alternative: Docker Deployment
For containerized deployment:
```bash
docker compose up -d
```

Access the application at `http://localhost:5000`.

## API Reference
Complete API documentation is accessible at `/api/docs` once the application is running.
Alternative documentation can be found in `static/swagger.json`.

## Sample API Calls

### Creating a User Account
```http
POST /api/users/ HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{
    "browser": "Firefox",
    "os": "macOS",
    "language": "en-GB"
}
```

Expected Response:
```json
{
    "user": {
        "test_group": "B",
        "browser": "Firefox",
        "os": "macOS",
        "language": "en-GB"
    },
    "token": "<JWT_ACCESS_TOKEN>"
}
```

### Retrieving User Recommendations
```http
GET /api/users/456/recommendations/ HTTP/1.1
Host: localhost:5000
Authorization: Bearer <JWT_ACCESS_TOKEN>
```

Response Format:
```json
[
    {
        "item_id": "tt0137523",
        "pred_score": 4.7,
        "is_known": false,
        "timestamp": "2024-01-05T14:45:00Z"
    },
    {
        "item_id": "tt0110912",
        "pred_score": 4.4,
        "is_known": false,
        "timestamp": "2024-01-05T14:45:00Z"
    }
]
```

### Movie Search with Parameters
```http
GET /api/items/?query=batman&sort=rating&limit=3 HTTP/1.1
Host: localhost:5000
Authorization: Bearer <JWT_ACCESS_TOKEN>
```

Response Example:
```json
[
    {
        "title": "The Dark Knight",
        "genres": ["Action", "Crime", "Drama"],
        "imdb_id": "tt0468569",
        "tmdb_id": "155"
    },
    {
        "title": "Batman Begins",
        "genres": ["Action", "Crime"],
        "imdb_id": "tt0372784",
        "tmdb_id": "272"
    }
]
```

## Primary API Routes
- `/api/users/`: Complete user account operations
- `/api/users/{id}/recommendations/`: Personalized movie suggestions
- `/api/users/{id}/ocean`: Personality trait analysis
- `/api/items/`: Movie catalog search and exploration
- `/api/recommendations/{id}/explain`: Detailed recommendation rationale

## Security & Authentication
The system employs JWT tokens for secure authentication. Include your token in requests:
```
Authorization: Bearer <your_access_token>
```

## HTTP Response Codes
Standard status codes used throughout the API:
- **200**: Request successful
- **201**: New resource created successfully
- **400**: Invalid request parameters
- **401**: Authentication required
- **403**: Access denied
- **404**: Requested resource not found
- **500**: Server error occurred

## Technology Stack
- **Backend**: Python Flask
- **Authentication**: JSON Web Tokens
- **Dataset**: MovieLens
- **Documentation**: Swagger/OpenAPI
- **Containerization**: Docker
