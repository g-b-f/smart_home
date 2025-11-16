bash start.sh
sleep 5
curl -q -X POST -H "Content-Type: application/json" -d '{"event":"sleep_tracking_started"}' http://192.168.1.117:5000/sleep | grep OK
