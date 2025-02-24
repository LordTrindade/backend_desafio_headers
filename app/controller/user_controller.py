
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import Swagger, swag_from
import os
# from model import User
# from service import UserService
# from utils import AuthorizationError,UserNotFoundError, UsedEmailError, InvalidUserType, MissingData
from  model.user import User
from  service.user_service import UserService
from  utils.exceptions import AuthorizationError,UserNotFoundError, UsedEmailError, InvalidUserType, MissingData

from  create_db import db


user_bp = Blueprint('users',__name__,url_prefix='/users')

base_dir = os.path.dirname(__file__)
swagger_dir = os.path.join(base_dir, '../docs/')
swagger_dir = os.path.normpath(swagger_dir)

@user_bp.route('/',methods=['GET'])
@jwt_required()
@swag_from(os.path.join(swagger_dir,'users/list_users.yml'))
def list_users():
    """Get a list of all users. This can be performed by any user"""
    try:
        users = UserService.list_users()
        users_data = [{'id': user.id, 'name': user.name, 'email': user.email} for user in users]
        return jsonify({'data': users_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@user_bp.route('/<int:user_id>', methods=['GET'])
@swag_from(os.path.join(swagger_dir,'users/get_user.yml'))
def get_user(user_id):
    """Get information about a single user. This can be performed by any user, and does not require authorization."""
    try:
        user = UserService.get_user_by_id(user_id)
        if user:
            return jsonify({'data': {'id': user.id, 'name': user.name, 'email': user.email}}), 200
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/register',methods=['POST'])
@swag_from(os.path.join(swagger_dir,'users/create_user.yml'))
def create_user():
    """To create a user. It needs data containing name, email, password and user_type"""
    #Seria possível criar a regra de que apenas admins podem criar usuários como admins. Nesse caso, seria analisado se há um token e qual a identidade do usuário daquele token.
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
@jwt_required()
@swag_from(os.path.join(swagger_dir,'users/update_user.yml'))
def update_user(user_id):
    """To update a user by its id. It's required its new data. Only the user himself or an admin user can perform this."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Data required'}), 400

    requesting_user = get_jwt_identity()
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
@jwt_required()
@swag_from(os.path.join(swagger_dir,'users/delete_user.yml'))
def delete_user(user_id):
    """To delete a specific user by its id. Only the user himself or an admin user can perform this."""
    requesting_user = get_jwt_identity()
    try:
        UserService.delete_user(user_id, requesting_user)
        return jsonify({'message': 'User deleted successfully'}), 200
    except AuthorizationError as e:
        return jsonify({'error': str(e)}), 403
    except UserNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500