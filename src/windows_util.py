import win32api as win
import win32con as con

S_KEY_HEX = 0x53
Q_KEY_HEX = 0x51
s_state = win.GetKeyState(S_KEY_HEX)
q_state = win.GetKeyState(Q_KEY_HEX)

def q_pressed():
    key_q = win.GetKeyState(Q_KEY_HEX)
    return key_q != q_state and key_q < 0

def s_pressed():
    key_s = win.GetKeyState(S_KEY_HEX)
    return key_s != s_state and key_s < 0

def mouse_move(x, y):
    win.SetCursorPos((x, y))

def get_mouse_event(btn="left", direction="down"):
    if btn == "left":
        return con.MOUSEEVENTF_LEFTDOWN if direction == "down" else con.MOUSEEVENTF_LEFTUP
    elif btn == "right":
        return con.MOUSEEVENTF_RIGHTDOWN if direction == "down" else con.MOUSEEVENTF_RIGHTUP
    return None

def mouse_down(x, y, btn="left"):
    win.mouse_event(get_mouse_event(btn, "down"), x, y, 0, 0)

def mouse_up(x, y, btn="left"):
    win.mouse_event(get_mouse_event(btn, "up"), x, y, 0, 0)

def click(x, y, btn="left"):
    mouse_move(x, y)
    mouse_down(x, y, btn)
    mouse_up(x, y, btn)

def get_screen_size():
    return (1920, 1080)#(win.GetSystemMetrics(0), win.GetSystemMetrics(1))
