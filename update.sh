cd smart_home &&
git reset --hard origin/master &&
git pull --force &&
bash start.sh &&
sleep 5 &&
tail log.txt 
