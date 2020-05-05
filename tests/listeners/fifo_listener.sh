OUTPUT_PATHFILE=./vaserving.fifo
rm -f $OUTPUT_PATHFILE
mkfifo $OUTPUT_PATHFILE
echo "Waiting for VA Serving to write lines to FIFO: $OUTPUT_PATHFILE"
tail -f $OUTPUT_PATHFILE
