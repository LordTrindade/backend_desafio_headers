

from flask import Blueprint, jsonify, request
# from model import User
# from service import UserService
# from utils import AuthorizationError,UserNotFoundError, UsedEmailError, InvalidUserType, MissingData


from  model.user import User
from  service.user_service import UserService
from  utils.exceptions import AuthorizationError,UserNotFoundError, UsedEmailError, InvalidUserType, MissingData

from  create_db import db

user_bp = Blueprint('users',__name__,url_prefix='/users')

@user_bp.route('/',methods=['GET'])
def list_users():
    users = UserService.list_users()
    users_data = [{'id': user.id, 'name': user.name, 'email': user.email} for user in users]
    return jsonify({'data': users_data}), 200

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = UserService.get_user_by_id(user_id)
    if user:
        return jsonify({'data': {'id': user.id, 'name': user.name, 'email': user.email}}), 200
    return jsonify({'error': 'User not found'}), 404

@user_bp.route('/register',methods=['POST'])
def create_user():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        user = UserService.create_user(
            name=data['name'],
            email=data['email'],
            password=data['password'],
            user_type_id=data['user_type_id']
        )
        if user:
            return jsonify({'message': 'User created successfully', 'user_id': user.id}), 200
        else:
            return jsonify({'error': 'Could not create user. Email may be unavailable.'}), 401
    except UsedEmailError as e:
        return jsonify({'error': str(e)}), 403
    except InvalidUserType as e:
        return jsonify({'error': str(e)}), 403
    except MissingData as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Data required'}), 400

    requesting_user = data['requester_id']
    try:
        updated_user = UserService.update_user(user_id, requesting_user, **data)
        return jsonify({'message': 'User updated successfully', 'user': {'id': updated_user.id, 'name': updated_user.name, 'email': updated_user.email}}), 200
    except AuthorizationError as e:
        return jsonify({'error': str(e)}), 403
    except UserNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    data = request.get_json()
    requesting_user = data['requester_id']
    try:
        UserService.delete_user(user_id, requesting_user)
        return jsonify({'message': 'User deleted successfully'}), 200
    except AuthorizationError as e:
        return jsonify({'error': str(e)}), 403
    except UserNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500