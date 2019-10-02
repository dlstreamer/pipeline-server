## Using Video Analytics Serving Samples

These steps walk you through how to launch the sample application that is included within the built docker image. We show steps for using the GStreamer based image, but you will find that altering to run for FFmpeg is very similar.

1. Build latest sources:
   ```
   ~/video-analytics-serving$ **build.sh**
   ```

2. Launch an interactive docker session, overriding the default entrypoint for the container:
   ```
   docker run -it -e http_proxy=$http_proxy -e https_proxy=$https_proxy -e no_proxy=$no_proxy \
   -it -p 8080:8080 -v /tmp:/tmp --name video_analytics_serving_gstreamer --rm \
   --entrypoint /bin/bash video_analytics_serving_gstreamer:latest
   ```

3. Within the container launch the Video Analytics Serving service:
   ```
   # ./docker-entrypoint.sh &
   # (press Enter to return to terminal prompt)
   ```

4. Launch the sample Python application.
   ```
   # cd /home/video-analytics/samples
   # python3 sample.py
   ```

5. Review the produced inferences. By default, these are saved to ./results.txt.
   ```
   # more ./results.txt
   ```

6. Run multiple times to calculate performance on your system:
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

7. Explore passing other sources, destination targets, and other options described in sample.py.
   '''
   \# **./sample.py --help**
   '''
