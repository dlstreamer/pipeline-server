OUTPUT_PATHFILE=./dlstreamer.fifo
rm -f $OUTPUT_PATHFILE
mkfifo $OUTPUT_PATHFILE
echo "Waiting for DL Streamer to write lines to FIFO: $OUTPUT_PATHFILE"
tail -f $OUTPUT_PATHFILE
