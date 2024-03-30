from .base import CoopBoardDriver


__all__ = ['driver']


def get_driver() -> CoopBoardDriver:
    import sys
    # todo 可定制使用什么driver，兼容esp32没有启动函数的问题。
    if sys.platform in ['linux']:
        from .browser import Browser
        return Browser()
    elif sys.platform in ['esp32']:
        from .esp32_hw import Esp32HWDriver
        return Esp32HWDriver()
    else:
        raise RuntimeError(f'can not measure paltform {sys.platform}')


driver: CoopBoardDriver = get_driver()


