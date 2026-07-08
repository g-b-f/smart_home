kill -s SIGINT $(ps -A | grep python | awk '{print $1}')
echo '' >> log.txt
date >> log.txt
nohup uv run app.py &>> log.txt &
sleep 3 &&
tail log.txt
