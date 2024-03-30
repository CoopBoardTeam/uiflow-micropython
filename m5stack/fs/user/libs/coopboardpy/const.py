#! /usr/bin/env python
# -*- coding: utf-8 -*_
# Author: Liu Yang <mkliuyang@gmail.com>

class K:
    NULL = 0
    ErrorRollOver = 1
    POSTFail = 2
    ErrorUndefined = 3
    A = 4
    B = 5
    C = 6
    D = 7
    E = 8
    F = 9
    G = 10
    H = 11
    I = 12
    J = 13
    K = 14
    L = 15
    M = 16
    N = 17
    O = 18
    P = 19
    Q = 20
    R = 21
    S = 22
    T = 23
    U = 24
    V = 25
    W = 26
    X = 27
    Y = 28
    Z = 29
    _1 = 30
    _2 = 31
    _3 = 32
    _4 = 33
    _5 = 34
    _6 = 35
    _7 = 36
    _8 = 37
    _9 = 38
    _0 = 39
    RETURN = 40
    ESC = 41
    DEL = 42
    TAB = 43
    SPACE = 44
    MINUS = 45
    EQUAL = 46
    LEFT_BRACKET = 47
    RIGHT_BRACKET = 48
    BACK_SLASH = 49
    SEMICOLON = 51  # ; :
    BACK_QUOTES = 53  # ·~
    QUOTES = 52  # " '
    COMMA = 54
    END_MARK = 55
    SLASH = 56
    CAPSLOCK = 57
    F1 = 58
    F2 = 59
    F3 = 60
    F4 = 61
    F5 = 62
    F6 = 63
    F7 = 64
    F8 = 65
    F9 = 66
    F10 = 67
    F11 = 68
    F12 = 69
    PRT_SCR = 70
    SCROLL_LOCK = 71
    PAUSE = 72
    INSERT = 73
    HOME = 74
    PAGE_UP = 75
    DELETE_FORWARD = 76
    END = 77
    PAGE_DOWN = 78
    RIGHT_ARROW = 79
    LEFT_ARROW = 80
    DOWN_ARROW = 81
    UP_ARROW = 82
    NumLock_and_Clear = 83
    Divide = 84  # '/'
    Multiply = 85  # *
    Minus = 86
    Plus = 87
    ENTER = 88
    NUM_1_and_End = 89
    NUM_2_and_Down_Arrow = 90
    NUM_3_and_PageDn = 91
    NUM_4_and_Left_Arrow = 92
    NUM_5 = 93
    NUM_6_and_Right_Arrow = 94
    NUM_7_and_Home = 95
    NUM_8_and_Up_Arrow = 96
    NUM_9_and_PageUp = 97
    NUM_0_and_Insert = 98
    Dot_and_Delete = 99  # .
    BACK_SLASH_2 = 100  # \ and |
    RIGHT_CLICK = 101  # click right
    Power = 102
    Equal = 103  # =
    F13 = 104
    F14 = 105
    F15 = 106
    F16 = 107
    F17 = 108
    F18 = 103
    F19 = 110
    F20 = 111
    F21 = 112
    F22 = 113
    F23 = 114
    F24 = 115
    Execute = 116
    Help = 117
    Menu = 118
    Select = 119
    Stop = 120
    Again = 121
    Undo = 122
    Cut = 123
    Copy = 124
    Paste = 125
    Find = 126
    VOLUME_MUTE = 127
    VOLUME_UP = 128
    VOLUME_DOWN = 129
    Locking_Caps_Lock = 130
    Locking_Num_Lock = 131
    Locking_Scroll_Lock = 132
    Comma = 133
    Equal_Sign = 134
    International1 = 135
    International2 = 136
    International3 = 137
    International4 = 138
    International5 = 139
    International6 = 140
    International7 = 141
    International8 = 142
    International9 = 143
    LANG1 = 144
    LANG2 = 145
    LANG3 = 146
    LANG4 = 147
    LANG5 = 148
    LANG6 = 149
    LANG7 = 150
    LANG8 = 151
    LANG9 = 152
    Alternate_Erase = 153
    SysReq_Attention = 154
    Cancel = 155
    Clear = 156
    Prior = 157
    Return = 158
    Separator = 159
    Out = 160
    Oper = 161
    Clear_Again = 162
    CrSel_Props = 163
    ExSel = 164
    _00 = 176
    _000 = 177
    # Thousands_Separator = 178
    # Decimal_Separator = 179
    # Currency_Unit = 180
    # Currency_Sub_unit = 181
    LEFT_BRACKET_2 = 182  # (
    RIGHT_BRACKET_2 = 183  # )
    LEFT_BIG_BRACKET = 184  # {
    RIGHT_BIG_BRACKET = 185  # }
    Tab = 186
    Backspace = 187
    A_2 = 188
    B_2 = 189
    C_2 = 190
    D_2 = 191
    E_2 = 192
    F_2 = 193
    XOR = 194
    XOR_BITS = 195  # ^
    Percent = 196  # %
    SMALLER = 197  # <
    GREATER = 198  # >
    AND = 199  # %
    AND_BITS = 200  # %%
    OR = 201  # |
    OR_BITS = 202  # ||
    Colon = 203  #:
    Number_Sign = 204  ##
    Space = 205
    AT = 206  # @
    NOT = 207  # !
    Memory_Store = 208
    Memory_Recall = 209
    Memory_Clear = 210
    Memory_Add = 211
    Memory_Subtract = 212
    Memory_Multiply = 213
    Memory_Divide = 214
    PLUS_SUBTRACTION = 215  # /+/-
    Clear_2 = 216
    Clear_Entry = 217
    Binary = 218
    Octal = 219
    Decimal = 220
    exadecimal = 221

    # / 以下是非标键码，用于特殊按键事件的判断。
    # 下跳沿事件键码
    RESERVED_PLF_CODE = 250
    # 上跳沿键码
    RESERVED_PLS_CODE = 251
    # 保持键码（保持逻辑是包括下跳沿的）
    RESERVED_KD_CODE = 252

    #    # 以下不属于标准键盘标准       
    #    FN1 =  101                      
    #    FN2 =  102
    #    FN3 =  103
    #    FN4 =  104
    #    FN5 =  105
    __name2code = {}
    __code2name = {}

    @classmethod
    def init_map(cls):
        if len(cls.__name2code) == 0:
            for k, v in cls.__dict__.items():
                if k.startswith('_'):
                    k = k[1:]  # attribute 的 名 由于有些是数字开头的，所以要以下划线开始。转换为字符串key时应去掉。
                if isinstance(v, int):
                    cls.__name2code[k] = v
                    cls.__code2name[v] = k

    @classmethod
    def get_code(cls, name: str) -> int:
        return cls.__name2code[name]

    @classmethod
    def get_name(cls, code: int) -> str:
        return cls.__code2name[code]

    @classmethod
    def has_name(cls, k: str):
        return k in cls.__name2code

    @classmethod
    def has_code(cls, c: int):
        return c in cls.__code2name


K.init_map()


class CK:
    # 以下三个按键在八字节的第一个字节的0123位
    CTRL_L = 1  # D0
    SHIFT_L = 2  # D1
    ALT_L = 4  # D2
    WIN_L = 8  # D3
    CTRL_R = 16  # D4
    SHIFT_R = 32  # D5
    ALT_R = 64  # D6
    WIN_R = 128  # D7

    # 第二个字节为0
    # 第345678字节保存键值
    __name2code = {}

    @classmethod
    def init_map(cls):
        if len(cls.__name2code) == 0:
            for k, v in cls.__dict__.items():
                if isinstance(v, int):
                    cls.__name2code[k] = v

    @classmethod
    def get_code(cls, name: str) -> int:
        if len(name) == 0:
            return 0
        code = 0
        for v in name.split('|'):
            code |= cls.__name2code[v]
        return code

    @classmethod
    def get_name(cls, code: int) -> str:
        if code == 0:
            return ''
        names = []
        for k, v in cls.__name2code.items():
            if v & code:
                names.append(k)
        return '|'.join(names)

    @classmethod
    def all_names(cls) -> list:
        return list(cls.__name2code.keys())

    @classmethod
    def has_name(cls, k: str):
        return k in cls.__name2code


CK.init_map()

assert all(not K.has_name(n) for n in CK.all_names())
assert all(not K.has_name(f'Fn{fn_id}') for fn_id in range(10))


if __name__ == '__main__':
    k_name = CK.get_name(CK.SHIFT_L | CK.ALT_L | CK.WIN_R)
    print(k_name)
    k_code = CK.get_code(k_name)
    print(k_code)

