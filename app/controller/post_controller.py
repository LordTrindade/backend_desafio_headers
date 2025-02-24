from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import Swagger, swag_from
import os

# from model import Post
# from service import PostService
# from utils import AuthorizationError,UserNotFoundError,PostNotFoundError, MissingData
from  model.post import Post
from  service.post_service import PostService; from service.user_service import UserService
from  utils.exceptions import AuthorizationError,UserNotFoundError,PostNotFoundError, MissingData

from  create_db import db

post_bp = Blueprint('posts',__name__,url_prefix='/posts')

base_dir = os.path.dirname(__file__)
swagger_dir = os.path.join(base_dir, '../docs/')
swagger_dir = os.path.normpath(swagger_dir)

#seria possivel criar uma rota de perfil, que mostra informacoes de um usuario e seus posts.

@post_bp.route('/',methods=['GET'])
@swag_from(os.path.join(swagger_dir,'posts/get_all_posts.yml'))
def get_all_posts():
    """Get list of every single post"""
    try:
        posts = PostService.list_all_posts()
        return jsonify({'data':posts}),200
    except Exception as e:
        return jsonify({'error': e}), 500

@post_bp.route('/create',methods=['POST'])
@jwt_required()
@swag_from(os.path.join(swagger_dir,'posts/create_posts.yml'))
def create_post():
    """Create a post. It requires author_id, title and post content."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing data'}), 400
    
    try:
        post = PostService.create_post(
            author_id=data['author_id'],
            title=data['title'],
            content=data['content']
        )
    except MissingData as e:
        return jsonify({'error': e}), 400
    except Exception as e:
        return jsonify({'error': e}), 400
    

    if(post):
        return jsonify({'message': 'Post created successfully', 'post_id': post.id,'post_title':post.title,'post_content':post.content}), 201
    else:
        return jsonify({'error': 'Could not create post.'}), 400
    

@post_bp.route('/user/<int:user_id>',methods=['GET'])
@swag_from(os.path.join(swagger_dir,'posts/get_user_posts.yml'))
def get_user_posts(user_id):
    """Get list of posts by an specific user."""
    #seria possivel tambem utilizar userservice para checar se o usuario existe, retornando erro caso nao
    try:
        posts  = PostService.list_posts_by_user_id(user_id=user_id)
        return jsonify({'data':posts}),200
    except Exception as e:
        return jsonify({'error': e}), 500

@post_bp.route('/<int:post_id>',methods=['GET'])
@swag_from(os.path.join(swagger_dir,'posts/get_post.yml'))
def get_post(post_id):
    """Get a post by id."""
    #seria possivel tambem utilizar userservice para checar se o usuario existe, retornando erro caso nao
    try:
        post = PostService.get_post_by_id(post_id)
        if post is None:
            return jsonify({'error': 'Post not found'}), 404
        else:
            return jsonify({
                'id': post.id,
                'author_id': post.author_id,
                'author_name':post.author.name,
                'title': post.title,
                'content': post.content
            }), 200
    except Exception as e:
        return jsonify({'error': e}), 500


@post_bp.route('/<int:post_id>', methods=['PUT'])
@jwt_required()
@swag_from(os.path.join(swagger_dir,'posts/update_post.yml'))
def update_post(post_id):
    """Update a post by its data. It requires the new data. Only the author himself or an admin user can perform this."""
    try:
        data = request.get_json()
        requesting_user = get_jwt_identity()
        user = UserService.get_user_by_id(requesting_user)

        updated_post = PostService.update_post(post_id, user, title=data.get('title'), content=data.get('content'))
        return jsonify({'message': 'Post updated successfully','post_id':updated_post.id,'post_title':updated_post.title,'post_content':updated_post.content}), 200
    except PostNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except AuthorizationError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@post_bp.route('/<int:post_id>', methods=['DELETE'])
@jwt_required()
@swag_from(os.path.join(swagger_dir,'posts/delete_post.yml'))
def delete_post(post_id):
    """To delete a post. Only the author himself or an admin user can perform this."""
    try: 
        requesting_user = get_jwt_identity()
        user = UserService.get_user_by_id(requesting_user)

        PostService.delete_post(post_id, user)
        return jsonify({'message': 'Post deleted successfully'}), 200
    except PostNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except AuthorizationError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500