#!/bin/bash

kill $(ps aux | grep -i '[p]ython3 main.py' | awk '{print $2}')
cd discord-bot-exchange-rate
rm nohup.out
git pull
pip install -r requirements.txt
nohup python3 main.py &