#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from aiohttp import web, BasicAuth, ClientSession, ClientConnectorError
from argparse import ArgumentParser
from asyncio import TimeoutError, set_event_loop_policy
from logging import error, getLogger
from os import path
from urllib.parse import parse_qs
from uvloop import EventLoopPolicy
from yajl import dumps, loads


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
        return web.Response(text='Credentials are required', status=400)

    try:
        data = parse_qs(data)
    except ValueError:
        return web.Response(text='Wrong credentials format', status=400)

    if 'username' in data:
        username = data['username'][0]

    if 'password' in data:
        password = data['password'][0]

    if not username or not password:
        return web.Response(text='Username or password are not defined ', status=400)

    data = {'grant_type': 'password',
            'username': username,
            'password': password}

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    url = config[project]['keyrock']+'/oauth2/token'

    async with ClientSession() as session:
        try:
            auth = config[project]['auth']
            timeout = config[project]['timeout']
            async with session.post(url, auth=auth, data=data, headers=headers, timeout=timeout) as response:
                status = response.status
                text = loads(await response.text())
        except ClientConnectorError:
            web.Response(text='Token request failed due to the connection problem', status=502)
        except TimeoutError:
            web.Response(text='Token request failed due to the timeout', status=504)
        except Exception as exception:
            error('request_token, %s, %s, %s', status, text, exception)
            return web.HTTPInternalServerError()

        if status == 200:
            return web.Response(text=loads(text)['access_token'])
        else:
            if 'message' in text['error']:
                text = text['error']['message']
            else:
                text = text['error']
            return web.Response(text="Token request failed due to the: " + text, status = status)


@routes.get('/version')
async def get_handler(request):
    return web.Response(text=version)


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('--ip', default='0.0.0.0', help='ip to use, default is 0.0.0.0')
    parser.add_argument('--port', default=8080, help="port to use, default is 8080")
    parser.add_argument('--config', default='/opt/config.json', help='path to config file, default is /opt/config.json')

    args = parser.parse_args()

    getLogger().setLevel(40)
    set_event_loop_policy(EventLoopPolicy())

    version_path = './version'
    if not path.isfile(version_path):
        error('Version file not found')
        exit(1)
    try:
        with open(version_path) as f:
            version_file = f.read().split('\n')
            version['build'] = version_file[0]
            version['commit'] = version_file[1]
            version = dumps(version)
    except IndexError:
        error('Unsupported version file type')
        exit(1)

    if not path.isfile(args.config):
        error('Config file not found')
        exit(1)

    try:
        with open(args.config) as file:
            temp = loads(file.read())
    except ValueError:
        error('Unsupported config type')
        exit(1)
    try:
        for element in temp['projects']:
            config[element['project']] = dict()
            config[element['project']]['keyrock'] = element['keyrock']
            config[element['project']]['auth'] = BasicAuth(element['client_id'], element['client_secret'])

            if 'timeout' in config[element['project']]:
                config[element['project']]['timeout'] = element['timeout']
            else:
                config[element['project']]['timeout'] = None

    except KeyError:
        error('Config is not correct')
        exit(1)

    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, host=args.ip, port=args.port)
