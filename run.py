#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from aiohttp import web, BasicAuth, ClientSession, client_exceptions
from argparse import ArgumentParser
from os import path
from urllib.parse import parse_qs
from yajl import dumps, loads
import logging


config = dict()
version = dict()
routes = web.RouteTableDef()


@routes.get('/ping')
async def get_handler(request):
    return web.Response(text = 'Pong')


@routes.post('/{project}')
async def get_handler(request):
    username = None
    password = None

    project = request.match_info['project']
    if project not in config:
        return web.Response(text='Project now found', status=404)

    data = (await request.read()).decode('UTF-8')

    if not data:
        return web.HTTPBadRequest()

    try:
        data = parse_qs(data)
    except ValueError:
        return web.HTTPBadRequest()

    if 'username' in data:
        username = data['username'][0]

    if 'password' in data:
        password = data['password'][0]

    if not username or not password:
        return web.HTTPBadRequest()

    data = {'grant_type': 'password',
            'username': username,
            'password': password}

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    url = config[project]['keyrock']+'/oauth2/token'

    try:
        async with ClientSession() as session:
            async with session.post(url, auth=config[project]['auth'], data=data, headers=headers, timeout=0) as response:
                if response.status == 200:
                    return web.Response(text=loads(await response.text())['access_token'])
                else:
                    return web.Response(text="Keyrock reply: " + response.reason, status = response.status)
    except client_exceptions.ClientConnectorError:
        return web.HTTPBadGateway()


@routes.get('/version')
async def get_handler(request):
    return web.Response(text=version)


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('--ip', dest="ip", default='0.0.0.0', help='ip address (default: 0.0.0.0)', action="store")
    parser.add_argument('--port', dest="port", default=8080, help='port (default: 8080)', action="store")
    parser.add_argument('--config', dest='config_path', default='/opt/config.json',
                        help='path to config file (default: /opt/config.json)',  action="store")

    args = parser.parse_args()

    version_path = './version'
    if not path.isfile(version_path):
        logging.error('Version file not found')
        exit(1)
    try:
        with open(version_path) as f:
            version_file = f.read().split('\n')
            version['build'] = version_file[0]
            version['commit'] = version_file[1]
            version = dumps(version)
    except IndexError:
        logging.error('Unsupported version file type')
        exit(1)

    if not path.isfile(args.config_path):
        logging.error('Config file not found')
        exit(1)

    try:
        with open(args.config_path) as file:
            temp = loads(file.read())
    except ValueError:
        logging.error('Unsupported config type')
        exit(1)
    try:
        for element in temp['projects']:
            config[element['project']] = dict()
            config[element['project']]['keyrock'] = element['keyrock']
            config[element['project']]['auth'] = BasicAuth(element['client_id'], element['client_secret'])
    except KeyError:
        logging.error('Config is not correct')
        exit(1)

    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, host=args.ip, port=args.port)
