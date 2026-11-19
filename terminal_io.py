"""リアルタイムASCIIゲーム用のキー入力補助（標準ライブラリのみ）。

Windows: msvcrt / macOS・Linux: termios + select。
Windows Terminal / VS Codeの統合ターミナルを推奨。
"""
from __future__ import annotations
import os
import sys


class Terminal:
    def __init__(self):
        self._old = None
        self._fd = None

    def __enter__(self):
        if os.name == 'nt':
            os.system('')  # WindowsでANSI制御を有効化できる環境では有効化
        elif sys.stdin.isatty():
            import termios
            import tty
            self._fd = sys.stdin.fileno()
            self._old = termios.tcgetattr(self._fd)
            tty.setcbreak(self._fd)
        print('\033[?25l', end='', flush=True)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._old is not None:
            import termios
            termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old)
        print('\033[?25h\033[0m', end='', flush=True)

    def read_key(self):
        """押されたキーを小文字で返す。何もなければ空文字。矢印は left/right/up/down。"""
        if os.name == 'nt':
            import msvcrt
            if not msvcrt.kbhit():
                return ''
            b = msvcrt.getwch()
            if b in ('\x00', '\xe0'):
                k = msvcrt.getwch()
                return {'K': 'left', 'M': 'right', 'H': 'up', 'P': 'down'}.get(k, '')
            return b.lower()
        import select
        if not select.select([sys.stdin], [], [], 0)[0]:
            return ''
        c = sys.stdin.read(1)
        if c == '\x1b':
            # 環境によってはESCシーケンスが分割到着する
            if select.select([sys.stdin], [], [], 0.015)[0] and sys.stdin.read(1) == '[':
                if select.select([sys.stdin], [], [], 0.015)[0]:
                    return {'A': 'up', 'B': 'down', 'C': 'right', 'D': 'left'}.get(sys.stdin.read(1), '')
            return 'q'
        return c.lower()


def paint(lines):
    print('\033[H\033[J' + '\n'.join(lines), end='\n', flush=True)
