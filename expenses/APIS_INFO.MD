1. Register

curl --location 'http://localhost:5002/api/auth/register' \
--header 'Content-Type: application/json' \
--data-raw '{"username":"vamsi_veginati","password":"test123","email":"test@test.com"}'

2. Login

curl --location 'http://localhost:5002/api/auth/login' \
--header 'Content-Type: application/json' \
--data '{
    "username": "vamsi_veginati",
    "password": "test123"
  }'

3. Get users

curl --location 'http://localhost:5002/api/users' \
--header 'Authorization: Bearer ' \
--header 'Content-Type: application/json'

4. Get expenses

curl --location 'http://localhost:5002/api/expenses' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer '

5. Post Expenses

curl --location 'http://localhost:5002/api/expenses' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer ' \
--data '{
    "description": "Haircut",
    "amount": 65.99,
    "category": "miscellaneous"
}'

