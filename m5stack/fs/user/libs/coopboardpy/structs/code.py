#! /usr/bin/env python
# -*- coding: utf-8 -*_
# Author: Liu Yang <mkliuyang@gmail.com>

"""
键码，可以扩展理解为一种操作（键盘按键、鼠标操作、键盘操作、宏等）。
"""
from coopboardpy.const import K, CK


class Code:
    _named_classes = {}

    @classmethod
    def register(cls, new_class):
        cls._named_classes[new_class.__name__] = new_class
        return new_class

    def __repr__(self):
        attr_string = ', '.join(f'{k}={v}' for k, v in self.__dict__)
        return f'{self.__class__.__name__}({attr_string}'

    @classmethod
    def from_dict(cls, d: 'Union[Dict[str, Any], str, int]'):
        if isinstance(d, str):   # 如果是字符串，默认为普通键名
            if d == '':
                return cls._named_classes['KeyCode'](0, 0)
            elif d.lower().startswith('fn'):  # FN开头的是Fn，key
                return cls._named_classes['FnCode'](int(d[2:]))
            elif CK.has_name(d):
                return cls._named_classes['KeyCode'](0, CK.get_code(d))
            elif K.has_name(d):
                return cls._named_classes['KeyCode'](K.get_code(d))
            else:
                raise ValueError(f'unknown simple str key code "{d}"')
        if isinstance(d, int):   # 如果是字符串，默认为普通键码
            return cls._named_classes['KeyCode'](d)
        t = d.pop('type')
        return cls._named_classes[t](**d)

    def to_dict(self):
        raise NotImplementedError()


@Code.register
class KeyCode(Code):
    def __init__(self, k=0, ck=0):
        self.k = k
        self.ck = ck

    def to_dict(self):
        if self.k and not self.ck:
            return K.get_name(self.k)
        elif not self.k and self.ck:
            return CK.get_name(self.ck)
        else:
            return {'type': self.__class__.__name__, 'k': self.k, 'ck': self.ck}

    def __bool__(self):
        return bool(self.k or self.ck)


@Code.register
class FnCode(Code):
    def __init__(self, fn: int):
        self.fn = fn  # fn_num
        self.fn_layer = 1 << (fn - 1)

    def to_dict(self):
        return f'Fn{self.fn}'


@Code.register
class Micro(Code):
    # todo
    pass


@Code.register
class SendCode(Code):
    max_code_num = 6
    """用于发送的键码。很特殊的一种格式，同时发送组合键相同的6个普通键码。"""
    def __init__(self, ck: int=0, k_list: 'List[int|str]'=None):
        self.ck = CK.get_code(ck) if isinstance(ck, str) else ck
        self.k_list: 'List[int]' = k_list or []
        for kid, k in enumerate(self.k_list):
            if isinstance(k, str):
                self.k_list[kid] = K.get_code(k)

    def to_dict(self):
        return {'type': self.__class__.__name__, 'ck': CK.get_name(self.ck), 'k_list': [K.get_name(k) for k in self.k_list]}


@Code.register
class EventCode(Code):
    """发送一个event"""
    def __init__(self, name='', args=None):
        self.name = name
        self.args = args


class CodeMap:
    def __init__(self, m=None):
        self.m = m or {}

    @classmethod
    def from_dict(cls, d: dict):
        d = {(int(k) if isinstance(k, str) and k.isdigit() else k): v for k, v in d.items()}
        for layer, v in d.items():
            for r in range(len(v)):
                for c in range(len(v[r])):
                    if v[r][c] is not None:
                        v[r][c] = Code.from_dict(v[r][c])
        return cls(d)

    def to_dict(self):
        nd = {}
        for layer, v in self.m.items():
            nd[layer] = []
            for r in range(len(v)):
                nd[layer].append([])
                for c in range(len(v[r])):
                    nd[layer][-1].append(v[r][c].to_dict() if isinstance(v[r][c], Code) else None)
        return nd

    @classmethod
    def keycode_test(cls):
        # 测试53键盘佩列
        return cls.from_dict({
            0: [
                ['ESC', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', K.LEFT_BIG_BRACKET, K.RIGHT_BIG_BRACKET, K.DELETE_FORWARD],
                ['TAB', "A", "S", "D", "F", "G", "H", "J", "K", "L", K.SEMICOLON, K.QUOTES, K.ENTER],
                ['FN1', 'SHIFT_L', "Z", "X", "C", "V", "B", "N", "M", K.SMALLER, K.GREATER, K.SLASH, K.UP_ARROW, 'FN2'],
                ['CTRL_L', 'WIN_L', 'ALT_L', 'FN3', 'FN4', K.SPACE, K.SPACE, "ALT_R", 'CTRL_R', K.LEFT_ARROW, K.DOWN_ARROW, K.RIGHT_ARROW],
            ]
        })


if __name__ == '__main__':
    cm = CodeMap.keycode_test()
    import json
    print(json.dumps(cm.to_dict()))

