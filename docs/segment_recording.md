# Segment Recording
One potential use case is the ability to save the video that is sent through a pipeline

Object Detection/2 is a version of the Object Detection pipeline that adds a segment recording feature

The pipeline will perform inference as usual, but will at the same time save the input video to a specified directory passed in through parameters in the request

Parameters needs to have a property called 'recording_prefix' to specify the output directory of the video segments

Videos are saved in a (<recording_prefix>)yyyy/mm/dd/ directory

Videos have the following naming convention
<Unix_timestamp>_<PTS>.mp4

### Example Request:
```json
{
	"source": {
		"uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true",
		"type": "uri"
	},
	"destination": {
		"type": "file",
		"path": "/tmp/results.txt",
		"format": "json-lines"
	},
	"parameters":{
		"recording_prefix": "/tmp/bottle"
	}
}
```
