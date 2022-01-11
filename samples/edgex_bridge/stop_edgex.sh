SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd $SCRIPT_DIR/edgex
edgex_request_rtsp_path="" edgex_env_enable_rtsp="false" edgex_rtsp_port=8554 docker-compose down

echo "NOTE: EdgeX data still persists in docker volumes."
echo "Call ./clear_edgex.sh to remove ALL persisted data"
echo "including service registrations, device profiles, events, ..."
