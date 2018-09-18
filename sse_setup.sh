#!/bin/bash


# TODO: Create status/check command


sudo apt update
sudo apt upgrade -y
sudo apt install python3-pip -y
pip3 install --upgrade pip
pip install -r requirements.txt
cp sse/scoring_engine/main.json.example1 sse/scoring_engine/main.json
