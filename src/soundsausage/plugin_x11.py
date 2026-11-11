"""Small Xlib window helpers used only inside the disposable editor process."""
import ctypes as C


class X11:
    def __init__(self):
        self.lib=C.CDLL('libX11.so.6')
        self.lib.XOpenDisplay.argtypes=[C.c_char_p];self.lib.XOpenDisplay.restype=C.c_void_p
        self.lib.XCloseDisplay.argtypes=[C.c_void_p]
        self.lib.XGetGeometry.argtypes=[C.c_void_p,C.c_ulong,C.POINTER(C.c_ulong),C.POINTER(C.c_int),C.POINTER(C.c_int),
            C.POINTER(C.c_uint),C.POINTER(C.c_uint),C.POINTER(C.c_uint),C.POINTER(C.c_uint)]
        self.lib.XMoveResizeWindow.argtypes=[C.c_void_p,C.c_ulong,C.c_int,C.c_int,C.c_uint,C.c_uint]
        self.lib.XFlush.argtypes=[C.c_void_p]
        self.display=self.lib.XOpenDisplay(None)
        if not self.display:raise ValueError('Cannot connect the plug-in window to X11/XWayland.')

    def size(self,window):
        root=C.c_ulong();x,y=C.c_int(),C.c_int();width,height,border,depth=(C.c_uint() for _ in range(4))
        ok=self.lib.XGetGeometry(self.display,window,C.byref(root),C.byref(x),C.byref(y),C.byref(width),C.byref(height),C.byref(border),C.byref(depth))
        return (width.value,height.value) if ok else None

    def resize(self,window,width,height):
        self.lib.XMoveResizeWindow(self.display,window,0,0,width,height);self.lib.XFlush(self.display)

    def close(self):
        if self.display:self.lib.XCloseDisplay(self.display);self.display=None
