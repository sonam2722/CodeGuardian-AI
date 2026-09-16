import time
import ctypes
import pyautogui


user32 = ctypes.windll.user32


def focus_notepad():
    """Bring Notepad to the foreground."""

    hwnd = user32.FindWindowW(
        None,
        None
    )

    # Find a visible Notepad window
    def enum_windows_proc(hwnd, lParam):
        length = user32.GetWindowTextLengthW(hwnd)

        if length == 0:
            return True

        title = ctypes.create_unicode_buffer(length + 1)

        user32.GetWindowTextW(
            hwnd,
            title,
            length + 1
        )

        window_title = title.value.lower()

        if "notepad" in window_title:
            user32.ShowWindow(hwnd, 5)
            user32.SetForegroundWindow(hwnd)
            return False

        return True

    enum_proc = ctypes.WINFUNCTYPE(
        ctypes.c_bool,
        ctypes.c_void_p,
        ctypes.c_void_p
    )(enum_windows_proc)

    user32.EnumWindows(
        enum_proc,
        0
    )

    time.sleep(0.5)


def type_text(text):
    """Type text into the active application."""

    focus_notepad()

    time.sleep(0.5)

    pyautogui.write(
        text,
        interval=0.03
    )

    return "Text typed successfully, Boss."


def press_key(key):
    """Press a keyboard key."""

    pyautogui.press(key)

    return f"Pressed {key}, Boss."


def hotkey(*keys):
    """Press a keyboard shortcut."""

    pyautogui.hotkey(*keys)

    return "Keyboard shortcut executed, Boss."


def click(x, y):
    """Click at a screen position."""

    pyautogui.click(x, y)

    return "Clicked successfully, Boss."


def move_mouse(x, y):
    """Move the mouse."""

    pyautogui.moveTo(
        x,
        y,
        duration=0.2
    )

    return "Mouse moved, Boss."


def wait(seconds=1):
    """Wait for a short time."""

    time.sleep(seconds)