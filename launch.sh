#!/bin/bash
python3 GoogleOAuth2Interface/GoogleOAuth2Interface-main.py &
python3 TelegramInterface/TelegramInterface_main.py &
python3 BusinessLogic/BusinessLogic.py 
