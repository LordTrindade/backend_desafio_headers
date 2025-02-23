from flask import Blueprint, jsonify, request
# from model import Post
# from service import PostService
# from utils import AuthorizationError,UserNotFoundError,PostNotFoundError, MissingData


from  model.post import Post
from  service.post_service import PostService; from service.user_service import UserService
from  utils.exceptions import AuthorizationError,UserNotFoundError,PostNotFoundError, MissingData

from  create_db import db

post_bp = Blueprint('posts',__name__,url_prefix='/posts')

@post_bp.route('/',methods=['GET'])
def get_all_posts():
    """Get list of every single post"""
    posts = PostService.list_all_posts()
    return jsonify({'data':posts}),200

@post_bp.route('/create',methods=['POST'])
def create_post():
    """create a post"""
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
def get_user_posts(user_id):
    """Get list of every user post"""
    #seria possivel tambem utilizar userservice para checar se o usuario existe, retornando erro caso nao
    posts  = PostService.list_posts_by_user_id(user_id=user_id)
    return jsonify({'data':posts}),200

@post_bp.route('/<int:post_id>',methods=['GET'])
def get_post(post_id):
    """Get a post by id"""
    #seria possivel tambem utilizar userservice para checar se o usuario existe, retornando erro caso nao
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


@post_bp.route('/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    try:
        data = request.get_json()
        user_id = data['requester_id']
        user = UserService.get_user_by_id(user_id)

        updated_post = PostService.update_post(post_id, user, title=data.get('title'), content=data.get('content'))
        return jsonify({'message': 'Post updated successfully','post_id':updated_post.id,'post_title':updated_post.title,'post_content':updated_post.content}), 200
    except PostNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except AuthorizationError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@post_bp.route('/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    try: 
        data = request.get_json()
        user_id = data['requester_id']
        user = UserService.get_user_by_id(user_id)
        
        PostService.delete_post(post_id, user)
        return jsonify({'message': 'Post deleted successfully'}), 200
    except PostNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except AuthorizationError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500