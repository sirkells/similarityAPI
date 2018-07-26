from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import spacy



app = Flask(__name__)
api = Api(app)
client = MongoClient("mongodb://db:27017")
db = client.SimilarityDB
users = db['Users']


def UserExist(username):
    if users.find({"Username":username}).count() == 0:
        return False
    else:
        return True

class Register(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]

        if UserExist(username):
            retJson = {
                "status": 301,
                "msg": "Invalid Username"
            }
            return jsonify(retJson)
        hashedpw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        users.insert({ "Username": username, "Password": hashedpw, "Token": 6 })

        retJson = {
            "status": 200,
            "message": "You succesfully signed up"
        }
        return jsonify(retJson)


api.add_resource(Register, '/register')



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
