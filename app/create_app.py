from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

#from service import UserService, PostService
from service.user_service import UserService; from service.post_service import PostService
#from controller import post_bp,user_bp
from controller.post_controller import post_bp; from controller.user_controller import user_bp

from create_db import db
from config import Config

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    jwt = JWTManager(app)

 
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(user_bp)
    app.register_blueprint(post_bp)

    @app.route('/')
    def home():
        return 'Hello from Flask!'

    return app

def ensure_admin_exists():
    # Verifica se existe um usuário com ID 1
    admin_user = UserService.get_user_by_id(1)
    if not admin_user:
        # Se não existir, cria o usuário admin
        print("Admin user does not exist, creating one...")
        # usuario admin criado com valor de tipo 1
        admin_type_id = 1
        admin_name = "admin"
        admin_email = "filipetrindade00@gmail.com"
        admin_password = "admin"
        UserService.create_user(name=admin_name, email=admin_email, password=admin_password, user_type_id=admin_type_id)
        print("Admin user created with ID 1.")
    else:
        print("Admin user already exists.")