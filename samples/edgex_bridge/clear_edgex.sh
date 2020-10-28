read -r -p "This will DESTROY all EdgeX data and metadata. Are you sure? [y/N] " response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    docker volume rm edgex_consul-config edgex_consul-data edgex_db-data edgex_log-data
fi
