#! /usr/bin/env python
# -*- coding: utf-8 -*_
# Author: Liu Yang <mkliuyang@gmail.com>
from coopboardpy.config import Cfg
from coopboardpy.event import event
from coopboardpy.structs.code import SendCode, Code, KeyCode, FnCode, Micro, EventCode


class Decoder:
    def __init__(self, cfg: Cfg):
        self.cfg = cfg

    def decode(self, key_ids: 'List[int]') -> 'List[SendCode]':
        raise NotImplementedError()


class SimpleDecoder(Decoder):
    """用于测试，只会返回第一层设置的键码。"""
    def __init__(self, cfg: Cfg):
        super().__init__(cfg)
        self.layer0: "list[Code]" = []
        for kc_line in self.cfg.code_map.m[0]:
            self.layer0.extend(kc_line)

    def decode(self, key_ids: 'list[int]') -> 'list[SendCode]':
        ret = []
        for id in key_ids:
            if isinstance(self.layer0[id], KeyCode):
                ret.append(SendCode(ck=self.layer0[id].ck, k_list=[self.layer0[id].k]))

        if len(ret) == 0:
            ret.append(SendCode())
        return ret


def combinations(arr, n, start_id=0, ret=None):
    """从arr中筛选出n个元素的所有组合。注意，为了速度考虑，不要在外面修改返回值。优先选靠前的元素。"""
    if ret is None:
        ret = []
    if len(arr) - start_id >= n - len(ret):  # 只有剩余项多于剩余应补充的项目，才能加入。
        ret.append(arr[start_id])
        if len(ret) == n:
            yield ret
        else:
            yield from combinations(arr, n, start_id + 1, ret)
        ret.pop()
        yield from combinations(arr, n, start_id + 1, ret)


def every_combinations(arr):
    yield arr   # 多数情况有键码，快速直接返回所有按键版本
    for i in range(len(arr) - 1, 0, -1):
        yield from combinations(arr, i)
    if len(arr):
        yield []  # 取0个组合


class AutoFitDecoder(Decoder):
    """自动适配解码器。
    1. 解决Fn升层和自动降层。
    2. 解决composite key的组合问题。
    """
    def __init__(self, cfg: Cfg):
        super().__init__(cfg)
        self.layers = {}
        self.fks: 'dict[int, FnCode]' = {}   # 键id到fn key。fn key 需要单独处理，提前检测。
        for layer_id, layer in self.cfg.code_map.m.items():
            self.layers[layer_id] = []
            for k in cfg.keyboard.keys:
                keycode = layer[k.r][k.c] if k.r < len(layer) and k.c < len(layer[k.r]) else None
                if isinstance(keycode, FnCode):
                    self.fks[k.gid] = keycode
                    if layer_id != 0:
                        raise ValueError('Fn keycode must be set in layer 0.')
                self.layers[layer_id].append(keycode)

    def decode(self, key_ids: 'List[int]') -> 'List[SendCode]':
        # todo find a quicker impl
        # step 1. 拆分fn
        fn_key_ids = []
        nfn_key_ids = []
        for kid in key_ids:
            if kid in self.fks:
                fn_key_ids.append(kid)
            else:
                nfn_key_ids.append(kid)
        # 从大到小排序的layer码。
        fn_key_layer = sorted(set(self.fks[kid].fn_layer for kid in fn_key_ids), reverse=True)

        # step 2. 用自动降层，获取所有设置的键码
        key_codes = []
        for key_id in nfn_key_ids:
            for fn_key_layers in every_combinations(fn_key_layer):
                fn_layer_joined = 0
                for l in fn_key_layers:  # todo 这里有个优化，可以在计算combination的时候直接返回 | 之后的layer值。
                    fn_layer_joined |= l

                if fn_layer_joined in self.layers and bool(self.layers[fn_layer_joined][key_id]):
                    key_codes.append(self.layers[fn_layer_joined][key_id])
                    break

        # step3. 将所有code 合成SendCode，
        normal_mod_keycodes = [SendCode()]  # 正常模式。每个键键码都是 组合键 或 独立按键。
        composite_mod_codes = []   # 某个键码是组合键+独立按键。要单独发送（不和其他按键使用相同 组合键 ）。

        for kc in key_codes:
            if isinstance(kc, Micro):
                # todo impl 暂停所有发送，使用宏模式。等宏发送完，再接受按键。
                pass
            elif isinstance(kc, EventCode):
                event.emit(kc.name, kc.args)  # 事件键码。直接执行。
            elif isinstance(kc, KeyCode):
                kc: KeyCode
                if kc.k and (not kc.ck):
                    # 如果按键非常多，超过一个SendCode能发送的内容，要放到下一个SendCode中（继承组合按键）。
                    if len(normal_mod_keycodes[-1].k_list) == SendCode.max_code_num:
                        normal_mod_keycodes.append(SendCode(ck=normal_mod_keycodes[-1].ck))
                    normal_mod_keycodes[-1].k_list.append(kc.k)
                elif (not kc.k) and kc.ck:
                    for sc in normal_mod_keycodes:
                        sc.ck = sc.ck | kc.ck
                elif kc.k and kc.ck:
                    composite_mod_codes.append(kc)
                else:
                    pass  # NULL code skip

        # 尝试将 组合键+独立按键 的键码插入normal_mod_keycodes中共用。否则单独发送
        composite_mod_codes_final = []
        for kc in composite_mod_codes:
            if kc.ck == normal_mod_keycodes[-1].ck:  # 插入normal_mod_keycodes中共用
                if len(normal_mod_keycodes[-1].k_list) == SendCode.max_code_num:
                    normal_mod_keycodes.append(SendCode(ck=normal_mod_keycodes[-1].ck))
                normal_mod_keycodes[-1].k_list.append(kc.k)
            else:
                for okc in composite_mod_codes_final:
                    if kc.ck == okc.ck and len(okc.k_list) < SendCode.max_code_num:    # 相同组合键，共用一个SendCode
                        okc.k_list.append(kc.k)
                        break
                else:
                    # 开启一个新的SendCode
                    composite_mod_codes_final.append(SendCode(ck=kc.ck, k_list=[kc.k]))
        return normal_mod_keycodes + composite_mod_codes_final

