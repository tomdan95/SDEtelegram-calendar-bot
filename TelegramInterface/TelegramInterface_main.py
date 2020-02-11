from flask import Flask
from flask import render_template, make_response
from flask_restful import Resource, Api, request

from TelegramInterface import TelegramInterface

telegramInterface = TelegramInterface()

app = Flask(__name__)
api = Api(app)

class SucessfulLogin(Resource):
    def get(self):
        chatid = request.args.get('chatid')
        return telegramInterface.sendSuccessfulLoginMessage(chatid)
    
    def post(self):
        chatid = request.get_json().get('chatid')
        return telegramInterface.sendSuccessfulLoginMessage(chatid)

class Webhook(Resource): 
    def post(self):
        message = request.get_json()
        return telegramInterface.parseMessages(message)

class ReciveEvent(Resource):
    def post(self):
        reqest_json = request.get_json()
        summary = reqest_json.get('summary')
        chatid = reqest_json.get('chatid')
        location = reqest_json.get('location')
        return telegramInterface.reciveEvent(chatid, summary, location)

class GetPosition(Resource):
    def get(self):
        chatid = request.args.get('chatid')
        return telegramInterface.getLastPosition(chatid)
    
    def post(self):
        chatid = request.get_json().get('chatid')
        return telegramInterface.getLastPosition(chatid)

class GetActiveChats(Resource):
    def get(self):
        return telegramInterface.getActiceChats()
    
    def post(self):
        return telegramInterface.getActiceChats()

class UpdateMessages(Resource):
    def get(self):
        telegramInterface.getMesages()
        return {'ok': True}
    
    def post(self):
        telegramInterface.getMesages()
        return {'ok': True}

api.add_resource(SucessfulLogin, '/sucessfulLogin')
api.add_resource(Webhook, '/webhook')
api.add_resource(ReciveEvent, '/reciveEvent')
api.add_resource(GetPosition, '/getPosition')
api.add_resource(GetActiveChats, '/getActiveChats')
api.add_resource(UpdateMessages, '/updateMessages')

if __name__ == '__main__':
    #telegramInterface.getMesages()
    app.run(debug=True, use_reloader=False)
    #app.run(debug=True)