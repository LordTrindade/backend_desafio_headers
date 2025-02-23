
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from model.user import User;
from service.user_service import UserService

login_bp = Blueprint('login',__name__,url_prefix='/login')

@login_bp.route('/login', methods=['POST'])
def login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    # Suponha que você tenha uma função que verifica o usuário e senha
    user = UserService.get_user_by_email(email)
    if(user is None):
        return jsonify({"msg": "Email not registered"}), 401
    result = UserService.verify_user_password(user_id=user.id,password=password)
    if result:
        access_token = create_access_token(identity=email, additional_claims={"user_type_id": user.user_type_id})
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Bad password"}), 401
