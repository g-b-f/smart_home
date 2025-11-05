kill -s SIGINT $(pgrep python)
#kill -9 $(ps -A | grep python | awk '{print $1}')
rm nohup.out
echo '' >> log.txt
(nohup uv run app.py 2> /dev/null &)
