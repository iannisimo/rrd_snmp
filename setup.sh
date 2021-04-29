#!/bin/bash

setup() {
    python3 -m venv .env
    # source .env/bin/activate
    .env/bin/pip install -r requirements.txt
}

clear() {
    rm -rf .env
    rm db.rrd
}

if [ $# -eq 0 ]; then
  echo "usage $0 [setup | clear]"
fi

case "$1" in
    "setup" )
        setup ;;
    "clear" )
        clear ;;
esac