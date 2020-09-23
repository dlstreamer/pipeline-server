# Record/Playback Sample

This sample demonstrates how you can record video to the local filesystem and playback inference results without having to recalculate inference results.

## How It Works

The record_playback_app.py supports both 'record' and 'playback'

When recording, the only required parameter from the user is the input video source. 

Defaults will be used for output video folder, output metadata file, max chunk size of recorded video

When doing playback, the app requires an input video source. To overlay metadata results, a metadata file needs to be passed in through the optional arguments

## Options

[ --record : Set the sample to record mode, record a video source into segments and collect inference results ]
[ --playback : Set the sample to playback mode, playback a recorded video and optionally display inference results ]
[ --input-video-path : (Required) Specify the input source for record or playback. Record does not support a directory as an input source ]
[] --metadata-file-path : (Optional) Specify the metadata file path to record to or read for playback. In record mode, default is metadata.txt ]
[ --output-video-folder : (Optional) (Record mode only) Specify the output directory for recorded video segments. Default is the current directory ]
[ --max-time : (Optional) (Record mode only) Specify the segment size based on time. Default is 2000000000 ns ] 

## Running

To Record

```sh
python3 record_playback_app_va_serving.py --record --input-video-path <VIDEO_PATH> --metadata-file-path <METADATA_PATH>
```

To Playback

Playback
```sh
python3 record_playback_app_va_serving.py --playback --input-video-path <VIDEO_PATH> --metadata-file-path <METADATA_PATH>
```

## Example
```sh
python3 record_playback_app.py --record --input-video-path /home/video-analytics-serving/samples/bottle_detection.mp4

python3 record_playback_app.py --playback --input-video-path /home/video-analytics-serving/samples/bottle_detection.mp4 --metadata-file-path /home/video-analytics-serving/samples/record_playback/metadata.txt
```

