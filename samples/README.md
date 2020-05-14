# Using Video Analytics Serving Sample Client

These steps walk you through how to launch the sample client that is included in the repository to exercise the VA Serving REST-API. 

1. Open two terminal windows.

In terminal window 1:

  2. Build the service container with sample pipelines:
     ```
     ~/video-analytics-serving$ ./docker/build.sh
     ```

  3. Run the container with the temp folder volume mounted to capture results.
     ```
     ~/video-analytics-serving$ ./docker/run.sh -v /tmp:/tmp --name vaserving
     ```

In terminal window 2:

  4. Launch a second container as an interactive session with the sample application volume mounted into the image (this is handled automatically by the run.sh script when given the --dev flag)
     ```
     ~/video-analytics-serving$ ./docker/run.sh --dev --name vaclient
     ```

  5. Invoke the sample python application
  
     ```
     # ./samples/sample.py --quiet
     ```

  6. Review the produced inferences. By default, these are saved to /tmp/results.txt.
     ```
     # tail /tmp/results.txt
     ```

  7. Run the pipeline multiple times to see runtime statistics on your system:
     ```
     # ./samples/sample.py --quiet --repeat 3 
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

  8. Explore running new pipelines, passing other sources, destination targets, and other options described in sample.py.
     ```
     # ./samples/sample.py --help
     ```

  9. Exit the interactive session and stop the service contianer.
  ```
	 # exit
	 # docker kill vaserving
  ```
