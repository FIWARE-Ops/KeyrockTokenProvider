![FIWARE Banner](https://nexus.lab.fiware.org/content/images/fiware-logo1.png)

# Keyrock Token Provider
[![Docker badge](https://img.shields.io/docker/pulls/fiware/service.keyrocktokenprovider.svg)](https://hub.docker.com/r/fiware/service.keyrocktokenprovider/)
[![Build Status](https://travis-ci.org/FIWARE-Ops/KeyrockTokenProvider.svg?branch=master)](https://travis-ci.org/FIWARE-Ops/KeyrockTokenProvider)

## Overview
This project is part of [FIWARE](https://fiware.org) OPS infrastructure.
It provides auth token from [Keyrock](https://fiware-idm.readthedocs.io/en/latest/) to communicate with software protected by [Wilma](https://fiware-pep-proxy.readthedocs.io/en/latest/).

## How to run
```console
$ docker run -d \
             -p 8080:8080 \
             fiware/service.idmtokenprovider \
             --config ${PATH_TO_CONFIG}
```
```console
$ curl http://localhost:8080/ping
```
## How to configure
Sample config is located [here](./config.json.example).

## How to use
Ping
```console
$ curl http://localhost:8080/ping
```
Get version
```console
$ curl http://localhost:8080/version
```
Get token
```console
$ curl -XPOST -d "username=$USER&password=$PASSWORD" http://localhost:8080/$PROJECT
```