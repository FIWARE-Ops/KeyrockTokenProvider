#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import json as jsn
import socket
import threading
import http.server
import requests
import os
import sys
import datetime
import argparse
from urllib.parse import parse_qs


def get_credentials(body):
    if 'username' in body:
        user = body['username'][0]
    else:
        return False, False

    if 'password' in body:
        password = body['password'][0]
    else:
        return False, False

    return user, password
    

def parse_request_line(request_line):
    request_line = request_line.split('HTTP')[0].strip()
    method = request_line.split('/')[0].strip()
    cmd = request_line.split('/')[1].strip().split('?')[0]

    if method == 'GET' and cmd in cmd_get:
        return cmd
    if method == 'POST' and cmd in cmd_post or cmd:
        return cmd

    return False


class Handler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        cmd = parse_request_line(self.requestline)
        if not cmd:
            message = {'message': 'Request not found'}
            self.reply(message, code=404)
            return

        if cmd == 'ping':
            message = {'message': 'Pong'}
            self.reply(message, silent=True, cmd=cmd)
            return

        if cmd == 'version':
            message = {'message': version}
            self.reply(message, cmd=cmd)
            return

    def do_POST(self):
        project = parse_request_line(self.requestline)
        if not project:
            message = {'message': 'Request not found'}
            self.reply(message, code=404)
            return

        if project in config:
            content_length = int(self.headers.get('content-length'))

            if content_length == 0:
                message = {'message': 'Length Required'}
                self.reply(message, code=411, cmd=project)
                return

            body = self.rfile.read(content_length).decode('utf-8')

            try:
                body = parse_qs(body)
            except ValueError:
                message = {'message': 'Unsupported media type'}
                self.reply(message, code=400, cmd=project)
                return

            user, password = get_credentials(body)

            if not user or not password:
                message = {'message': 'Missing username or password', 'cmd': project}
                self.reply(message, code=400)
                return

            payload = {'grant_type': 'password',
                       'username': user,
                       'password': password}

            url = config[project]['keyrock']+'/oauth2/token'
            try:
                resp = requests.post(url, auth=config[project]['auth'], data=payload, headers=headers, timeout=5)
            except requests.exceptions.ConnectionError:
                self.reply({'message': 'Keyrock request timeout'}, code=408, cmd=project)
                return
            reply = jsn.loads(resp.text)
            if resp.status_code == 200:
                if 'access_token' in reply:
                    self.reply({'message': reply['access_token']}, cmd=project)
                    return
            elif resp.status_code == 500:
                if 'statusCode' in reply:
                    if reply['statusCode'] == 400:
                        self.reply({'message': 'Invalid username or password'}, code=401, cmd=project)
                        return
            self.reply({'message': 'Keyrock Bad request'}, code=resp.status_code, cmd=project)
            return
        else:
            self.reply({'message': 'Project not found'}, code=404, cmd=project)
        return

    def log_message(self, format, *args):
        return

    def reply(self, message=None, silent=False, code=200, cmd=None):
        self.send_response(code)
        if cmd in cmd_get:
            self.send_header('content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(jsn.dumps(message, indent=2) + '\n', 'utf8'))
        else:
            self.send_header('content-type', 'application/x-www-form-urlencoded')
            self.end_headers()
            self.wfile.write(bytes(message['message'] + '\n', 'utf8'))

        if not silent:
            message['code'] = code
            if self.headers.get('X-Real-IP'):
                message['ip'] = self.headers.get('X-Real-IP')
            else:
                message['ip'] = self.client_address[0]
            message['request'] = self.requestline
            message['date'] = datetime.datetime.now().isoformat()
            if cmd:
                message['cmd'] = cmd
            print(jsn.dumps(message, indent=2))
        return


class Thread(threading.Thread):
    def __init__(self, i):
        threading.Thread.__init__(self)
        self.i = i
        self.daemon = True
        self.start()

    def run(self):
        httpd = http.server.HTTPServer(address, Handler, False)

        httpd.socket = sock
        httpd.server_bind = self.server_close = lambda self: None

        httpd.serve_forever()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', dest="ip", default='0.0.0.0', help='ip address (default: 0.0.0.0)', action="store")
    parser.add_argument('--port', dest="port", default=8000, help='port (default: 8000)', action="store")
    parser.add_argument('--threads', dest='threads', default=10, help='threads to start (default: 10)',
                        action="store")
    parser.add_argument('--socks', dest='socks', default=5, help='threads to start (default: 5)',  action="store")
    parser.add_argument('--config', dest='config_path', default='/opt/config.json',
                        help='path to config file (default: /opt/config.json)',  action="store")
    args = parser.parse_args()

    address = (args.ip, args.port)
    version_path = os.path.split(os.path.abspath(__file__))[0] + '/version'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    cmd_get = ['ping', 'version']
    cmd_post = ['token']

    version = dict()
    if not os.path.isfile(version_path):
        print(jsn.dumps({'message': 'Version file not found', 'code': 500, 'cmd': 'start'}, indent=2))
        version_file = None
        sys.exit(1)
    try:
        with open(version_path) as f:
            version_file = f.read().split('\n')
            version['build'] = version_file[0]
            version['commit'] = version_file[1]
    except IndexError:
        print(jsn.dumps({'message': 'Unsupported version file type', 'code': 500, 'cmd': 'start'}, indent=2))
        sys.exit(1)

    config=dict()
    if not os.path.isfile(args.config_path):
        print(jsn.dumps({'message': 'Config file not found', 'code': 500, 'cmd': 'start'}, indent=2))
        config_file = None
        sys.exit(1)

    try:
        with open(args.config_path) as file:
            temp = jsn.load(file)
    except ValueError:
        print(jsn.dumps({'message': 'Unsupported config type', 'code': 500, 'cmd': 'start'}, indent=2))
        sys.exit(1)
    try:
        for element in temp:
            config[element['project']] = dict()
            config[element['project']]['keyrock'] = element['keyrock']
            config[element['project']]['auth'] = requests.auth.HTTPBasicAuth(element['client_id'], element['client_secret'])
    except KeyError:
        print(jsn.dumps({'message': 'Config is not correct', 'code': 500, 'cmd': 'start'}, indent=2))
        sys.exit(1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(args.socks)

    [Thread(i) for i in range(args.threads)]

    print(jsn.dumps({'message': 'Service started', 'code': 200}, indent=2))

    while True:
        time.sleep(9999)
