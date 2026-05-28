#!/bin/bash

# Expense Tracker API Testing Script
# Run: bash test.sh

set -e

API_URL="http://localhost:5002"
USERNAME="testuser_$(date +%s)"
PASSWORD="test123456"
EMAIL="test_$(date +%s)@example.com"

echo "=========================================="
echo "Expense Tracker API - Testing Script"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ==================== Health Check ====================
echo -e "${BLUE}1. Health Check${NC}"
curl -s "$API_URL/api/health" | jq
echo ""

# ==================== Register ====================
echo -e "${BLUE}2. Register User${NC}"
echo "Username: $USERNAME"
echo "Email: $EMAIL"
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$USERNAME\",
    \"password\": \"$PASSWORD\",
    \"email\": \"$EMAIL\"
  }")
echo "$REGISTER_RESPONSE" | jq
USER_ID=$(echo "$REGISTER_RESPONSE" | jq -r '.user.id')
echo ""

# ==================== Login ====================
echo -e "${BLUE}3. Login User${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$USERNAME\",
    \"password\": \"$PASSWORD\"
  }")
echo "$LOGIN_RESPONSE" | jq
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
echo "Token: $TOKEN"
echo ""

# ==================== Create Expenses ====================
echo -e "${BLUE}4. Create Expenses${NC}"

echo "Creating Expense 1: Lunch (Food)"
EXP1=$(curl -s -X POST "$API_URL/api/expenses" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Lunch at restaurant",
    "amount": 25.50,
    "category": "Food"
  }' | jq -r '.id')
echo "Expense ID: $EXP1"
echo ""

echo "Creating Expense 2: Uber (Transport)"
EXP2=$(curl -s -X POST "$API_URL/api/expenses" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Uber ride to office",
    "amount": 15.00,
    "category": "Transport"
  }' | jq -r '.id')
echo "Expense ID: $EXP2"
echo ""

echo "Creating Expense 3: Movie (Entertainment)"
EXP3=$(curl -s -X POST "$API_URL/api/expenses" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Movie tickets",
    "amount": 30.00,
    "category": "Entertainment"
  }' | jq -r '.id')
echo "Expense ID: $EXP3"
echo ""

# ==================== Get All Expenses ====================
echo -e "${BLUE}5. Get All Expenses${NC}"
curl -s -H "Authorization: Bearer $TOKEN" \
  "$API_URL/api/expenses" | jq
echo ""

# ==================== Get Single Expense ====================
echo -e "${BLUE}6. Get Single Expense (ID: $EXP1)${NC}"
curl -s -H "Authorization: Bearer $TOKEN" \
  "$API_URL/api/expenses/$EXP1" | jq
echo ""

# ==================== Get Expenses by Category ====================
echo -e "${BLUE}7. Get Expenses by Category (Food)${NC}"
curl -s -H "Authorization: Bearer $TOKEN" \
  "$API_URL/api/expenses?category=Food" | jq
echo ""

# ==================== Update Expense ====================
echo -e "${BLUE}8. Update Expense (ID: $EXP1)${NC}"
echo "Updating description and amount..."
curl -s -X PUT "$API_URL/api/expenses/$EXP1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Expensive lunch at fancy restaurant",
    "amount": 45.75,
    "category": "Dining"
  }' | jq
echo ""

# ==================== Get Summary ====================
echo -e "${BLUE}9. Get Expense Summary by Category${NC}"
curl -s -H "Authorization: Bearer $TOKEN" \
  "$API_URL/api/expenses/summary" | jq
echo ""

# ==================== Delete Expense ====================
echo -e "${BLUE}10. Delete Expense (ID: $EXP2)${NC}"
curl -s -X DELETE "$API_URL/api/expenses/$EXP2" \
  -H "Authorization: Bearer $TOKEN" | jq
echo ""

# ==================== Get Summary After Delete ====================
echo -e "${BLUE}11. Get Summary After Delete${NC}"
curl -s -H "Authorization: Bearer $TOKEN" \
  "$API_URL/api/expenses/summary" | jq
echo ""

# ==================== Error Cases ====================
echo -e "${BLUE}12. Test Error Cases${NC}"

echo "a) Unauthorized request (no token):"
curl -s "$API_URL/api/expenses" | jq
echo ""

echo "b) Invalid token:"
curl -s -H "Authorization: Bearer invalid_token" \
  "$API_URL/api/expenses" | jq
echo ""

echo "c) Non-existent expense:"
curl -s -H "Authorization: Bearer $TOKEN" \
  "$API_URL/api/expenses/nonexistent_id" | jq
echo ""

echo "d) Duplicate registration (same username):"
curl -s -X POST "$API_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$USERNAME\",
    \"password\": \"$PASSWORD\",
    \"email\": \"another@example.com\"
  }" | jq
echo ""

# ==================== Summary ====================
echo -e "${GREEN}=========================================="
echo "Testing Complete!"
echo "==========================================${NC}"
echo ""
echo "Test Summary:"
echo "- Registered user: $USERNAME"
echo "- User ID: $USER_ID"
echo "- Created 3 expenses: $EXP1, $EXP2, $EXP3"
echo "- Updated expense: $EXP1"
echo "- Deleted expense: $EXP2"
echo ""
