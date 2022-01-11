read -r -p "This will DESTROY all EdgeX data and metadata. Are you sure? [y/N] " response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then
#    removes all persisted data, similar to:
#    docker volume rm edgex_consul-config edgex_consul-data edgex_db-data edgex_log-data
    cd ./edgex
    edgex_env_enable_rtsp="" edgex_request_rtsp_path="" edgex_rtsp_port=8554 docker-compose down --volumes
fi
