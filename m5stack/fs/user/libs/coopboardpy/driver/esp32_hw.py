from .base import CoopBoardDriver
import coopboard
import random
import time

class Esp32HWDriver(CoopBoardDriver):
    def __init__(self) -> None:
        super().__init__()
        self.kc_map = {}


    def start(self, cfg: 'Cfg'):
        """启动钩子。在运行功能前调用的钩子"""
        self.cfg = cfg
        for k in cfg.keyboard.keys:
            self.kc_map[(k.r, k.c)] = k.gid
        coopboard.board_scan_init()

    def close(self, cfg):
        """结束钩子。停止运行"""
        pass

    # 下面是供给逻辑调用的底层函数。
    def scan_key(self) -> 'List[int]':
        ret = []
        for rc in coopboard.board_scan():
            key = tuple(rc)
            if key in self.kc_map:
                ret.append(self.kc_map[key])
        return ret

    def send_keycode(self, codes: 'List[SendCode]') -> None:
        code = codes[0]  # 目前先实现只能一个SendCode的6键码同时发送。
        coopboard.sendkey(0, code.ck, *code.k_list)

    def set_light(self, lights: 'List[Color]') -> None:
        # todo 
        pass

    def wait_us(self, n: int) -> None:
        time.sleep_us(n)

    def log(self, msg: str, level='info') -> None:
        print(f'[{level}] {msg}')

    def random(self) -> float:
        return random.random()
