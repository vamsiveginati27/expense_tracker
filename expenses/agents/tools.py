import requests

from config import settings


class ExpenseTools:
    def __init__(self, token: str):
        self.base_url = settings.expense_api_base_url
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def create_expense(self, description: str, amount: float, category: str) -> dict:
        url = f"{self.base_url}/expenses"
        data = {
            "description": description,
            "amount": amount,
            "category": category,
        }
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_expenses(self) -> list[dict]:
        url = f"{self.base_url}/expenses"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_expense_summary(self) -> dict:
        url = f"{self.base_url}/expenses/summary"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def delete_expense(self, expense_id: str) -> dict:
        url = f"{self.base_url}/expenses/{expense_id}"
        response = requests.delete(url, headers=self.headers)
        return response.json()


# Tools definitions for lang-graph
TOOLS = [
    {
        "name": "create_expense",
        "description": "Create a new expense with the given description, amount and category",
        "input_schema": {
            "type": "object",
            "properties": {
                "description": {"type": "string", "description": "The description of the expense"},
                "amount": {"type": "number", "description": "The amount of the expense in dollars"},
                "category": {
                    "type": "string",
                    "description": "Category (Food, Transport, Entertainment, etc)",
                },
            },
            "required": ["description", "amount", "category"],
        },
    },
    {
        "name": "get_expenses",
        "description": "Retrieve user's expenses with optional filtering",
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "Filter by category (optional)"},
                "limit": {
                    "type": "integer",
                    "description": "Max number of expenses to return (default 100)",
                },
            },
        },
    },
    {
        "name": "delete_expense",
        "description": "Delete an expense",
        "input_schema": {
            "type": "object",
            "properties": {
                "expense_id": {"type": "string", "description": "ID of expense to delete"}
            },
            "required": ["expense_id"],
        },
    },
]
