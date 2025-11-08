# kill -s SIGINT $(pgrep python)
kill -s SIGINT $(ps -A | grep python | awk '{print $1}')
rm nohup.out
echo '' >> log.txt
(nohup uv run app.py >> log.txt &)
