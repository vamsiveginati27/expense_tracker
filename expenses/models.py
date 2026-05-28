from mongoengine import Document, StringField, FloatField, DateTimeField, ReferenceField
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(Document):
    username = StringField(required=True, unique=True)
    password_hash = StringField(required=True)
    email = StringField()
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'users',
        'indexes': ['username']
    }

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }


class Expense(Document):
    user = ReferenceField(User, required=True)
    description = StringField(required=True, max_length=200)
    amount = FloatField(required=True, min_value=0)
    category = StringField(default='Other', max_length=50)
    date = DateTimeField(default=datetime.utcnow)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'expenses',
        'indexes': ['user', 'category', 'date'],
        'ordering': ['-date']
    }

    def to_dict(self):
        return {
            'id': str(self.id),
            'user': str(self.user.id),
            'description': self.description,
            'amount': self.amount,
            'category': self.category,
            'date': self.date.isoformat(),
            'created_at': self.created_at.isoformat()
        }

    @classmethod
    def get_by_user(cls, user, skip=0, limit=100):
        return cls.objects(user=user).skip(skip).limit(limit)

    @classmethod
    def get_summary_by_category(cls, user):
        pipeline = [
            {'$match': {'user': user.id}},
            {'$group': {'_id': '$category', 'total': {'$sum': '$amount'}}},
            {'$sort': {'total': -1}}
        ]
        return cls.objects.aggregate(pipeline)