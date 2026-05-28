from mongoengine import StringField, FloatField, Document



class User(Document):
    user_name: StringField
    pass_word: StringField

 
class ExpenseCategory(Document):
    category_id: StringField
    category_name: StringField
    category_desc: StringField

class ExpenseItem(Document):
    expense_id: StringField
    expense_cost: FloatField
    expense_date: StringField
    expense_category: StringField
