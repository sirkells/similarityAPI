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

def verifyPw(username, password):
    hashed_pw = users.find({
        "Username": username
    })[0]["Password"]
    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False

def countTokens(username):
    tokens = users.find({
        "Username": username
    })[0]["Token"]
    return tokens

class Detect(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        text1 = postedData["text1"]
        text2 = postedData["text2"]


        if not UserExist(username):
            retJson = {
                "status": 301,
                "msg": "Username does not exist"
            }
            return jsonify(retJson)

        correct_pw = verifyPw(username, password)
        if not correct_pw:
            retJson = {
                "status": 302,
                "message": "invalid username/pwd"
                }
            return jsonify(retJson)


        #step4 verify user has enough tokens
        num_tokens= countTokens(username)
        if num_tokens <= 0:
            retJson = {
                "status": 301,
                "Error": "insufficient tokens, buy more tokens"
                }
            return jsonify(retJson)

        nlp = spacy.load('en_core_web_sm')
        text1 = nlp(text1)
        text2 =  nlp(text2)

        ratio = text1.similarity(text2)
        retJson = {
            "status": 200,
            "ratio": ratio,
            "Message": "Similarity ration succesfully calculated"
            }
        num_tokens= countTokens(username)
        users.update({
                "Username": username },
            {
                    "$set":{
                        "Token": num_tokens - 1
                }
            })

        return jsonify(retJson)

class Refill(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        refill_amount = postedData["refill"]


        if not UserExist(username):
            retJson = {
                "status": 301,
                "msg": "Username does not exist"
            }
            return jsonify(retJson)

        correct_pw = "abc123"
        if not password == correct_pw:
            retJson = {
                "status": 304,
                "msg": "Invalid Admin Password"
            }
            return jsonify(retJson)
        users.update({
                "Username": username },
            {
                    "$set":{
                        "Token": refill_amount
                }
            })
        retJson = {
            "status": 200,
            "msg": "Refilled Succesfully"
        }

        return jsonify(retJson)

api.add_resource(Register, '/register')
api.add_resource(Detect, '/detect')
api.add_resource(Refill, '/refill')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
