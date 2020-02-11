import requests
import time
import urllib
import json

from flask import Flask
from flask import render_template, make_response
from flask_restful import Resource, Api

class TelegramInterface():
    def __init__(self):
        self._googleOAuth2InterfaceUrl = 'http://127.0.0.1:5001'
        self._googleOAuth2Interface_apipsw = 'placeholder'
        self._telegramAPIToken = 'placeholder'

        with open('settings.json') as json_file:
            data = json.load(json_file)
            self._googleOAuth2InterfaceUrl = data.get('googleOAuth2InterfaceUrl')
            self._googleOAuth2Interface_apipsw = data.get('apipsw')
            self._telegramAPIToken = data.get('telegramAPIToken')

        self._telegramAPIUrl = 'https://api.telegram.org/bot'
        self._lastUpdateId = 0
        self._activeChats = set()
        self._lastChatsPosition = {}
        self._botUsername = requests.get(self._telegramAPIUrl + self._telegramAPIToken +'/getMe').json()['result']['username']
    
    def parseMessages(self, jsonMessage):
        self._lastUpdateId = int(jsonMessage['update_id'])

        msgName = 'message'
        if not msgName in jsonMessage:
            msgName = 'edited_message'
        
        chatid = int(jsonMessage[msgName]['chat']['id'])
        text = jsonMessage[msgName].get('text', '')

        #check if it is first message
        welcomeSent = False
        if not chatid in self._activeChats:
            self._activeChats.add(chatid)
            #send welcome message
            welcomeSent = True
            self.__sendWelcomeMessage(chatid)
        
        if('text' in jsonMessage[msgName]):
            if (text == '/start') and (not welcomeSent):
                #send welcome message
                self.__sendWelcomeMessage(chatid)
            
            elif (text == '/login'):
                #send login link"
                self.__sendLoginLink(chatid)
            else:
                #ingore non comands messages
                pass
        
        if('location' in jsonMessage[msgName]):
            self._lastChatsPosition[chatid] = (jsonMessage[msgName]['location']['latitude'], jsonMessage[msgName]['location']['longitude'])
        return {'ok':'true'}
    
    def __sendWelcomeMessage(self, chatid):
        chatid = int(chatid)
        text = 'Welcome to ' + self._botUsername + ' the telegram bot that remind you of your appoinments!\n Please log in to your Google calendar acount and share your position whit us.\n Use the /login comand to recive a login link'
        requests.post(self._telegramAPIUrl + self._telegramAPIToken +'/sendMessage', json={"chat_id": chatid, "text": text})
    
    def __sendLoginLink(self, chatid):
        chatid = int(chatid)
        response = requests.post(self._googleOAuth2InterfaceUrl +'/login', json={"chatid": chatid, 'apipsw': self._googleOAuth2Interface_apipsw})
        json_response = response.json()
        text = json_response['message']
        requests.post(self._telegramAPIUrl + self._telegramAPIToken +'/sendMessage', json={"chat_id": chatid, "text": text})
        if 'link' in json_response:
            text = json_response['link']
            requests.post(self._telegramAPIUrl + self._telegramAPIToken +'/sendMessage', json={"chat_id": chatid, "text": text})
    
    def sendSuccessfulLoginMessage(self, chatid):
        chatid = int(chatid)
        text = 'You have successfully logged in to your Google Acccount!'
        requests.post(self._telegramAPIUrl + self._telegramAPIToken +'/sendMessage', json={"chat_id": chatid, "text": text})
        return {'ok': True}
    
    def getLastPosition(self, chatid):
        chatid = int(chatid)
        lastPosition = self._lastChatsPosition.get(chatid, (0,0))
        #lastPosition = self._lastChatsPosition[chatid]
        return {'latitude': lastPosition[0], 'longitude': lastPosition[1]}
    
    def getActiceChats(self):
        chatList = list(self._activeChats)
        return {"items":chatList}

    def getMesages(self):
        response = requests.get(self._telegramAPIUrl + self._telegramAPIToken + '/getUpdates?offset=' + str(self._lastUpdateId + 1))
        json_response = response.json()
        for message in json_response['result']:
            self.parseMessages(message)
    
    def reciveEvent(self, chatid, summary, location):
        chatid = int(chatid)
        text = 'You have to go if you dont want to be late at this event:'
        requests.post(self._telegramAPIUrl + self._telegramAPIToken +'/sendMessage', json={"chat_id": chatid, "text": text})
        requests.post(self._telegramAPIUrl + self._telegramAPIToken +'/sendMessage', json={"chat_id": chatid, "text": summary})
        gMapsLink = 'https://www.google.it/maps/place/' + urllib.parse.quote_plus(location)
        requests.post(self._telegramAPIUrl + self._telegramAPIToken +'/sendMessage', json={"chat_id": chatid, "text": gMapsLink})
        return {'ok': True}
    
    def runPullMode(self):
        while True:
            self.getMesages()
            time.sleep(3)
