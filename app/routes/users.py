from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from flask import Blueprint, request, jsonify, current_app, abort

from app.utils.auth.auth import get_jwt, token_required, firewall
from app.utils.recommender import recommend_movies_endpoint

users_bp = Blueprint('users', __name__)


# ---------------------------------------------- GET ----------------------------------------------

@users_bp.route('/users', methods=['GET'])
@firewall
def get_users():
    users = list(current_app.db.users.find())
    for user in users:
        user['_id'] = str(user['_id'])
    return jsonify(users)


@users_bp.route('/users/<user_id>', methods=['GET'])
@token_required
def get_user(sub, user_id):
    if sub != user_id:
        return jsonify({'message': 'Forbidden'}), 403
    try:
        # Convert user_id to ObjectId
        object_id = ObjectId(user_id)
    except InvalidId:
        # If user_id is not a valid ObjectId, return a 404 error
        return jsonify({'message': 'Cannot find user'}), 404

    # Try to find the user in the database
    user = current_app.db.users.find_one({'_id': object_id})
    if user:
        # If user is found, convert ObjectId to string and return user data
        user['_id'] = str(user['_id'])
        return jsonify(user), 200
    else:
        # If user is not found, return a 404 error
        return jsonify({'message': 'Cannot find user'}), 404


@users_bp.route('/users/<user_id>/recommendations', methods=['GET'])
@token_required
def get_user_recommendation(sub, user_id):
    if sub != user_id:
        return jsonify({'message': 'Forbidden'}), 403
    try:
        object_id = ObjectId(user_id)
    except InvalidId:
        # If user_id is not a valid ObjectId, return a 404 error
        abort(404, description="User not found")

    # Try to find the user in the database
    user = current_app.db.users.find_one({'_id': object_id})
    if user:
        # If user is found, convert ObjectId to string and return recommendations
        k = int(request.args.get('k', 5))
        # @todo qua serve il metodo per la raccomandazione ###
        recommendations = user['recommendation'][:k]
        return jsonify(recommendations), 200
    else:
        # If user is not found, return a 404 error
        abort(404, description="User not found")


@users_bp.route('/users/<user_id>/ratings', methods=['GET'])
@token_required
def get_user_ratings(sub, user_id):
    if sub != user_id:
        return jsonify({'message': 'Forbidden'}), 403
    try:
        # Convert user_id to ObjectId
        object_id = ObjectId(user_id)
    except InvalidId:
        # If user_id is not a valid ObjectId, return a 404 error
        abort(404, description="User not found")

    # Try to find the user in the database
    user = current_app.db.users.find_one({'_id': object_id})
    if user:
        # If user is found, convert ObjectId to string and return recommendations
        ratings = user['ratings']
        return jsonify(ratings), 200
    else:
        # If user is not found, return a 404 error
        abort(404, description="User not found")


# ---------------------------------------------- POST ----------------------------------------------

@users_bp.route('/users', methods=['POST'])
def add_new_user():
    # Parse JSON data from the request
    data = request.get_json()
    current_time = datetime.now()

    # Construct the user object with default values where necessary
    user = {
        'browser': data.get('browser'),
        'os': data.get('os'),
        'language': data.get('language'),
        'ratings': data.get('ratings', []),
        'recommendations': data.get('recommendations', []),  # Fixed spelling: 'recommendations'
        'created_at': datetime.timestamp(current_time),
        'updated_at': datetime.timestamp(current_time),
        'version': 1
    }

    try:
        # Insert the new user into the database
        user_id = current_app.db.users.insert_one(user).inserted_id
    except Exception as e:
        # Handle database insertion errors
        current_app.logger.error(f"Error inserting new user: {e}")
        return jsonify({'error': 'Failed to add new user'}), 400

    # Convert the ObjectId to a string for JSON serialization
    user['_id'] = str(user_id)

    # Generate the JWT for the new user
    token = get_jwt({'sub': str(user_id)})

    return jsonify({'user': user, 'token': token}), 201


@users_bp.route('/users/<user_id>/ratings', methods=['POST'])
@token_required
def add_user_rating(sub, user_id):
    if sub != user_id:
        return jsonify({'message': 'Forbidden'}), 403
    data = request.get_json()
    current_time = datetime.now()

    # Validate the input data
    if not data:
        return jsonify({'message': 'No input data provided'}), 400
    if 'item_id' not in data:
        return jsonify({'message': 'Missing item_id'}), 400
    if data.get('score') is not None:
        if not isinstance(data['score'], int) or data['score'] < 1 or data['score'] > 5:
            return jsonify({'message': 'Invalid rating value'}), 400

    # check if item_id exists
    try:
        ObjectId(data['item_id'])
    except InvalidId:
        return jsonify({'message': 'Invalid item_id'}), 400

    rating = {
        'item_id': data['item_id'],
        'score': data['score'] if 'score' in data else None,
        'timestamp': datetime.timestamp(datetime.now()),
        'created_at': datetime.timestamp(current_time),
        'updated_at': datetime.timestamp(current_time),
        'version': 1,
    }

    try:
        # Insert the new rating into the database, using the user_id to identify the user, set updated_at and version
        current_app.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$push': {'ratings': rating},
             '$set': {'updated_at': datetime.timestamp(current_time), 'version': data.get('version', 1) + 1}}
        )
    except Exception as e:
        # Handle database insertion errors
        current_app.logger.error(f"Error inserting new rating: {e}")
        return jsonify({'error': 'Failed to add new rating'}), 400

    return jsonify(rating), 201


@users_bp.route('/users/<user_id>/recommendations', methods=['POST'])
@token_required
def add_recommendation_feedback(sub, user_id):
    if sub != user_id:
        return jsonify({'message': 'Forbidden'}), 403
    data = request.get_json()
    feedback = {
        'item_id': data['item_id'],
        'score': data['score'],
        'pred_score': data['pred_score'],
        'is_known': data['is_known'],
        'timestamp': datetime.timestamp(datetime.now())
    }
    current_app.db.users.update_one({'user_id': data['user_id']}, {'$push': {'recommendation': feedback}})
    return jsonify(feedback)


# ---------------------------------------------- PUT ----------------------------------------------
@users_bp.route('/users/<user_id>', methods=['PUT'])
@token_required
def update_user(sub, user_id):
    if sub != user_id:
        return jsonify({'message': 'Forbidden'}), 403

    try:
        object_id = ObjectId(user_id)
    except InvalidId:
        return jsonify({'message': 'Invalid user_id'}), 400

    # Retrieve and validate input data
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No input data provided'}), 400

    # Filter out any fields that should not be updated
    disallowed_fields = ['_id', 'user_id', 'password', 'created_at', 'updated_at', 'version', 'deleted_at', 'ratings',
                         'recommendations']
    update_data = {key: value for key, value in data.items() if key not in disallowed_fields}
    update_data['updated_at'] = datetime.timestamp(datetime.now())
    update_data['version'] = current_app.db.users.find_one({'_id': object_id})['version'] + 1

    if not update_data:
        return jsonify({'message': 'No valid fields to update'}), 400

    try:
        # Update user document in the database
        result = current_app.db.users.update_one({'_id': object_id}, {'$set': update_data})
        if result.matched_count == 0:
            return jsonify({'message': 'User not found'}), 404

        # Retrieve the updated user document
        user = current_app.db.users.find_one({'_id': object_id})
        if not user:
            return jsonify({'message': 'User not found after update'}), 404

        user['_id'] = str(user['_id'])  # Convert ObjectId to string for JSON serialization
        return jsonify({'message': 'User updated successfully', 'user': user}), 200

    except Exception as e:
        current_app.logger.error(f"Error updating user: {e}")
        return jsonify({'message': 'Internal server error'}), 500


@users_bp.route('/users/<user_id>/ratings', methods=['PUT'])
@token_required
def update_user_rating(sub, user_id):
    if sub != user_id:
        return jsonify({'message': 'Forbidden'}), 403

    try:
        object_id = ObjectId(user_id)
    except InvalidId:
        return jsonify({'message': 'Invalid user_id'}), 400

    data = request.get_json()
    if not data:
        return jsonify({'message': 'No input data provided'}), 400

    if 'item_id' not in data:
        return jsonify({'message': 'Missing item_id'}), 400

    if data.get('score') is not None:
        if not isinstance(data['score'], int) or data['score'] < 1 or data['score'] > 5:
            return jsonify({'message': 'Invalid rating value'}), 400

    rating = {
        'item_id': data['item_id'],
        'score': data['score'] if 'score' in data else None,
        'timestamp': datetime.timestamp(datetime.now())
    }

    try:
        current_app.db.users.update_one(
            {'_id': object_id, 'ratings.item_id': data['item_id']},
            {'$set': {'ratings.$.score': rating['score'], 'ratings.$.timestamp': rating['timestamp']}}
        )
    except Exception as e:
        current_app.logger.error(f"Error updating rating: {e}")
        return jsonify({'error': 'Failed to update rating'}), 400

    return jsonify(rating), 200
