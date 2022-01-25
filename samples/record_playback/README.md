# Record/Playback Sample

This sample demonstrates how you can record video to the local filesystem and playback inference results without having to recalculate inference results.

## How It Works

The record_playback.py supports both 'record' and 'playback'

When recording, the only required parameter from the user is the input video source.

Defaults will be used for output video folder, output metadata file, max chunk size of recorded video

When doing playback, the app requires an input video source. To overlay metadata results, a metadata file needs to be passed in through the optional arguments

## Options

[ --record : Set the sample to record mode, record a video source into segments and collect inference results ]

[ --playback : Set the sample to playback mode, playback a recorded video and optionally display inference results ]

[ --input-video-path : (Required) Specify the input source for record or playback. Record does not support a directory as an input source ]

[ --metadata-file-path : (Record:Optional) (Playback:Required) Specify the metadata file path to record to or read for playback. In record mode, default is /tmp/metadata.txt ]

[ --output-video-folder : (Optional) (Record mode only) Specify the output directory for recorded video segments. Default is /tmp/video_output ]

[ --max-time : (Optional) (Record mode only) Specify the segment size based on time. Default is 2000000000 ns ]

## Running

To run the program, use `./docker/run.sh --dev` to enter a container with the appropriate environment.

To playback metadata on top of recordings, access to an Xdisplay is required. This will be dependent on your setup. For most people working in a GUI environment, this will be the value for $DISPLAY on the host

```
./docker/run.sh --dev -v $HOME/.Xauthority:/home/pipeline-server/.Xauthority
export DISPLAY=<X display you want to render to>
```

To Record

```sh
python3 ./samples/record_playback/record_playback.py --record --input-video-path <VIDEO_PATH> --metadata-file-path <METADATA_PATH> --output-video-folder <OUTPUT_FOLDER>
```

Recorded segments are stored in a `year/month/day` directory in the target folder. To playback recorded segments the full path to the folder containing the recorded segments must be provided

To Playback

```sh
python3 ./samples/record_playback/record_playback.py --playback --input-video-path <VIDEO_PATH> --metadata-file-path <METADATA_PATH>
```

For playback, VIDEO_PATH is OUTPUT_FOLDER/<year>/<month>/<day> where OUTPUT_FOLDER is the path specified during record

### Example Record
```sh
python3 ./samples/record_playback/record_playback.py --record --input-video-path /home/pipeline-server/samples/bottle_detection.mp4
```

### Example Playback on recorded segments (update input folder path year/month/day as appropriate)
```sh
python3 ./samples/record_playback/record_playback.py --playback --input-video-path /tmp/video_output/2021/1/1/ --metadata-file-path /tmp/metadata.txt
```

### Example Playback on original video
```sh
python3 ./samples/record_playback/record_playback.py --playback --input-video-path /home/pipeline-server/samples/bottle_detection.mp4 --metadata-file-path /tmp/metadata.txt
```

## The 'Playing back video that does not conform to unixtimestamp_pts filename, assuming metadata file and video file timestamps match' warning
Playback works on both the recorded chunks and the original video for matching up the metadata file. The recorded chunks are in `<unixtimestamp>_<pts>` name format to allow playback to know how to organize the recorded chunks, and if playing back a specific chunk how much to offset the presentations time (pts) to match up properly with the metadata

When playing back the metadata on the original video, this pts info is not available, and a warning is printed that the playback file name does not conform to that format, and playback will assume metadata file and video file timestamps match.

There won't be an issue unless attempting to playback metadata on a different video file.
