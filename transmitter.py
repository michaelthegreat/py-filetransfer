"""
`transmitter.py send <filename> <ip> <port>`
`transmitter.py recv <ip> <port>`

"""
import sys
import socket
import os

CHUNK_SIZE = 4096  # 4KB

def send_file(filename, ip, port):
    if not os.path.isfile(filename):
        print(f"Error: File '{filename}' not found.")
        return

    filesize = os.path.getsize(filename)
    try:
        with socket.create_connection((ip, int(port))) as sock:
            print(f"Connected to {ip}:{port}. Sending file: {filename} ({filesize} bytes)")

            # Send filename and filesize first
            sock.sendall(f"{os.path.basename(filename)}|{filesize}".encode() + b'\n')

            with open(filename, 'rb') as f:
                while chunk := f.read(CHUNK_SIZE):
                    sock.sendall(chunk)

            print("File sent successfully.")
    except Exception as e:
        print(f"Error sending file: {e}")
        

def receive_file(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.bind((ip, int(port)))
            server_sock.listen(1)
            print(f"Listening on {ip}:{port}...")

            conn, addr = server_sock.accept()
            with conn:
                print(f"Connection from {addr}")

                # Read header (filename and filesize)
                header = b''
                while not header.endswith(b'\n'):
                    part = conn.recv(1)
                    if not part:
                        raise ConnectionError("Connection closed while reading header.")
                    header += part

                filename, filesize = header.decode().strip().split('|')
                filesize = int(filesize)
                print(f"Receiving file: {filename} ({filesize} bytes)")

                with open(f"received_{filename}", 'wb') as f:
                    bytes_received = 0
                    while bytes_received < filesize:
                        chunk = conn.recv(min(CHUNK_SIZE, filesize - bytes_received))
                        if not chunk:
                            raise ConnectionError("Connection closed unexpectedly.")
                        f.write(chunk)
                        bytes_received += len(chunk)

                print(f"File received and saved as 'received_{filename}'")
    except Exception as e:
        print(f"Error receiving file: {e}")

    
def print_usage():
    print("Usage:")
    print("  transmitter.py send <filename> <ip> <port>")
    print("  transmitter.py recv <ip> <port>")

def main():
    if len(sys.argv) < 2:
        print_usage()
        return

    mode = sys.argv[1]

    if mode == 'send' and len(sys.argv) == 5:
        _, _, filename, ip, port = sys.argv
        send_file(filename, ip, port)
    elif mode == 'recv' and len(sys.argv) == 4:
        _, _, ip, port = sys.argv
        receive_file(ip, port)
    else:
        print_usage()

if __name__ == "__main__":
    main()