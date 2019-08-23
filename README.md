![FIWARE Banner](https://nexus.lab.fiware.org/content/images/fiware-logo1.png)

# Keyrock Token Provider
[![Docker badge](https://img.shields.io/docker/pulls/fiware/service.keyrocktokenprovider.svg)](https://hub.docker.com/r/fiware/service.keyrocktokenprovider/)

## Overview
This project is part of [FIWARE](https://fiware.org) OPS infrastructure.
It provides auth token from [FIWARE Keyrock](https://account.lab.fiware.org) to communicate with [Orion global instance](http://orion.lab.fiware.org:1026).
It works in pair with [token_script](https://raw.githubusercontent.com/fgalan/oauth2-example-orion-client/master/token_script.sh) provided as part of 
[Orion Context Broker](https://github.com/telefonicaid/fiware-orion) [QuickStart Guide](https://fiware-orion.readthedocs.io/en/master/quick_start_guide).

## How to run
```console
$ docker run -e CLIENT_ID=${CLIENT_ID} \
             -e CLIENT_SECRET=${CLIENT_SECRET} \
             -e IDM=${IDM} \
             -e ORION=${ORION} \
             -p 0.0.0.0:8000:8000 \
             fiware/service.idmtokenprovider \
             --ip ${IP} \
             --port ${PORT} \
             --threads ${THREADS} \
             --socks ${SOCKS}
```
```console
$ curl http://localhost:8000/ping
```

## How to configure
+ You should provide a valid values of CLIENT_ID, CLIENT_SECRET, IDM, ORION for communication with Keyrock.

## How to use
Ping
```console
$ curl http://localhost:8000/ping
```
Get version
```console
$ curl http://localhost:8000/version
```
Get token
```console
$ curl -s -d "{\"username\": \"$USER\", \"password\":\"$PASSWORD\"}" -H "Content-type: application/json" http://localhost:8000/token
```