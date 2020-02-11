import os.path
import requests
import datetime
import json

import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from flask import make_response

class GoogleOAuth2Interface():
    def __init__(self):
        self._host  = 'http://127.0.0.1:5001' #Url to myself
        self._telegramInterfaceUrl = 'http://127.0.0.1:5000'
        self._apipsw = 'placeholder'

        with open('settings.json') as json_file:
            data = json.load(json_file)
            self._host = data.get('host')
            self._telegramInterfaceUrl = data.get('telegramInterfaceUrl')
            self._apipsw = data.get('apipsw')

        self._oauth2callbackAdress = '/oauth2callback'
        self._scopes = ['https://www.googleapis.com/auth/calendar.readonly']
        self._creds = {}
        self._openFlow = {}
    
    def login(self, chatID, apipsw):
        print(apipsw)
        print('banana')
        print(self._apipsw)
        chatID = int(chatID)
        creds = None
        
        if not (self._apipsw == apipsw):
            return {}

        if chatID in self._creds:
            creds = self._creds[chatID]
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                self._creds[chatID] = creds
                return {'login-completed':'true', 'message':'Login refreshed!'}
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self._scopes)
                flow.redirect_uri = self._host  + self._oauth2callbackAdress
                authorization_url, state = flow.authorization_url()
                self._openFlow[state] = (flow, chatID)
                return {'login-completed':'false', 'message':'Please log in at the following link:', 'link': authorization_url}
        else:
            return {'login-completed':'true', 'message':'You are alreay loged in!'}
    
    def oauth2Callback(self, state, token):
        headers = {'Content-Type': 'text/html'}
        if state in self._openFlow:
            flow, chatID = self._openFlow.pop(state)
            flow.fetch_token(code=token)
            self._creds[chatID] = flow.credentials
            #request login success
            self.__sendSucessfulLoginNotification(chatID)
            return make_response('<html><head><title>Sucessful Login</title></head><body><div align=”center”>You have successfully logged in to your Google Acccount!</div><div align=”center”>Please close this window!</div></body></html>',200,headers)
        else:
            return make_response('<html><head><title>Benvenuto</title></head><body><div align=”center”>Invalid request!</div></body></html>',200,headers)
    
    def __sendSucessfulLoginNotification(self, chatID):
        requests.get(self._telegramInterfaceUrl + '/sucessfulLogin?chatid=' + str(chatID))

    def getCredentials(self, chatID, apipsw):
        if not (self._apipsw == apipsw):
            return {}
        chatID = int(chatID)
        if chatID in self._creds:
            creds = self._creds[chatID]
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                self._creds[chatID] = creds
            return {'ok': True, 'token': self._creds[chatID].token}
        else:
            return {'ok': False}
