import socket
import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
PORT = 5005

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, output=True, frames_per_buffer=CHUNK)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', PORT))

print("Receiving audio... Press Ctrl+C to stop.")

try:
    while True:
        data, addr = sock.recvfrom(2048)
        stream.write(data)
except KeyboardInterrupt:
    print("\nShutting down receiver...")

finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    sock.close()
    print("Receiver closed cleanly.")
