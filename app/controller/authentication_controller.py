
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token,jwt_required, get_jwt_identity
from flasgger import Swagger, swag_from
from model.user import User;
from service.user_service import UserService

auth_bp = Blueprint('login',__name__,url_prefix='/authentication')


import os
base_dir = os.path.dirname(__file__)
swagger_dir = os.path.join(base_dir, '../docs/')
swagger_dir = os.path.normpath(swagger_dir)

@auth_bp.route('/login', methods=['POST'])
@swag_from(os.path.join(swagger_dir,'authentication/login.yml'))
def login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    user = UserService.get_user_by_email(email)
    if(user is None):
        return jsonify({"msg": "Email not registered."}), 401
    result = UserService.verify_user_password(user_id=user.id,password=password)
    if result:
        access_token = create_access_token(identity=user.id, additional_claims={"user_type_id": user.user_type_id})
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Bad password."}), 401

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required()
def refresh_token():
    current_user = get_jwt_identity()

    new_token = create_access_token(identity=current_user)

    return jsonify(access_token=new_token), 200

#nao cheguei a usar a funcao na pratica... mas teoricamente, aqui seria o refresh do token. poderia ser feito ao acessar certos endpoints.