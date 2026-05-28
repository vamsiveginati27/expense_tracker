from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
api = Api(app)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)

# In-memory database (replace with real DB in production)
expenses = {}
users = {'user1': 'password123'}  # Simple user store
expense_id_counter = 1


# ==================== Auth Endpoints ====================

class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='Username required')
        parser.add_argument('password', type=str, required=True, help='Password required')
        args = parser.parse_args()

        # Validate credentials (in production, hash passwords!)
        if args['username'] not in users or users[args['username']] != args['password']:
            return {'message': 'Invalid credentials'}, 401

        access_token = create_access_token(identity=args['username'])
        return {
            'message': 'Login successful',
            'access_token': access_token,
            'user': args['username']
        }, 200


# ==================== Expense Endpoints ====================

class ExpenseList(Resource):
    @jwt_required()
    def get(self):
        """Get all expenses for current user"""
        current_user = get_jwt_identity()
        user_expenses = [
            exp for exp in expenses.values()
            if exp.get('user') == current_user
        ]
        return {'expenses': user_expenses, 'count': len(user_expenses)}, 200

    @jwt_required()
    def post(self):
        """Create new expense"""
        global expense_id_counter
        current_user = get_jwt_identity()

        parser = reqparse.RequestParser()
        parser.add_argument('description', type=str, required=True, help='Description required')
        parser.add_argument('amount', type=float, required=True, help='Amount required')
        parser.add_argument('category', type=str, default='Other')
        args = parser.parse_args()

        expense = {
            'id': expense_id_counter,
            'user': current_user,
            'description': args['description'],
            'amount': args['amount'],
            'category': args['category'],
            'date': datetime.now().isoformat()
        }

        expenses[expense_id_counter] = expense
        expense_id_counter += 1

        return expense, 201


class ExpenseDetail(Resource):
    @jwt_required()
    def get(self, expense_id):
        """Get single expense"""
        current_user = get_jwt_identity()
        expense = expenses.get(expense_id)

        if not expense:
            return {'message': 'Expense not found'}, 404

        if expense['user'] != current_user:
            return {'message': 'Unauthorized'}, 403

        return expense, 200

    @jwt_required()
    def put(self, expense_id):
        """Update expense"""
        current_user = get_jwt_identity()
        expense = expenses.get(expense_id)

        if not expense:
            return {'message': 'Expense not found'}, 404

        if expense['user'] != current_user:
            return {'message': 'Unauthorized'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('description', type=str)
        parser.add_argument('amount', type=float)
        parser.add_argument('category', type=str)
        args = parser.parse_args()

        if args['description']:
            expense['description'] = args['description']
        if args['amount']:
            expense['amount'] = args['amount']
        if args['category']:
            expense['category'] = args['category']

        return expense, 200

    @jwt_required()
    def delete(self, expense_id):
        """Delete expense"""
        current_user = get_jwt_identity()
        expense = expenses.get(expense_id)

        if not expense:
            return {'message': 'Expense not found'}, 404

        if expense['user'] != current_user:
            return {'message': 'Unauthorized'}, 403

        del expenses[expense_id]
        return {'message': 'Expense deleted'}, 200


class ExpenseSummary(Resource):
    @jwt_required()
    def get(self):
        """Get expense summary by category"""
        current_user = get_jwt_identity()
        user_expenses = [
            exp for exp in expenses.values()
            if exp.get('user') == current_user
        ]

        summary = {}
        total = 0
        for exp in user_expenses:
            category = exp['category']
            summary[category] = summary.get(category, 0) + exp['amount']
            total += exp['amount']

        return {
            'summary': summary,
            'total': total,
            'count': len(user_expenses)
        }, 200


# ==================== Register Routes ====================

api.add_resource(Login, '/api/auth/login')
api.add_resource(ExpenseList, '/api/expenses')
api.add_resource(ExpenseDetail, '/api/expenses/<int:expense_id>')
api.add_resource(ExpenseSummary, '/api/expenses/summary')


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    return {'message': 'Endpoint not found'}, 404


@app.errorhandler(500)
def internal_error(error):
    return {'message': 'Internal server error'}, 500


# ==================== Health Check ====================

@app.route('/api/health', methods=['GET'])
def health():
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}, 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
