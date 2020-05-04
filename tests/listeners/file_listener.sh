OUTPUT_PATH=./
OUTPUT_FILE=dlstreamer.json
OUTPUT_PATHFILE=${OUTPUT_PATH}${OUTPUT_FILE}

# Assure previous file does not exist.
# Note that default output format for file is batch to easily bulk import JSON.
if [ -f $OUTPUT_PATHFILE ]; then
   rm -f $OUTPUT_PATHFILE
   echo "Removed existing file: $OUTPUT_PATHFILE"
fi

echo "Waiting for DL Streamer to create output file: $OUTPUT_PATHFILE"
while read i; do if [ "$i" = $OUTPUT_FILE ]; then break; fi; done \
   < <(inotifywait  -e create,open --format '%f' --quiet $OUTPUT_PATH --monitor)

tail -f $OUTPUT_PATHFILE

