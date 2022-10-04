#!/bin/bash -e
#
# Copyright (C) 2019-2020 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#

if ! command -v openssl &> /dev/null
then
	echo "openssl could not be found, please install openssl e.g. apt install openssl"
	exit
fi

error() {
    printf '%s\n' "$1" >&2
    exit 1
}

if [ "$1" ]; then
	echo "This certificate should only be used for development purposes and not production use. It will expire in 1 day."
	mkdir -p $1/cert
	cd $1/cert
	openssl req -new -newkey rsa:4096 -x509 -sha256 -days 1 -nodes -out server.crt -keyout server.key \
		-subj "/C=US/ST=Oregon/L=Hillsboro/O=pipelineserver/OU=pipelineserver/CN=localhost"
	shift
else
	error 'ERROR: "generate_cert.sh" requires one argument for directory. e.g. ./generate_cert.sh <your_directory>'
fi

