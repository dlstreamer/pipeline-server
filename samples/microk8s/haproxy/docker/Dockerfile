ARG BASE=haproxytech/haproxy-ubuntu:2.6
FROM $BASE

COPY ./generated/haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg
COPY ./generated/servers.map /usr/local/etc/haproxy/servers.map