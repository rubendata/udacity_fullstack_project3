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

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

# ROUTES


@app.route("/drinks", methods=["GET"])  # public endpoint
def get_drinks():
    # TODO: error handling
    drinks = Drink.query.all()
    drinks = [drink.short() for drink in drinks]
    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route("/drinks-detail", methods=["GET"])
@requires_auth("get:drinks-detail")
def get_drinks_detail(jwt):
    try:
        drinks = Drink.query.all()
        drinks = [drink.long() for drink in drinks]
        return jsonify({
            "success": True,
            "drinks": drinks
        })
    except BaseException as e:
        print(e)
        abort(401)


@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def create_drink(jwt):
    try:
        body = request.get_json()
        print(type(body.get("recipe")))

        if not isinstance(body.get("recipe"), list):
            return abort(400)

        drink = Drink(
            title=body.get("title"),
            recipe=json.dumps(body.get("recipe"))
        )
        drink.insert()
        return jsonify({
            "success": True,
            "drink": drink.long()
        })
    except BaseException as e:
        print(e)
        abort(400, "recipe must be type list")


@app.route("/drinks/<id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def specific_drink(jwt, id):
    try:
        body = request.get_json()
        drink = Drink.query.filter_by(id=id).one_or_none()
        for i in body:
            '''
            The input for body can be flexibel: title, title+recipe, recipe
            So used this variable for loop to get whatever is typed in
            and use this data to patch the item
            '''
            #print(f"key: {i}, value:{body.get(i)}")
            # print(f"before: {getattr(drink, i)}")
            if i == "recipe" and not isinstance(i, list):
                return abort(400)
            if isinstance(body.get(i), list):
                setattr(drink, i, json.dumps(body.get(i)))
            else:
                setattr(drink, i, body.get(i))
            # print(f"after: {getattr(drink, i)}")
        drink.update()
        drink = drink.long()
        return jsonify({
            "success": True,
            "drinks": [drink]
        })
    except BaseException as e:
        print(e)
        abort(404)


@app.route("/drinks/<id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(jwt, id):
    try:
        drink = Drink.query.filter_by(id=id).one_or_none()
        drink.delete()
        return jsonify({
            "success": True,
            "delete": id
        })
    except BaseException as e:
        print(e)
        abort(404)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "not found"
    }), 404


@app.errorhandler(401)
@app.errorhandler(AuthError)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
