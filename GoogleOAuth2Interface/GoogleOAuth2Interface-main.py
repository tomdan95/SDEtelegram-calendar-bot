from flask import Flask
from flask import render_template, make_response
from flask_restful import Resource, Api, request

from GoogleOAuth2Interface import GoogleOAuth2Interface

googleOAuth2Interface = GoogleOAuth2Interface()

app = Flask(__name__)
api = Api(app)

class Login(Resource):
    def get(self):
        chatid = request.args.get('chatid')
        apipsw = request.args.get('apipsw')
        return googleOAuth2Interface.login(chatid, apipsw)
    
    def post(self):
        chatid = request.get_json().get('chatid')
        apipsw = request.get_json().get('apipsw')
        return googleOAuth2Interface.login(chatid, apipsw)

class Oauth2Callback(Resource):
    def get(self):
        state = request.args.get('state')
        token = request.args.get('code')
        return googleOAuth2Interface.oauth2Callback(state, token)
    
    def post(self):
        request_json = request.get_json()
        state = request_json.get('state')
        token = request_json.get('code')
        return googleOAuth2Interface.oauth2Callback(state, token)

class GetCredentials(Resource):
    def get(self):
        chatid = request.args.get('chatid')
        apipsw = request.args.get('apipsw')
        return googleOAuth2Interface.getCredentials(chatid, apipsw)
    
    def post(self):
        chatid = request.get_json().get('chatid')
        apipsw = request.get_json().get('apipsw')
        return googleOAuth2Interface.getCredentials(chatid, apipsw)

api.add_resource(Login, '/login')
api.add_resource(Oauth2Callback, '/oauth2callback')
api.add_resource(GetCredentials, '/getCredentials')

if __name__ == '__main__':
    #app.run(debug=True, port=5001)
    app.run(debug=True, use_reloader=False, port=5001)