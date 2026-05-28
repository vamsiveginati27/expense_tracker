# Expense Tracker API

Production-ready REST API for expense tracking with JWT authentication and MongoDB.

**Features:**
- User authentication with JWT tokens
- Password hashing with werkzeug
- MongoDB document models with mongoengine
- RESTful API with Flask-RESTful
- Modular blueprint architecture
- Request validation and error handling

## Prerequisites

- Python 3.8+
- MongoDB running locally or remote
- pip/uv for package management

## Setup

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
# OR with uv
uv pip install -r requirements.txt

# Create .env file from template
cp .env.example .env

# Run development server
python app.py
```

**Server runs on:** `http://localhost:5002`

## MongoDB Setup

### Local MongoDB

```bash
# Using Homebrew (macOS)
brew install mongodb-community
brew services start mongodb-community

# Or with Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### Remote MongoDB (Atlas)

Update `.env`:
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/expense_tracker?retryWrites=true&w=majority
```

## API Endpoints

### Authentication

**Register** - Create new user
```bash
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password",
  "email": "john@example.com"
}
```

Response (201):
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2024-05-24T10:30:00"
  }
}
```

**Login** - Get access token
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password"
}
```

Response (200):
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2024-05-24T10:30:00"
  }
}
```

### Expenses

All expense endpoints require `Authorization: Bearer <token>` header.

**Get All Expenses**
```bash
GET /api/expenses?skip=0&limit=100&category=Food
Authorization: Bearer <token>
```

Response (200):
```json
{
  "expenses": [
    {
      "id": "507f1f77bcf86cd799439012",
      "user": "507f1f77bcf86cd799439011",
      "description": "Lunch at restaurant",
      "amount": 25.50,
      "category": "Food",
      "date": "2024-05-24T12:30:00",
      "created_at": "2024-05-24T12:31:00"
    }
  ],
  "count": 1,
  "total": 1
}
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

Response (201): Returns created expense document

**Get Single Expense**
```bash
GET /api/expenses/507f1f77bcf86cd799439012
Authorization: Bearer <token>
```

**Update Expense**
```bash
PUT /api/expenses/507f1f77bcf86cd799439012
Authorization: Bearer <token>
Content-Type: application/json

{
  "description": "Dinner",
  "amount": 25.00,
  "category": "Dining"
}
```

**Delete Expense**
```bash
DELETE /api/expenses/507f1f77bcf86cd799439012
Authorization: Bearer <token>
```

**Get Summary by Category**
```bash
GET /api/expenses/summary
Authorization: Bearer <token>
```

Response (200):
```json
{
  "summary": {
    "Food": 125.50,
    "Transport": 45.00,
    "Entertainment": 30.00
  },
  "total": 200.50,
  "count": 10
}
```

### Health Check

```bash
GET /api/health
```

Response (200):
```json
{
  "status": "healthy",
  "timestamp": "2024-05-24T10:30:00"
}
```

## Testing with cURL

```bash
# 1. Register user
curl -X POST http://localhost:5002/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "password": "test_pass123",
    "email": "test@example.com"
  }'

# 2. Login and save token
TOKEN=$(curl -s -X POST http://localhost:5002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test_user","password":"test_pass123"}' | jq -r '.access_token')

echo "Token: $TOKEN"

# 3. Create expense
curl -X POST http://localhost:5002/api/expenses \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Coffee",
    "amount": 5.50,
    "category": "Food"
  }'

# 4. Get all expenses
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5002/api/expenses

# 5. Get summary
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5002/api/expenses/summary
```

## Project Structure

```
expense_tracker/
├── app.py                          # Entry point
├── config.py                       # Configuration
├── requirements.txt                # Dependencies
├── .env                            # Environment variables
├── .env.example                    # Environment template
├── app/
│   ├── __init__.py                 # App factory
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                 # User document model
│   │   └── expense.py              # Expense document model
│   └── routes/
│       ├── __init__.py
│       ├── auth.py                 # Auth blueprint (register, login)
│       └── expenses.py             # Expenses blueprint (CRUD, summary)
└── tests/
    └── test_api.py                 # Unit tests
```

## MongoDB Documents

### User Document
```javascript
{
  _id: ObjectId,
  username: String (unique),
  password_hash: String,
  email: String,
  created_at: DateTime
}
```

### Expense Document
```javascript
{
  _id: ObjectId,
  user: Reference<User>,
  description: String,
  amount: Float,
  category: String,
  date: DateTime,
  created_at: DateTime
}
```

## Production Deployment

### Using Gunicorn

```bash
gunicorn -c gunicorn_config.py app:app
```

### Using Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

Build and run:
```bash
docker build -t expense-api .
docker run -p 8000:8000 \
  -e MONGODB_URI="mongodb://host.docker.internal:27017/expense_tracker" \
  expense-api
```

## Development

### Run Tests
```bash
pytest tests/ -v
```

### Install Dev Dependencies
```bash
pip install pytest pytest-flask
```

## Next Steps

- Add user profile endpoints
- Implement expense filters and sorting
- Add recurring expense support
- Implement expense budget tracking
- Add data export (CSV, PDF)
- Add multi-currency support
