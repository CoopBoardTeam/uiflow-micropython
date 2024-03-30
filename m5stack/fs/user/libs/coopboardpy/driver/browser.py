
"""
使用python架设的浏览器模拟后端。
* 使用chrome或火狐。
"""
import json
import random
import time
from flask import Response, jsonify
import logging

from socket_station import SocketStation

from .base import CoopBoardDriver


logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] %(asctime)s.%(msecs)03d: %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S')

log_level_mapping = logging.getLevelNamesMapping()


class Browser(CoopBoardDriver):
    def __init__(self):
        self.key_cache = []  # 用于记录远程传回的key的值
        self.socket = SocketStation(9999)
        self.socket.app.static_folder = '../coopboard/static'

    def start(self, cfg):
        # will emit
        self.socket.bind('set_light')
        self.socket.bind('new_code')

        @self.socket.bind('set_key_down')
        def set_key(key_down):
            self.key_cache = key_down
            self.log(f'key update to {self.key_cache}')

        # normal http get
        @self.socket.route('/hello')
        def hello_world():
            return Response("Hello, World!")

        @self.socket.route('/index')
        def send_index():
            return self.socket.app.send_static_file('index.html')

        @self.socket.route('/static/<path:path>')
        def send_static(path):
            return self.socket.app.send_static_file(path)

        @self.socket.route('/get_board')
        def get_board():
            return jsonify(cfg.keyboard.to_dict())

        self.socket.serve()
        self.log(f'server start at 127.0.0.1:{9999}. open http://127.0.0.1:{9999}/index to interact.')

    def close(self, cfg):
        self.socket.stop()

    def scan_key(self) -> 'List[int]':
        return self.key_cache

    def send_keycode(self, codes: 'List[SendCode]') -> None:
        for code in codes:
            self.socket.emit('new_code', code.to_dict())

    def set_light(self, lights: 'List[Color]') -> None:
        self.socket.emit('set_light', [(int(c.r * 256), int(c.g * 256), int(c.b * 256)) for c in lights])

    def wait_us(self, n: int) -> None:
        time.sleep(n * 1e-6)

    def log(self, msg: str, level='INFO') -> None:
        logging.log(log_level_mapping.get(level, logging.DEBUG), msg)

    def random(self) -> float:
        return random.random()


