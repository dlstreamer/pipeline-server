#!/usr/bin/python3
'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import argparse
import os
from shutil import copyfile
import traceback
from vaserving.vaserving import VAServing

DEFAULT_SOURCE_URI = "https://github.com/intel/video-analytics-serving/raw/master/samples/bottle_detection.mp4"

def parse_args(args=None):
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--source",
                        action="store",
                        dest="source",
                        help="URI describing the source media to use as input.",
                        default=DEFAULT_SOURCE_URI)
    parser.add_argument("--destination",
                        action="store",
                        dest="destination",
                        help="address of MQTT broker listening for edgex inference results.",
                        default="edgex-mqtt-broker:1883")
    parser.add_argument("--edgexdevice",
                        action="store",
                        dest="edgexdevice",
                        help="Device name registered with edgex-device-mqtt.",
                        default="videoAnalytics-mqtt")
    parser.add_argument("--edgexcommand",
                        action="store",
                        dest="edgexcommand",
                        help="EdgeX command declared in the device profile.",
                        default="videoAnalyticsData")
    parser.add_argument("--edgexresource",
                        action="store",
                        dest="edgexresource",
                        help="EdgeX device resource declared in the device profile.",
                        default="videoAnalyticsData")
    parser.add_argument("--topic",
                        action="store",
                        dest="topic",
                        help="destination topic associated with EdgeX Core Data.",
                        default="objects_detected")
    parser.add_argument("--generate",
                        action="store_true",
                        dest="generate_profile",
                        help="Generate EdgeX device profile for device-mqtt.",
                        default=False)
    parser.add_argument("--analytics-image",
                        action="store",
                        dest="analyticsimage",
                        help="Analytics image to use for uService deployment to Docker compose.",
                        default="edgex-video-analytics-serving:0.5.0")
    if (isinstance(args, dict)):
        args = ["--{}={}".format(key, value)
                for key, value in args.items() if value]
    return parser.parse_args(args)

def print_args(args, program_name=__file__):
    heading = "Arguments for {}".format(program_name)
    banner = "="*len(heading)
    print(banner)
    print(heading)
    print(banner)
    for arg in vars(args):
        print("\t{} == {}".format(arg, getattr(args, arg)))
    print()

if __name__ == "__main__":
    args = parse_args()
    print_args(args, program_name=__file__)
    try:
        parameters = {"edgexbridge":{"topic":args.topic,
                                     "edgexdevice":args.edgexdevice,
                                     "edgexcommand":args.edgexcommand,
                                     "edgexresource":args.edgexresource,
                                     "analyticsimage":args.analyticsimage,
                                     "containername":args.analyticsimage.split(":", 1)[0],
                                     "source":args.source},
                      "inference-interval":6}

        # TODO: Add parameter to specify edgex folder
        out_folder = "/home/video-analytics-serving/samples/edgex_bridge/edgex/"
        compose_dest = os.path.abspath(os.path.join(out_folder, "docker-compose.override.yml"))
        if args.generate_profile:
            TEMPLATE = "name: \"{edgexdevice}\"\n" \
            "manufacturer: \"VideoAnalyticsServing\"\n"\
            "model: \"MQTT-2\"\n"\
            "description: \"Device profile for inference events published by Video Analytics "\
            "Serving over MQTT.\"\n"\
            "labels:\n"\
            "- \"MQTT\"\n"\
            "- \"VideoAnalyticsServing\"\n"\
            "\n"\
            "deviceResources:\n"\
            "- name: \"{edgexresource}\"\n"\
            "  description: \"Inference with one or more detections on an analyzed media "\
            "frame.\"\n"\
            "  properties:\n"\
            "    value:\n"\
            "      {{ type: \"String\", readWrite: \"R\", defaultValue: \"\"}}\n"\
            "    units:\n"\
            "      {{ type: \"String\", readWrite: \"R\", defaultValue: \"\"}}\n"\
            "\n"\
            "deviceCommands:\n"\
            "- name: \"{edgexcommand}\"\n"\
            "  get:\n"\
            "  - {{ operation: \"get\", object: \"{edgexresource}\", "\
            "parameter: \"{edgexresource}\" }}\n"\
            "\n"
            mqtt_folder = "res/device-mqtt-go/"
            output_path = os.path.abspath(
                os.path.join(out_folder,
                             mqtt_folder,
                             parameters["edgexbridge"]["edgexdevice"] + ".yml"))

            with open(output_path, 'w') as output_file:
                output_file.write(TEMPLATE.format(**parameters["edgexbridge"]))
                print("Generated EdgeX Device Profile:\n{}\n\n".format(output_path))

            DEVICE_LIST = "\n[[DeviceList]]\n"\
                "Name = '{edgexdevice}'\n"\
                "Profile = '{edgexdevice}'\n"\
                "Description = 'MQTT device that receives media analytics events.'\n"\
                "Labels = ['MQTT', 'VideoAnalyticsServing']\n"\
                "[DeviceList.Protocols]\n"\
                "  [DeviceList.Protocols.mqtt]\n"\
                "  Schema = 'tcp'\n"\
                "  Host = 'mqtt-broker'\n"\
                "  Port = '1883'\n"\
                "  ClientId = 'videoAnalytics-pub'\n"\
                "  Topic = 'videoAnalyticsTopic'\n"\
                "  User = ''\n"\
                "  Password = ''\n"
            config_source = os.path.abspath(os.path.join(out_folder,
                                                         mqtt_folder,
                                                         "configuration.toml.edgex"))
            config_dest = os.path.abspath(os.path.join(out_folder,
                                                       mqtt_folder,
                                                       "configuration.toml"))
            copyfile(config_source, config_dest)
            with open(config_dest, "a") as config_file:
                config_file.write(DEVICE_LIST.format(**parameters["edgexbridge"]))
                print("Appended to EdgeX configuration.toml:\n{}\n\n".format(config_dest))

            COMPOSE = "services:\n"\
                "  device-mqtt:\n"\
                "    environment:\n"\
                "      DRIVER_INCOMINGTOPIC: edgex_bridge/#\n"\
                "      DRIVER_INCOMINGCLIENTID: edgex-mqtt-sub\n"\
                "      DRIVER_RESPONSECLIENTID: edgex-mqtt-command-sub\n"\
                "      DRIVER_RESPONSETOPIC: Edgex-command-response\n"\
                "    volumes:\n"\
                "      - ./res/device-mqtt-go/:/res/\n\n"\
                "  vaserving:\n"\
                "    container_name: {containername}\n"\
                "    depends_on:\n"\
                "      device-mqtt:\n"\
                "        condition: service_started\n"\
                "      data:\n"\
                "        condition: service_started\n"\
                "      metadata:\n"\
                "        condition: service_started\n"\
                "    environment:\n"\
                "      CLIENTS_COMMAND_HOST: edgex-core-command\n"\
                "      CLIENTS_COREDATA_HOST: edgex-core-data\n"\
                "      CLIENTS_DATA_HOST: edgex-core-data\n"\
                "      CLIENTS_METADATA_HOST: edgex-core-metadata\n"\
                "      CLIENTS_NOTIFICATIONS_HOST: edgex-support-notifications\n"\
                "      CLIENTS_RULESENGINE_HOST: edgex-kuiper\n"\
                "      CLIENTS_SCHEDULER_HOST: edgex-support-scheduler\n"\
                "      CLIENTS_VIRTUALDEVICE_HOST: edgex-device-virtual\n"\
                "      DATABASES_PRIMARY_HOST: edgex-redis\n"\
                "      DRIVER_INCOMINGHOST: edgex-mqtt-broker\n"\
                "      DRIVER_RESPONSEHOST: edgex-mqtt-broker\n"\
                "      EDGEX_SECURITY_SECRET_STORE: 'false'\n"\
                "      REGISTRY_HOST: edgex-core-consul\n"\
                "      SERVICE_HOST: {containername}\n"\
                "      DISPLAY: $DISPLAY\n"\
                "    volumes:\n"\
                "      - /tmp/.X11-unix:/tmp/.X11-unix\n"\
                "    devices:\n"\
                "      - /dev/dri:/dev/dri\n"\
                "    hostname: {containername}\n"\
                "    image: {analyticsimage}\n"\
                "    command: \"--source={source} --topic={topic}\"\n" \
                "    user: vaserving\n"\
                "    networks:\n"\
                "      edgex-network: {{}}\n"\
                "    ports:\n"\
                "    - 127.0.0.1:8080:8080/tcp\n"\
                "    read_only: true\n"\
                "version: '3.7'\n\n"
            with open(compose_dest, 'w') as override_file:
                override_file.write(COMPOSE.format(**parameters["edgexbridge"]))
                print("Generated EdgeX Compose Override:\n{}\n\n".format(compose_dest))

        else:
            pipeline_name = "object_detection"
            pipeline_version = "edgex_event_emitter"
            VAServing.start({'log_level': 'INFO', "ignore_init_errors":False})
            pipeline = VAServing.pipeline(pipeline_name, pipeline_version)
            source = {"uri":args.source, "type":"uri"}
            destination = {"type":"mqtt",
                           "host":args.destination,
                           "topic":'edgex_bridge/'+args.topic}
            pipeline.start(source=source, destination=destination, parameters=parameters)
            start_time = None
            start_size = 0
            VAServing.wait()
    except FileNotFoundError:
        print("Did you forget to run ./samples/edgex_bridge/fetch_edgex.sh ?")
        print("Error processing script: {}".format(traceback.print_exc()))
    except KeyboardInterrupt:
        pass
    except Exception:
        print("Error processing script: {}".format(traceback.print_exc()))
    VAServing.stop()
