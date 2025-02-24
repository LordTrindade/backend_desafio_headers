#from model import Post, User
#from utils import AuthorizationError,UserNotFoundError,PostNotFoundError, MissingData
from  model.post import Post; from  model.user import User
from  utils.exceptions import AuthorizationError,UserNotFoundError,PostNotFoundError, MissingData

from  create_db import db

class PostService:
    @staticmethod
    def create_post(author_id, title, content):
        """Create new post"""
        if author_id is None or title is None or content is None:
            raise MissingData(f"É necessário todos os dados para criar o usuário.")
        
        user = User.query.filter_by(id=author_id).first()
        if not user:
            raise UserNotFoundError(f"User with id {author_id} not found")
        
        new_post = Post(author_id=author_id, title=title, content=content)
        db.session.add(new_post)
        db.session.commit()
        return new_post

    @staticmethod
    def update_post(post_id, user, title=None, content=None):
        """Update post, checking if authorized"""
        post = Post.query.get(post_id)
        if not post:
            raise PostNotFoundError(f"Post with ID {post_id} not found.")
        
        if not (post.author_id == user.id or user.user_type.name == 'ADMIN'):
            raise AuthorizationError("User not authorized to update this post.")

        if title:
            post.title = title
        if content:
            post.content = content
        db.session.commit()
        return post
    
    #num sistema real, seria possivel definir uma interface para classes novas, que verificam se um usuario pode ou nao editar o post
    #nesse caso, teriamos baixo acoplamento, e poderiamos trocar com mais facilidade a estrategia de permitir ou nao a edicao/delecao de um post
    #principalmente pois evitaria usos de ifs para caso as regras mudem.
    #porem, acredito que foge do escopo do desafio pensar tao longe assim.
    #na pratica, seria algo como uma classe Abstrata PermissionChecker, e em update_post/delete_post fariamos if self.permission_checker.authorize_edition(user,post)...

    @staticmethod
    def get_post_by_id(post_id):
        """Get post by id"""
        return Post.query.get(post_id)

    @staticmethod
    def list_all_posts():
        """Get all posts"""
        results = Post.query.join(User).add_columns(
            User.id.label('user_id'),
            User.name.label('user_name'),
            Post.id.label('post_id'),
            Post.title.label('post_title'),
            Post.content.label('post_content')
        ).all()

        # Convertendo os resultados em uma lista de dicionários
        posts = [{
            'user_id': row.user_id,
            'user_name': row.user_name,
            'post_id': row.post_id,
            'post_title': row.post_title,
            'post_content': row.post_content
        } for row in results]
        return posts

    @staticmethod
    def list_posts_by_user_id(user_id):
        """Get posts by user id"""
        results = Post.query.join(User).add_columns(
            User.id.label('user_id'),
            User.name.label('user_name'),
            Post.id.label('post_id'),
            Post.title.label('post_title'),
            Post.content.label('post_content')
        ).filter(Post.author_id == user_id).all()

        # Convertendo os resultados em uma lista de dicionários
        posts = [{
            'user_id': row.user_id,
            'user_name': row.user_name,
            'post_id': row.post_id,
            'post_title': row.post_title,
            'post_content': row.post_content
        } for row in results]
        return posts

    @staticmethod
    def delete_post(post_id, user):
        """Delete post if authorized"""

        post = Post.query.get(post_id)

        if not post:
            raise PostNotFoundError(f"Post with ID {post_id} not found.")
        
        if not (post.author_id == user.id or user.user_type.name == 'ADMIN'):
            raise AuthorizationError("User not authorized to update this post.")
        
        db.session.delete(post)
        db.session.commit()
        return True
