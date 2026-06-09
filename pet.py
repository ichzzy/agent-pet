#!/usr/bin/env python3
"""
Agent Pet — a draggable desktop mascot that reacts to Claude activity.

Usage:
    python pet.py [--idle PATH] [--busy PATH] [--width N] [--height N]

State file:  /tmp/claude_busy  (1 = busy, 0 or missing = idle)
"""

import argparse
import ctypes
import ctypes.util
import sys
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, QPoint, QSize
from PyQt6.QtGui import QMovie, QPixmap
from PyQt6.QtWidgets import QApplication, QLabel, QWidget

STATE_FILE = Path("/tmp/claude_busy")
POLL_MS = 1000

ASSETS = Path(__file__).parent / "assets"
DEFAULT_IDLE = ASSETS / "idle.png"
DEFAULT_BUSY = ASSETS / "busy.gif"


class PetWindow(QWidget):
    def __init__(self, idle_path: Path, busy_path: Path, width: int, height: int):
        super().__init__()
        self._idle_path = idle_path
        self._busy_path = busy_path
        self._size = QSize(width, height)
        self._drag_pos: QPoint | None = None
        self._is_busy = False

        self._setup_window()
        self._setup_label()
        self._setup_movie()
        self._show_idle()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._check_state)
        self._timer.start(POLL_MS)

    # ------------------------------------------------------------------
    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow)
        self.resize(self._size)

    def _setup_label(self):
        self._label = QLabel(self)
        self._label.setGeometry(0, 0, self._size.width(), self._size.height())
        self._label.setScaledContents(True)

    def _setup_movie(self):
        self._movie = QMovie(str(self._busy_path))
        self._movie.setScaledSize(self._size)

    # ------------------------------------------------------------------
    def _show_idle(self):
        self._movie.stop()
        pix = QPixmap(str(self._idle_path)).scaled(
            self._size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._label.setMovie(None)
        self._label.setPixmap(pix)

    def _show_busy(self):
        self._label.setPixmap(QPixmap())
        self._label.setMovie(self._movie)
        self._movie.start()

    # ------------------------------------------------------------------
    def _check_state(self):
        busy = STATE_FILE.exists() and STATE_FILE.read_text().strip() == "1"
        if busy == self._is_busy:
            return
        self._is_busy = busy
        if busy:
            self._show_busy()
        else:
            self._show_idle()

    # ------------------------------------------------------------------  drag
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            QApplication.quit()

    def contextMenuEvent(self, event):
        QApplication.quit()


# ----------------------------------------------------------------------
def _pin_to_all_spaces(win_id: int) -> None:
    """Set NSWindowCollectionBehaviorCanJoinAllSpaces so the window appears on every macOS Space."""
    if sys.platform != "darwin":
        return
    objc = ctypes.cdll.LoadLibrary(ctypes.util.find_library("objc"))
    objc.sel_registerName.restype = ctypes.c_void_p
    objc.objc_msgSend.restype = ctypes.c_void_p
    objc.objc_msgSend.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    ns_window = objc.objc_msgSend(win_id, objc.sel_registerName(b"window"))
    objc.objc_msgSend.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
    objc.objc_msgSend(ns_window, objc.sel_registerName(b"setCollectionBehavior:"), ctypes.c_ulong(1))


def main():
    parser = argparse.ArgumentParser(description="Desktop pet that reacts to Claude")
    parser.add_argument("--idle", default=str(DEFAULT_IDLE), help="Static image path")
    parser.add_argument("--busy", default=str(DEFAULT_BUSY), help="Animated GIF path")
    parser.add_argument("--width", type=int, default=120, help="Window width")
    parser.add_argument("--height", type=int, default=120, help="Window height")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    win = PetWindow(Path(args.idle), Path(args.busy), args.width, args.height)
    win.show()
    _pin_to_all_spaces(int(win.winId()))

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
