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

def parse_args(args=None):
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--source",
                        action="store",
                        dest="source",
                        help="URI describing the source media to use as input.",
                        default="file:///home/video-analytics-serving/samples/classroom.mp4")
    parser.add_argument("--destination",
                        action="store",
                        dest="destination",
                        help="address of MQTT broker listening for edgex inference results.",
                        default="localhost:1883")
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
                        help="destination topic associated with EdgeX Core Data",
                        default="objects_detected")
    parser.add_argument("--generate",
                        action="store_true",
                        dest="generate_profile",
                        help="Generate EdgeX device profile for device-mqtt.",
                        default=False)
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
                                     "edgexresource":args.edgexresource}}

        # TODO: Add parameter to specify edgex folder
        out_folder = "/home/video-analytics-serving/edgex/"
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
                "  Host = 'localhost'\n"\
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
                "      - ./res/device-mqtt-go/:/res/\n"\
                "version: '3.7'"
            with open(compose_dest, 'w') as override_file:
                override_file.write(COMPOSE.format(**parameters["edgexbridge"]))
                print("Generated EdgeX Compose Override:\n{}\n\n".format(compose_dest))

        else:
            # Raise error if compose override does not exist, expecting the generation to
            # complete at least once.
            if os.path.isfile(compose_dest):
                pipeline_name = "object_detection"
                pipeline_version = "edgex"
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
            else:
                print("ERROR: Invoke edgex_bridge.py with '--generate' to prepare EdgeX Foundry.")
    except KeyboardInterrupt:
        pass
    except Exception:
        print("Error processing script: {}".format(traceback.print_exc()))
    VAServing.stop()
