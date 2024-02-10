import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


with app.app_context():
    db_drop_and_create_all()


@app.route('/drinks', methods=['GET'])
def get_drinks():
    """
    Public endpoint to get all drinks
    """
    try:
        drinks_query = Drink.query.all()
        drinks = [drink.short() for drink in drinks_query]

        return jsonify({
            "success": True,
            "drinks": drinks
        }), 200
    except:
        abort(500)

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    """
    Private endpoint to get all drinks with details
    """
    try:
        drinks = Drink.query.all()
        drinks = [drink.long() for drink in drinks]

        return jsonify({
            "success": True,
            "drinks": drinks
        }), 200
    except:
        abort(500)

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    """
    Create a new drink
    """
    try:
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get('recipe', None)

        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
    except:
        abort(422)

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    """
    Update a drink
    """
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if drink is None:
            abort(404)

        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get('recipe', None)

        if title:
            drink.title = title

        if recipe:
            drink.recipe = json.dumps(recipe)

        drink.update()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
    except:
        abort(422)

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    """
    Delete a drink
    """
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({
            "success": True,
            "delete": id
        }), 200
    except:
        abort(500)


@app.errorhandler(422)
def unprocessable(error):
    """
    Error handler for unprocessable entity
    """
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(404)
def not_found(error):
    """
    Error handler for resource not found
    """
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(AuthError)
def auth_error(error):
    """
    Error handler for AuthError
    """
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code


@app.errorhandler(401)
def unauthorized(error):
    """
    Error handler for unauthorized
    """
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unathorized'
    }), 401


@app.errorhandler(500)
def internal_server_error(error):
    """
    Error handler for internal server error
    """
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'Internal Server Error'
    }), 500


@app.errorhandler(400)
def bad_request(error):
    """
    Error handler for bad request
    """
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'Bad Request'
    }), 400


@app.errorhandler(405)
def method_not_allowed(error):
    """
    Error handler for method not allowed
    """
    return jsonify({
        "success": False,
        "error": 405,
        "message": 'Method Not Allowed'
    }), 405
