'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import sys
import argparse
import json
import paho.mqtt.client as mqtt
import cv2

file_location = "host-file-location"
object_type = "vehicle"

def on_connect(client, user_data, _unused_flags, return_code):
    if return_code == 0:
        args = user_data
        print("Connected to broker at {}:{}".format(args.broker_address, args.broker_port))
        print("Subscribing to topic {}".format(args.topic))
        client.subscribe(args.topic)
    else:
        print("Error {} connecting to broker".format(return_code))
        sys.exit(1)

def on_message(_unused_client, user_data, msg):
    result = json.loads(msg.payload)
    if not "frame_id" in result:
        return
    objects = result.get("objects", [])
    for obj in objects:
        if obj["roi_type"] == object_type and obj["detection"]["confidence"] > 0.75:
            args = user_data
            frame_path = args.frame_store_template % result["frame_id"]
            print("Detected {}: frame_id = {}".format(object_type, result["frame_id"]))
            print("Frame path: {}".format(frame_path))
            image = cv2.imread(frame_path)
            cv2.imshow(object_type, image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            break

def get_arguments():
    """Process command line options"""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--topic',
                        action='store',
                        type=str,
                        default='pipeline-server',
                        help='Set MQTT topic')
    parser.add_argument('--broker-address',
                        action='store',
                        type=str,
                        default='localhost',
                        help='Set MQTT broker address')
    parser.add_argument('--broker-port',
                        action='store',
                        type=int,
                        default=1883,
                        help='Set MQTT broker port')
    parser.add_argument('--frame-store-template',
                        action='store',
                        type=str,
                        required=True,
                        help='Frame store file name template')
    return parser.parse_args()

if __name__ == "__main__":
    args = get_arguments()
    client = mqtt.Client("VA Serving Frame Retrieval", userdata=args)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(args.broker_address, args.broker_port)
    client.loop_forever()
