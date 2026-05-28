from pydantic.dataclasses import dataclasses
from datetime import datetime

@dataclasses
class User:
    user_name: str
    pass_word: str

    def __init__(self, user_name, pass_word):
        self.user_name = user_name
        self.pass_word = pass_word

@dataclasses
class ExpenseCategory:
    category_id: str
    category_name: str
    category_desc: str

@dataclasses
class ExpenseItem:
    expense_id: str
    expense_cost: float
    expense_date: str
    expense_category: str


