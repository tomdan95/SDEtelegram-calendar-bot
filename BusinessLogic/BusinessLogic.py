import requests
import time
import urllib
import json
from datetime import datetime, timedelta

class BusinessLogic():
    def __init__(self):
        self._googleOAuth2InterfaceUrl = 'http://127.0.0.1:5001'
        self._telegramInterfaceUrl = 'http://127.0.0.1:5000'
        self._mapQestToken = 'placeholder'
        self._googleOAuth2Interface_apipsw = 'placeholder'
        self._telegramWebHooksMode = False

        with open('settings.json') as json_file:
            data = json.load(json_file)
            self._googleOAuth2InterfaceUrl = data.get('googleOAuth2InterfaceUrl')
            self._telegramInterfaceUrl = data.get('telegramInterfaceUrl')
            self._mapQestToken = data.get('mapQestToken')
            self._googleOAuth2Interface_apipsw = data.get('apipsw')
            self._telegramWebHooksMode = data.get('telegramWebHooksMode', False)

        self._alreadyNotificated = {}
    
    def __getEvents(self, chatid):
        token = self.__getCredential(chatid)
        if not token:
            return None
        now = datetime.utcnow().isoformat() + '-01:00' # '-01:00' indicates Rome time offset
        end = (datetime.utcnow() + timedelta(hours=8)).isoformat() + '-01:00' # '-01:00' indicates Rome time offset
        param = token + '&singleEvents=True&orderBy=startTime&timeMin=' + now + '&timeMax=' + end
        request_json = requests.get('https://www.googleapis.com/calendar/v3/calendars/primary/events?access_token=' + param).json()
        for event in request_json.get('items', []):
            self.__parseEvent(event, chatid)

    def __parseEvent(self, event, chatid):
        eventid = event['id']
        start = datetime.fromisoformat(event['start']['dateTime']).replace(tzinfo=None)
        location = event.get('location')
        summary = event.get('summary', 'Event without Name')
        currentPosition = self.__getPosition(chatid)
        now = datetime.utcnow() + timedelta(hours=1) #Rome time offset
        travelTime = self.__getTravelTime(currentPosition, location)
        if ((start-now).seconds - travelTime) <= (10*60):
            if chatid in self._alreadyNotificated:
                if eventid in self._alreadyNotificated[chatid]:
                    return None
                else:
                    self._alreadyNotificated[chatid].add(eventid)
            else:
                self._alreadyNotificated[chatid] = set()
                self._alreadyNotificated[chatid].add(eventid)
            self.__sendEventNotification(chatid, summary, location)


    def __getActiveChat(self):
        return requests.get(self._telegramInterfaceUrl + '/getActiveChats').json().get('items', [])

    def __getPosition(self, chatid):
        request_json = requests.get(self._telegramInterfaceUrl + '/getPosition?chatid=' + str(chatid)).json()
        return (request_json.get('latitude'), request_json.get('longitude'))

    def __sendEventNotification(self, chatid, summary, location):
        if location:
            requests.post(self._telegramInterfaceUrl + '/reciveEvent', json={'chatid': chatid, 'summary': summary, 'location': location})
        else:
            requests.post(self._telegramInterfaceUrl + '/reciveEvent', json={'chatid': chatid, 'summary': summary})

    def __getCredential(self, chatid):
        return  requests.get(self._googleOAuth2InterfaceUrl + '/getCredentials?chatid=' + str(chatid) + '&apipsw=' + str(self._googleOAuth2Interface_apipsw)).json().get('token')
    
    def __getTravelTime(self, start, end):
        if not end:
            return 0
        par = 'key=' + self._mapQestToken + '&from=' + urllib.parse.quote_plus(str(start[0]) + ',' + str(start[1])) + '&to=' + urllib.parse.quote_plus(end)
        response_json = requests.get('https://www.mapquestapi.com/directions/v2/route?'+ par + '&outFormat=json&ambiguities=ignore&routeType=fastest&doReverseGeocode=false&enhancedNarrative=false&avoidTimedConditions=false').json()
        time = response_json.get('route', {}).get('time', 0)
        time = int(time)
        return time
    
    def __updateMessages(self):
        requests.get(self._telegramInterfaceUrl + '/updateMessages')

    def __runTelegramWebhooksMode(self):
        wait = 15
        while True:
            activeChat = self.__getActiveChat()
            for chatid in activeChat:
                self.__getEvents(int(chatid))
            time.sleep(wait)
    
    def __runTelegramWebhooksLessMode(self):
        waitTelegram = 1
        waitGcalendar = int(15 / waitTelegram)
        while True:
            for _ in range(waitGcalendar):
                #update telegram message
                self.__updateMessages()
                time.sleep(waitTelegram)
            activeChat = self.__getActiveChat()
            for chatid in activeChat:
                self.__getEvents(int(chatid)) 
    
    def run(self):
        if self._telegramWebHooksMode:
            self.__runTelegramWebhooksMode()
        else:
            self.__runTelegramWebhooksLessMode()

if __name__ == '__main__':
    blg = BusinessLogic()
    blg.run()