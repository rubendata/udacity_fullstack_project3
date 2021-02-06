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
#db_drop_and_create_all()

## ROUTES
@app.route("/drinks", methods=["GET"])
def get_drinks():
    #TODO: error handling
    drinks = Drink.query.all()
    drinks = [drink.short() for drink in drinks]
    return jsonify({
        "success": True,
        "drinks": drinks
    })

@app.route("/drinks-detail", methods=["GET"])
def get_drinks_detail():
    #TODO: 
    # 1) 1error handling
    # 2) it should require the 'get:drinks-detail' permission
    drinks = Drink.query.all()
    drinks = [drink.long() for drink in drinks]
    return jsonify({
        "success": True,
        "drinks": drinks
    })

@app.route("/drinks", methods=["POST"])
def create_drink():
    #TODO: it should require the 'post:drinks' permission
    try:
        body = request.get_json()
        drink = Drink(
            title=body.get("title"),
            recipe=json.dumps(body.get("recipe"))
        )
        drink.insert()
        return jsonify({
            "success":True,
            "drink":drink.long()
        })
    except BaseException as e:
        print(e)
        abort(401)


@app.route("/drinks/<id>", methods=["PATCH"])
def specific_drink(id):
    #TODO: 
    # it should respond with a 404 error if <id> is not found, 
    # it should require the 'patch:drinks' permission
    
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
            if type(body.get(i)) == list:
                setattr(drink, i, json.dumps(body.get(i)))
            else:
                setattr(drink, i, body.get(i))
            # print(f"after: {getattr(drink, i)}")
        drink.update()
        drink = drink.long()
        return jsonify({
            "success":True,
            "drink":drink
        })
    except BaseException as e:
        print(e)
        abort(400)

    

@app.route("/drinks/<id>", methods=["DELETE"])
def delete_drink(id):
    
    #TODO:  it should require the 'delete:drinks' permission
    try:
        drink = Drink.query.filter_by(id=id).one_or_none()
        print(drink)
        drink.delete()
        return jsonify({
            "success":True,
            "delete":id
        })
    except BaseException as e:
        print(e)
        abort(404)

    

## Error Handling
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
