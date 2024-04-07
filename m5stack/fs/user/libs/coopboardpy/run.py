#! /usr/bin/env python
# -*- coding: utf-8 -*_
# Author: Liu Yang <mkliuyang@gmail.com>
import json

from coopboardpy.config import Cfg
from coopboardpy.decoder import get_decoder
from coopboardpy.driver import driver


class Runner:
    def main_loop(self):
        cfg = Cfg.from_dict(json.load(open('config/coop53.json')))
        driver.start(cfg)
        decoder = get_decoder(cfg)
        pressed_key_ids_cache = []
        try:
            while True:
                colors = cfg.light.get_color(cfg.keyboard, 0.1)
                driver.set_light(colors)
                # todo 这里目前比较粗糙，之后要做一更快的扫描缓存。
                pressed_key_ids = driver.scan_key()
                if pressed_key_ids != pressed_key_ids_cache:
                    keycodes4send = decoder.decode(pressed_key_ids)
                    driver.send_keycode(keycodes4send)
                    pressed_key_ids_cache = pressed_key_ids[:]
                driver.wait_us(50)
        except KeyboardInterrupt as e:
            driver.close(cfg)


if __name__ == '__main__':
    Runner().main_loop()

