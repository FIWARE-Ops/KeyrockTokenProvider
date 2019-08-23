![FIWARE Banner](https://nexus.lab.fiware.org/content/images/fiware-logo1.png)

# Keyrock Token Provider
[![Docker badge](https://img.shields.io/docker/pulls/fiware/service.keyrocktokenprovider.svg)](https://hub.docker.com/r/fiware/service.keyrocktokenprovider/)
[![Build Status](https://travis-ci.org/FIWARE-Ops/KeyrockTokenProvider.svg?branch=master)](https://travis-ci.org/FIWARE-Ops/KeyrockTokenProvider)

## Overview
This project is part of [FIWARE](https://fiware.org) OPS infrastructure.
It provides auth token from [Keyrock](https://fiware-idm.readthedocs.io/en/latest/) to communicate with software protected by [Wilma](https://fiware-pep-proxy.readthedocs.io/en/latest/).

## How to run
```console
$ docker run -it --rm \
             -p 0.0.0.0:${PORT}:${PORT} \
             fiware/service.idmtokenprovider \
             --ip 0.0.0.0 \
             --port ${PORT} \
             --config ${PATH_TO_CONFIG}
```
```console
$ curl http://localhost:${PORT}/ping
```
## How to configure
Sample config is located [here](./config.example.json).

## How to use
Ping
```console
$ curl http://localhost:${PORT}/ping
```
Get version
```console
$ curl http://localhost:${PORT}/version
```
Get token
```console
$ curl -XPOST -d "username=${USER}&password=${PASSWORD}" http://localhost:${PORT}/$PROJECT
```