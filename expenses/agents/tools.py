import requests
from typing import Any, Optional
from config import settings


class ExpenseTools:

    def __init__(self):
        self.base_url = settings.expense_api_base_url