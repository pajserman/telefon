import socket
import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100


# List of receivers to call
receivers = {
    '1': ('localhost', 5005),
    '2': ('hannes-Nitro-AN515-51.local', 5005),
    '3': ('192.168.1.12', 5005),
}

def start_call(target_ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    stream = p.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True, frames_per_buffer=CHUNK)
    print(f"Calling {target_ip}... Press Ctrl+C to hang up.")
    try:
        while True:
            data = stream.read(CHUNK)
            sock.sendto(data, (target_ip, port))
    except KeyboardInterrupt:
        print("Ending call...")
    finally:
        stream.stop_stream()
        stream.close()
        sock.close()

if __name__ == "__main__":
    p = pyaudio.PyAudio()
    while True:
        print("\nAvailable receivers:")
        for key, (ip, port) in receivers.items():
            print(f"{key}: {ip}:{port}")
        choice = input("Enter number to call (or q to quit): ").strip()
        if choice.lower() == 'q':
            break
        if choice in receivers:
            ip, port = receivers[choice]
            start_call(ip, port)
        else:
            print("Invalid selection.")
    p.terminate()
