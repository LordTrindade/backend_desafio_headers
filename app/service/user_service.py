from werkzeug.security import generate_password_hash, check_password_hash
# from model import User, UserType
# from utils import AuthorizationError,UserNotFoundError, UsedEmailError, InvalidUserType, MissingData

from  model.user import User; from  model.user_type import UserType
from  utils.exceptions import AuthorizationError,UserNotFoundError, UsedEmailError, InvalidUserType, MissingData

from  create_db import db

class UserService:
    @staticmethod
    def create_user(name, email, password, user_type_id):
        """Creates a new user with the given details and saves to the database."""
        #seria possivel simplesmente permitir que usuarios so possam ser criados com o tipo 2: DEFAULT
    
        if not UserType.query.get(user_type_id):
            raise InvalidUserType("Invalid user type")

        if UserService.check_if_user_email_exists(email):
            raise UsedEmailError(f"An account with the email '{email}' already exists.")
        
        #nota: coloquei aqui o email de forma arbitraria...

        if name is None or email is None or user_type_id is None:
            raise MissingData(f"All fields required to create an user.")


        new_user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            user_type_id=user_type_id
        )
        #seria possivel simplesmente permitir que usuarios so possam ser criados com o tipo 2: DEFAULT
        
        db.session.add(new_user)
        db.session.commit()
        return new_user
    
    @staticmethod
    def check_if_user_email_exists(email):
        if User.query.filter_by(email=email).first():
            return True
        return False

    @staticmethod
    def update_user(user_id, requesting_user_id, **kwargs):
        """Updates an existing user's details in the database, checking for authorization."""
        user = User.query.filter_by(id=user_id).first()
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        
        requesting_user = UserService.get_user_by_id(requesting_user_id)

        if not (requesting_user.id == user_id or requesting_user.user_type.name == 'ADMIN'):
            raise AuthorizationError("Not authorized to update this user.")

        for key, value in kwargs.items():
            if key == 'password':
                setattr(user, 'password_hash', generate_password_hash(value))
            else:
                setattr(user, key, value)
        db.session.commit()
        return user

    @staticmethod
    def delete_user(user_id, requesting_user_id):
        """Deletes a user by their ID from the database, checking for authorization."""
        user = User.query.filter_by(id=user_id).first()
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")

        requesting_user = UserService.get_user_by_id(requesting_user_id)

        if not (requesting_user.id == user_id or requesting_user.user_type.name == 'ADMIN'):
            raise AuthorizationError("Not authorized to delete this user.")

        db.session.delete(user)
        db.session.commit()
        return True

    @staticmethod
    def get_user_by_id(user_id):
        """Retrieves a user by their ID from the database."""
        return User.query.get(user_id)
    
    def get_user_by_email(email):
        """Retrieves a user by their ID from the database."""
        return User.query.filter_by(email=email).first()

    @staticmethod
    def list_users():
        """Retrieves all users from the database."""
        return User.query.all()
    
    @staticmethod
    def verify_user_password(user_id, password):
        """
        Verifies that the provided password matches the hashed password of the user.
        
        Args:
        user_id (int): The ID of the user.
        password (str): The plaintext password to verify.
        
        Returns:
        bool: True if the password is correct, False otherwise.
        """
        user = User.query.get(user_id)
        if user is not None and check_password_hash(user.password_hash, password):
            return True
        return False