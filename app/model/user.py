from create_db import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    user_type_id = db.Column(db.Integer, db.ForeignKey('user_types.id'), nullable=False)
    user_type = db.relationship('UserType', backref=db.backref('users', lazy=True))
    password_hash = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'