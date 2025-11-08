bash start.sh
sleep 10
curl -X POST -H "Content-Type: application/json" -d '{"event":"sleep_tracking_started"}' http://192.168.1.117:5000/sleep
echo $?