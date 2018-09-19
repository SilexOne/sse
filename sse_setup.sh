#!/bin/bash


# TODO: Create status/check command


sudo apt update
sudo apt upgrade -y
sudo apt install python3-pip -y
pip3 install --upgrade pip
pip install --user -r requirements.txt
# Use abs path
cp scoring_engine/main.json.example1 scoring_engine/main.json
