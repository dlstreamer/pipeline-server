FROM video_analytics_serving_gstreamer_base

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    libgirepository-1.0-1 \
    python3-kafka \
    python3-kazoo \
    python3-requests \
    python3-tornado \
    && rm -rf /var/lib/apt/lists/*; fi

COPY ./service/app/server/requirements.txt /
RUN pip3 install  --no-cache-dir -r /requirements.txt
COPY ./samples /home/video-analytics/samples
COPY ./service/app /home/video-analytics/app
COPY ./models/ /home/video-analytics/models/
COPY ./pipelines /home/video-analytics/pipelines
COPY   docker-entrypoint.sh /home/video-analytics/

WORKDIR /home/video-analytics

ENTRYPOINT ["./docker-entrypoint.sh"]
