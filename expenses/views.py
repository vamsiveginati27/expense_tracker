from bson import ObjectId
from flask import Blueprint, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_restful import Api, Resource, reqparse
from mongoengine import NotUniqueError
from mongoengine import ValidationError as MongoValidationError
from pydantic import ValidationError as PydanticValidationError

from .models import Expense, User
from .types import ExpenseRequest, ExpenseUpdateRequest, LoginRequest, RegisterRequest

# ==================== Auth Blueprint ====================

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
auth_api = Api(auth_bp)


class Register(Resource):
    def post(self):
        try:
            # Get JSON data
            data = request.get_json()
            if not data:
                return {"message": "Request body is required"}, 400

            # Validate input with Pydantic
            reg_request = RegisterRequest(**data)

            # Create user
            user = User(username=reg_request.username, email=reg_request.email)
            user.set_password(reg_request.password)
            user.save()

            return {"message": "User registered successfully", "user": user.to_dict()}, 201

        except PydanticValidationError as e:
            errors = [{"field": err["loc"][0], "message": err["msg"]} for err in e.errors()]
            return {"message": "Validation failed", "errors": errors}, 400
        except NotUniqueError:
            return {"message": "Username already exists"}, 409
        except Exception as e:
            return {"message": f"Registration error: {str(e)}"}, 400


class Login(Resource):
    def post(self):
        try:
            # Get JSON data
            data = request.get_json()
            if not data:
                return {"message": "Request body is required"}, 400

            # Validate input with Pydantic
            login_request = LoginRequest(**data)

            # Find user
            user = User.objects.get(username=login_request.username)
        except PydanticValidationError as e:
            errors = [{"field": err["loc"][0], "message": err["msg"]} for err in e.errors()]
            return {"message": "Validation failed", "errors": errors}, 400
        except User.DoesNotExist:
            return {"message": "Invalid credentials"}, 401

        # Check password
        if not user.check_password(login_request.password):
            return {"message": "Invalid credentials"}, 401

        access_token = create_access_token(identity=str(user.id))
        return {
            "message": "Login successful",
            "access_token": access_token,
            "user": user.to_dict(),
        }, 200


class UsersInfo(Resource):
    @jwt_required()
    def get(self):
        try:
            # Find user
            users = User.objects.all()

            users_response = []

            for user in users:
                users_response.append({"name": user.username, "email": user.email})
            return users_response, 200

        except Exception as e:
            return {"message": f"Error fetching expenses: {str(e)}"}, 400


auth_api.add_resource(Register, "/register")
auth_api.add_resource(Login, "/login")

# =================== Users Blueprint =======================
users_bp = Blueprint("users", __name__, url_prefix="/api/users")
users_api = Api(users_bp)

users_api.add_resource(UsersInfo, "")

# ==================== Expenses Blueprint ====================

expenses_bp = Blueprint("expenses", __name__, url_prefix="/api/expenses")
expenses_api = Api(expenses_bp)


class ExpenseList(Resource):
    @jwt_required()
    def get(self):
        try:
            current_user_id = get_jwt_identity()
            user = User.objects.get(id=ObjectId(current_user_id))
        except User.DoesNotExist:
            return {"message": "User not found"}, 404
        except Exception as e:
            return {"message": f"Error fetching user: {str(e)}"}, 400

        try:
            parser = reqparse.RequestParser()
            parser.add_argument("skip", type=int, default=0, location="args")
            parser.add_argument("limit", type=int, default=100, location="args")
            parser.add_argument("category", type=str, location="args")
            args = parser.parse_args()

            query = Expense.objects(user=user)
            if args["category"]:
                query = query(category=args["category"])

            expenses = [exp.to_dict() for exp in query.skip(args["skip"]).limit(args["limit"])]
            return {"expenses": expenses, "count": len(expenses), "total": query.count()}, 200
        except Exception as e:
            return {"message": f"Error fetching expenses: {str(e)}"}, 400

    @jwt_required()
    def post(self):
        try:
            current_user_id = get_jwt_identity()
            user = User.objects.get(id=ObjectId(current_user_id))
        except User.DoesNotExist:
            return {"message": "User not found"}, 404
        except Exception as e:
            return {"message": f"Error fetching user: {str(e)}"}, 400

        try:
            # Get JSON data
            data = request.get_json()
            if not data:
                return {"message": "Request body is required"}, 400

            # Validate input with Pydantic
            expense_request = ExpenseRequest(**data)

            # Create expense
            expense = Expense(
                user=user,
                description=expense_request.description,
                amount=expense_request.amount,
                category=expense_request.category,
            )
            expense.save()
            return expense.to_dict(), 201
        except PydanticValidationError as e:
            errors = [{"field": err["loc"][0], "message": err["msg"]} for err in e.errors()]
            return {"message": "Validation failed", "errors": errors}, 400
        except MongoValidationError as e:
            return {"message": str(e)}, 400
        except Exception as e:
            return {"message": f"Error creating expense: {str(e)}"}, 400


class ExpenseDetail(Resource):
    @jwt_required()
    def get(self, expense_id):
        current_user_id = get_jwt_identity()
        try:
            user = User.objects.get(id=ObjectId(current_user_id))
        except User.DoesNotExist:
            return {"message": "User not found"}, 404

        try:
            expense = Expense.objects.get(id=ObjectId(expense_id))
        except Expense.DoesNotExist:
            return {"message": "Expense not found"}, 404

        if expense.user.id != user.id:
            return {"message": "Unauthorized"}, 403

        return expense.to_dict(), 200

    @jwt_required()
    def put(self, expense_id):
        try:
            current_user_id = get_jwt_identity()
            user = User.objects.get(id=ObjectId(current_user_id))
        except User.DoesNotExist:
            return {"message": "User not found"}, 404
        except Exception as e:
            return {"message": f"Error fetching user: {str(e)}"}, 400

        try:
            expense = Expense.objects.get(id=ObjectId(expense_id))
        except Expense.DoesNotExist:
            return {"message": "Expense not found"}, 404

        if expense.user.id != user.id:
            return {"message": "Unauthorized"}, 403

        try:
            # Get JSON data
            data = request.get_json()
            if not data:
                return {"message": "Request body is required"}, 400

            # Validate input with Pydantic
            update_request = ExpenseUpdateRequest(**data)

            # Update fields
            if update_request.description is not None:
                expense.description = update_request.description
            if update_request.amount is not None:
                expense.amount = update_request.amount
            if update_request.category is not None:
                expense.category = update_request.category

            expense.save()
            return expense.to_dict(), 200
        except PydanticValidationError as e:
            errors = [{"field": err["loc"][0], "message": err["msg"]} for err in e.errors()]
            return {"message": "Validation failed", "errors": errors}, 400
        except MongoValidationError as e:
            return {"message": str(e)}, 400
        except Exception as e:
            return {"message": f"Error updating expense: {str(e)}"}, 400

    @jwt_required()
    def delete(self, expense_id):
        current_user_id = get_jwt_identity()
        try:
            user = User.objects.get(id=ObjectId(current_user_id))
        except User.DoesNotExist:
            return {"message": "User not found"}, 404

        try:
            expense = Expense.objects.get(id=ObjectId(expense_id))
        except Expense.DoesNotExist:
            return {"message": "Expense not found"}, 404

        if expense.user.id != user.id:
            return {"message": "Unauthorized"}, 403

        expense.delete()
        return {"message": "Expense deleted"}, 200


class ExpenseSummary(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        try:
            user = User.objects.get(id=ObjectId(current_user_id))
        except User.DoesNotExist:
            return {"message": "User not found"}, 404

        expenses = Expense.objects(user=user)

        summary = {}
        total = 0
        for exp in expenses:
            category = exp.category
            summary[category] = summary.get(category, 0) + exp.amount
            total += exp.amount

        return {"summary": summary, "total": total, "count": expenses.count()}, 200


expenses_api.add_resource(ExpenseList, "")
expenses_api.add_resource(ExpenseDetail, "/<string:expense_id>")
expenses_api.add_resource(ExpenseSummary, "/summary")
