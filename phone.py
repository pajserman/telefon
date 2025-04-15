# primary_phone.py

import socket
import threading
import pyaudio

class IntercomMaster:
    def __init__(self, recv_port=5006, control_port=6000):
        self.audio_chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.recv_port = recv_port
        self.control_port = control_port

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.format, channels=self.channels,
                                  rate=self.rate, input=True, frames_per_buffer=self.audio_chunk)

        self.response_stream = self.p.open(format=self.format, channels=self.channels,
                                           rate=self.rate, output=True, frames_per_buffer=self.audio_chunk)

        self.audio_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_sock.bind(('', self.recv_port))

        self.running = False

    def _recv_audio(self):
        while self.running:
            try:
                data, _ = self.recv_sock.recvfrom(2048)
                self.response_stream.write(data)
            except Exception as e:
                print(f"[!] Error receiving audio: {e}")

    def start_call(self, target_ip, target_audio_port=5005, target_control_port=6000):
        self.running = True
        recv_thread = threading.Thread(target=self._recv_audio, daemon=True)
        recv_thread.start()

        # Send START_TALK command
        control_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        control_sock.sendto(b"START_TALK", (target_ip, target_control_port))

        print(f"[+] Talking to {target_ip}. Press Ctrl+C to stop.")
        try:
            while self.running:
                data = self.stream.read(self.audio_chunk, exception_on_overflow=False)
                self.audio_sock.sendto(data, (target_ip, target_audio_port))
        except KeyboardInterrupt:
            print("\n[!] Ending call.")
            self.end_call(target_ip, target_control_port)
        finally:
            self.running = False

    def end_call(self, target_ip, target_control_port=6000):
        control_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        control_sock.sendto(b"STOP_TALK", (target_ip, target_control_port))

    def close(self):
        self.running = False
        self.stream.stop_stream()
        self.stream.close()
        self.response_stream.stop_stream()
        self.response_stream.close()
        self.p.terminate()
        self.audio_sock.close()
        self.recv_sock.close()
