from create_db import db

class UserType(db.Model):
    __tablename__ = 'user_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)

#tipos criados:
#ADMIN
#DEFAULT

#seria possivel tambem criar uma tabela a mais que relaciona o usuario ao tipo. estaria em uma forma mais normalizada.