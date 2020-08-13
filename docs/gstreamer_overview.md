# GStreamer Media Framework
## Background
[GStreamer](https://gstreamer.freedesktop.org/) is a pipeline-based multimedia framework that links together a wide variety of media processing systems to complete complex workflows.
For instance, GStreamer can be used to build a system that reads files in one format, processes them, and exports them in another.

GStreamer pipelines adhere to the [GStreamer Pipeline Description](https://gstreamer.freedesktop.org/documentation/tools/gst-launch.html?gi-language=c#pipeline-description) and
consist of an ordered sequence of [elements](https://gstreamer.freedesktop.org/documentation/application-development/basics/elements.html?gi-language=c), their [configuration properties](#properties), and connections are all specified as a list of strings separated by exclamation
marks (!). Internally the GStreamer library constructs a pipeline object that contains the individual elements and handles common operations such as clocking, messaging, and state changes.

**Example:** `gst-launch-1.0 videotestsrc ! ximagesink`

## Elements
An [element](https://gstreamer.freedesktop.org/documentation/application-development/basics/elements.html?gi-language=c) is the fundamental building block of a pipeline. 
Elements perform specific operations on incoming frames and then push the resulting frames 
downstream for further processing. Elements are linked together textually by exclamation marks (`!`) with the full chain of elements 
representing the entire pipeline. Each element will take data from its upstream element, process it and then output the data for further processing by the next element.

Elements designated as **source** elements provide input into the pipeline from external sources. Elements designated as **sink** elements represent the final stage of a pipeline. 
As an example a sink element could write transcoded frames to a file on the local disk or open a window to render the video content to the screen or even re-stream the content 
via [RTSP](https://tools.ietf.org/html/rfc2326). 

Object detection pipelines typically use the [decodebin](https://gstreamer.freedesktop.org/documentation/playback/decodebin.html#decodebin) utility element 
to construct a set of decode operations based on the given input format, decoder and demuxer elements available in the system. 
The next step in the pipeline is often color space conversion which is handled by the 
[videoconvert](https://gstreamer.freedesktop.org/documentation/videoconvert/index.html?gi-language=c#videoconvert) element. 

## Properties
Elements are configured using key-value pairs called properties. As an example the `filesrc` element has a property named `location` which specifies the file path for input.

**Example**:
 `filesrc location=cars_1900.mp4`

A list of properties supported by each element can be viewed using the command line tool `gst-inspect-1.0`. The tool also provides a property description and 
the valid range of values that can be set.
