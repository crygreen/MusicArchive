import ctypes
import time
import pygetwindow as gw

windows = gw.getWindowsWithTitle("Яндекс")

if not windows:
    print("Яндекс не найден")
    input()
    raise SystemExit

window = windows[0]
hwnd = window._hWnd
user32 = ctypes.windll.user32

# SW_RESTORE — восстановить окно, если оно свёрнуто
user32.ShowWindow(hwnd, 9)
time.sleep(1)

# Переводим окно на передний план
user32.BringWindowToTop(hwnd)
user32.SetForegroundWindow(hwnd)

time.sleep(1)

print("Свёрнуто:", window.isMinimized)
print("Активное окно:", gw.getActiveWindow().title)

input("Проверь браузер. Enter для выхода...")