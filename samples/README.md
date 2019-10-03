## Using Video Analytics Serving Samples

These steps walk you through how to launch the sample application that is included within the built docker image. We show steps for using the GStreamer based image, but you will find that altering to run for FFmpeg is very similar.

1. Open two terminal windows.

In terminal window 1:

  2. Build the latest sources:
     ```
     ~/video-analytics-serving$ ./build.sh gstreamer
     ```

  3. Run the container. This launches the Video Analytics Serving service with GStreamer support:
     ```
     ~/video-analytics-serving$ ./run.sh gstreamer
     ```

In terminal window 2:

  4. Launch an interactive session to explore the sample application already located in the same container we ran in step 3:
     ```
     ~/video-analytics-serving$ docker exec -it -e http_proxy=$http_proxy -e https_proxy=$https_proxy -e no_proxy=$no_proxy -e FRAMEWORK=gstreamer video_analytics_serving_gstreamer /bin/bash
     ```

  5. Invoke the sample Python application.
     ```
     # cd /home/video-analytics/samples
     # python3 sample.py
     ```

  6. Review the produced inferences. By default, these are saved to ./results.txt.
     ```
     # more ./results.txt
     ```

  7. Run with multiple retries to calculate performance on your system:
     ```
     # ./sample.py --retries 3
     ```

     This time you will notice that the sample outputs calculated statistics upon completion. Ex:
     ```
     {
         "Average": 53.95606659806379,
         "Count": 3,
         "Max": 55.831869705475086,
         "Min": 52.22430268675434,
         "Variance": 3.2691954161506676,
         "value": "avg_fps"
     }
     {
         "Average": 4.637118577957153,
         "Count": 3,
         "Max": 4.787312269210815,
         "Min": 4.4779980182647705,
         "Variance": 0.023978593194669884,
         "value": "elapsed_time"
     }
     ```

    8. Explore passing other sources, destination targets, and other options described in sample.py.
       ```
       # ./sample.py --help
       ```

    9. Stop the container by typing `exit` and running the `stop.sh` script. Notice that this stops activities in both terminal windows.
        ```
        # exit
        $ ./stop.sh gstreamer
        ```
