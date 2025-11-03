kill $(pgrep python)
rm nohup.out
(nohup uv run app.py 2> /dev/null &)
