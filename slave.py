# secondary_phone.py

import socket
import threading
import time
import traceback
import pyaudio

def run_secondary():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    AUDIO_RECV_PORT = 5005     # Receives from master
    CONTROL_RECV_PORT = 6000   # For START/STOP messages
    MASTER_IP = None           # Dynamically detected on START_TALK
    MASTER_PORT = 5006         # Sends audio back here

    sending = False

    while True:
        try:
            p = pyaudio.PyAudio()

            stream_out = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                                output=True, frames_per_buffer=CHUNK)

            stream_in = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                               input=True, frames_per_buffer=CHUNK)

            audio_recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            audio_recv_sock.bind(('', AUDIO_RECV_PORT))

            control_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            control_sock.bind(('', CONTROL_RECV_PORT))

            send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            def listen_for_audio():
                while True:
                    data, _ = audio_recv_sock.recvfrom(2048)
                    stream_out.write(data)

            def listen_for_control():
                nonlocal sending, MASTER_IP
                while True:
                    msg, addr = control_sock.recvfrom(1024)
                    command = msg.decode().strip()
                    if command == "START_TALK":
                        MASTER_IP = addr[0]
                        sending = True
                        print(f"[+] Called by {MASTER_IP}")
                    elif command == "STOP_TALK":
                        sending = False
                        print("[!] Call ended")

            def send_audio():
                while True:
                    if sending and MASTER_IP:
                        data = stream_in.read(CHUNK, exception_on_overflow=False)
                        send_sock.sendto(data, (MASTER_IP, MASTER_PORT))

            # Start all threads
            threading.Thread(target=listen_for_audio, daemon=True).start()
            threading.Thread(target=listen_for_control, daemon=True).start()
            threading.Thread(target=send_audio, daemon=True).start()

            print("[*] Secondary phone ready.")
            while True:
                time.sleep(1)

        except Exception as e:
            print("[!] Error occurred:")
            traceback.print_exc()
            print("[*] Restarting in 3 seconds...")
            time.sleep(3)

if __name__ == "__main__":
    run_secondary()
