#!/bin/bash


# TODO: Create status/check command
check_command(){
    eval $@
    LAST_RETURN_CODE=$?
    if [ $LAST_RETURN_CODE != 0 ]; then
        echo "$@ exited with return code $LAST_RETURN_CODE" >&2
        exit $LAST_RETURN_CODE
    fi
}

sudo apt update
sudo apt upgrade -y
sudo apt install python3-pip -y
pip3 install --upgrade pip
pip install --user -r requirements.txt
# Use abs path
cp scoring_engine/main.json.example1 scoring_engine/main.json
