kill $(pgrep python)
rm nohup.out
nohup uv run app.py &
