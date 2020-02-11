#!/bin/bash
python /GoogleOAuth2Interface\GoogleOAuth2Interface.py &
sleep 5
python /TelegramInterface\TelegramInterface.py &
sleep 5
python /BusinessLogic/BusinessLogic.py
