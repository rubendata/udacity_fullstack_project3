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


@app.route("/drinks/<id>", methods=["GET","PATCH", "DELETE"])
def specific_drink(id):
    #TODO: 
    # it should respond with a 404 error if <id> is not found, 
    # it should require the 'patch:drinks' permission
    if request.method=="PATCH":
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
    if request.method=="DELETE":
        try:
            drink = Drink.query.filter_by(id=id).one_or_none()
            print(drink)
            drink.delete()
            return jsonify({
                "success":True,
                "deleted_id":id
            })
        except BaseException as e:
            print(e)
            abort(400)
    else:
        try:
            drink = Drink.query.filter_by(id=id).one_or_none()
            drink.long()
            return jsonify({
                "success":True,
                "drink":drink
            })
        except BaseException as e:
            print(e)
            abort(400)


    
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


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

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
