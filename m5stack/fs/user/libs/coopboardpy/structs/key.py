

class Key:
    """键盘上的实体按键"""
    def __init__(self, name: str='', gid: int=0, r: int=0, c: int=0, x: float=0., y: float=0., w: float=1., h: float=1.):
        """

        :param gid: 全局id
        :param r: 行
        :param c: 列
        :param x: 绝对坐标x（按照u为单位）
        :param y: 绝对坐标y。（按照u为单位）
        :param w: 宽度
        :param h: 高度：
        """
        self.name = name
        self.gid = gid
        self.r, self.c, self.x, self.y, self.w, self.h = r, c, x, y, w, h

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, d: dict):
        return cls(**d)


class KeyBoard:
    def __init__(self):
        self.keys: 'list[Key]' = []

    @classmethod
    def from_quick_set(cls, key_list_by_rc: 'List[List[Union[str, Key, dict]]]'):
        """
        :param key_list_by_rc: 按照行、列从上到下从左到右（左上角为0，0）传入key的二维数组。
            其中元素 1. 如果是str，则新增叫这个名字的1x1按键。
                   2. 如果是Key，可设置w和h，其设置的x,y为相对上一个自动位置的偏移。
                   3. 如果是dict，则先当作参数构造Key。再用Key构造。
                   * 自动位置，同行猜测为上一个按键右上角，下一行猜测为之前行y+1的位置。
        :return:
        """
        kb = cls()
        gid, r, c, x, y = 0, 0, 0, 0., 0.
        for row in key_list_by_rc:
            for k in row:
                if isinstance(k, dict):
                    k = Key(**k)
                if isinstance(k, str):
                    kb.keys.append(Key(k, gid, r, c, x, y))
                elif isinstance(k, Key):
                    # 如果键盘中有偏移的按键，会带走基础坐标。
                    if abs(k.y-y) > 1e-3:
                        y += k.y
                    if abs(k.x-x) > 1e-3:
                        x += k.x
                    kb.keys.append(Key(k.name, gid, r, c, x, y, k.w, k.h))
                else:
                    raise NotImplementedError()
                gid, c, x = gid + 1, c + 1, x + kb.keys[-1].w
            r, c, x, y = r + 1, 0, 0., y + 1
        return kb

    def to_dict(self):
        return [k.to_dict() for k in self.keys]

    @classmethod
    def from_dict(cls, d: list):
        kb = cls()
        kb.keys = [Key.from_dict(k) for k in d]
        return kb

    @classmethod
    def coopboard_test(cls):
        """原始佩列，用于测试"""
        return cls.from_quick_set([
            [Key('ESC', w=1.25), 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '{[', '}]', '←'],
            [Key('TAB', w=1.5), 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':;', '"\'', Key('ENTER', w=1.75)],
            ['F1', 'Shift-L', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '<,', '>.', Key('?/', w=1.25), '↑', 'F2'],
            ['Ctrl-L', 'Win-L', 'Alt-L', 'F3', 'F4', Key('BLANK', w=2.), Key('BLANK', w=2), 'Alt-R', Key('Ctrl-R', w=1.25), '←', '↓', '→'],
        ])


if __name__ == '__main__':
    from flask import Flask, jsonify
    from flask_cors import CORS

    app = Flask(__name__)
    CORS(app)

    @app.route('/api/keyboard')
    def get_data():
        return jsonify(KeyBoard.coopboard_test().to_dict())

    app.run(debug=True, port=3006)

