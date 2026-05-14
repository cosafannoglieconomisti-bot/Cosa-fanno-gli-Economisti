import os
import time
import sys

BRIDGE_LOG = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/cesare/telegram_bridge.log"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    print("🌉 --- TELEGRAM BRIDGE MONITOR --- 🌉")
    print("In attesa di messaggi...")
    
    last_size = 0
    if os.path.exists(BRIDGE_LOG):
        last_size = os.path.getsize(BRIDGE_LOG)
        with open(BRIDGE_LOG, 'r', encoding='utf-8') as f:
            print(f.read())

    try:
        while True:
            if os.path.exists(BRIDGE_LOG):
                current_size = os.path.getsize(BRIDGE_LOG)
                if current_size > last_size:
                    with open(BRIDGE_LOG, 'r', encoding='utf-8') as f:
                        f.seek(last_size)
                        new_data = f.read()
                        print(new_data, end='')
                    last_size = current_size
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMonitor chiuso.")

if __name__ == "__main__":
    main()
