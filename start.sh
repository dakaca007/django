#!/bin/bash

cd /var/www/html/flaskapp && python3 app.py &
# 以appuser用户启动GoTTY
su - root -c "gotty --permit-write --port 3000 bash" &