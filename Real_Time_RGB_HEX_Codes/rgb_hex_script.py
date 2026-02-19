import pyautogui
from PIL import ImageGrab
import time
from pynput import keyboard

##### Helper functions #####
def get_rgb_hex(rgb):
    # Take the first 3 values (R, G, B) to handle edge case where alpha channel is present
    r, g, b = rgb[:3]
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def on_press(key):
    if hasattr(key, 'char') and key.char == 's':
        global hex_color
        
        with open(fr'Real_Time_RGB_HEX_Codes\rgb_hex_colors.txt', 'a') as f:
            f.write(f'{hex_color}\n')
            print(f'Saved {hex_color} to rgb_hex_colors.txt')
            
def clear_color_file():
    with open(fr'Real_Time_RGB_HEX_Codes\rgb_hex_colors.txt', 'w') as f:
        f.write('')

##### Main program #####
clear_color_file()
listener = keyboard.Listener(on_press=on_press)
listener.start()

print('Press Ctrl+C to stop program...')

try:
    while True:
        # Get the current mouse position
        x, y = pyautogui.position()
        
        img = ImageGrab.grab(bbox=(x, y, x+1, y+1))  # Capture a 1x1 pixel area at the mouse position
        # Get the RGB value of the pixel at the mouse position
        rgb = img.getpixel((0, 0))
        # Convert RGB to HEX
        hex_color = get_rgb_hex(rgb)
        
        print(f'RGB: {rgb} | HEX: {hex_color}        ', end='\r')
        time.sleep(0.1)    
except KeyboardInterrupt:
    print("\nExiting...")