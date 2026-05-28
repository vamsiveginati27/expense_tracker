# Expense Tracker API

Simple REST API for expense tracking with JWT authentication.

## Setup

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
uv add flask gunicorn python-dotenv flask-jwt-extended flask-restful

# Run development server
python app.py
```

Server runs on `http://localhost:5000`

## API Endpoints

### Authentication

**Login** - Get access token
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "user1",
  "password": "password123"
}
```

Response:
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": "user1"
}
```

### Expenses

All expense endpoints require `Authorization: Bearer <token>` header.

**Get All Expenses**
```bash
GET /api/expenses
Authorization: Bearer <token>
```

**Create Expense**
```bash
POST /api/expenses
Authorization: Bearer <token>
Content-Type: application/json

{
  "description": "Lunch",
  "amount": 15.50,
  "category": "Food"
}
```

**Get Single Expense**
```bash
GET /api/expenses/<id>
Authorization: Bearer <token>
```

**Update Expense**
```bash
PUT /api/expenses/<id>
Authorization: Bearer <token>
Content-Type: application/json

{
  "description": "Dinner",
  "amount": 25.00,
  "category": "Food"
}
```

**Delete Expense**
```bash
DELETE /api/expenses/<id>
Authorization: Bearer <token>
```

**Get Summary by Category**
```bash
GET /api/expenses/summary
Authorization: Bearer <token>
```

### Health Check

```bash
GET /api/health
```

## Testing with cURL

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"password123"}' | jq -r '.access_token')

# 2. Create expense
curl -X POST http://localhost:5000/api/expenses \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description":"Lunch","amount":12.99,"category":"Food"}'

# 3. Get all expenses
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/expenses

# 4. Get summary
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/expenses/summary
```

## Default Test Credentials

- Username: `user1`
- Password: `password123`

## Project Structure

```
expense_tracker/
├── app.py              # Main Flask app with all endpoints
├── .env                # Environment variables (development)
├── .env.example        # Environment template
├── venv/               # Virtual environment
└── README.md           # This file
```

## Production Deployment

### Using Gunicorn

```bash
uv add gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Using Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install uv && uv pip install --system flask gunicorn python-dotenv flask-jwt-extended flask-restful

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

Build and run:
```bash
docker build -t expense-api .
docker run -p 8000:8000 expense-api
```

## Next Steps

- Replace in-memory storage with a real database (SQLAlchemy, SQLite, PostgreSQL)
- Add proper password hashing (werkzeug.security)
- Implement user registration endpoint
- Add input validation and error messages
- Add request logging and monitoring
- Write unit tests
