#
# Copyright (C) 2022 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#
FROM grafana/grafana:7.3.4
USER root
RUN grafana-cli --pluginsDir "/var/lib/grafana/plugins" plugins install ryantxu-ajax-panel
RUN grafana-cli --pluginsDir "/var/lib/grafana/plugins" plugins install yesoreyeram-infinity-datasource

COPY ./conf/datasources/datasources.yml /etc/grafana/provisioning/datasources/datasources.yml
COPY ./conf/dashboards/dashboards.yml /etc/grafana/provisioning/dashboards/dashboards.yml
COPY ./content/http-stream-dashboard.json /var/lib/grafana/dashboards/http-stream-dashboard.json 

USER grafana
