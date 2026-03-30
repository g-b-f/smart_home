log(){
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}

log "Device restarted"

until ping -c 1 8.8.8.8 &> /dev/null; do
  log "Waiting for network..."
  sleep 2
done

log "Network is up, starting server"

bash update && sudo disable-led
