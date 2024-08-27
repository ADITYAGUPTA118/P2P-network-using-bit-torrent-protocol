import socket
import random
import sys

class CreatePeer:
    def __init__(self, server_ip, peer_name):
        self.server_ip = server_ip
        self.peer_name = peer_name
        self.peer_ip = self.get_local_ip()
        self.peer_port = self.find_available_port()

    def get_local_ip(self):
        """Fetches the local IP address of the machine."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))  # Connect to a public DNS server
            local_ip = s.getsockname()[0]
        except Exception:
            local_ip = '127.0.0.1'
        finally:
            s.close()
        return local_ip

    def find_available_port(self):
        """Finds an available port on the machine."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))  # Bind to any available port
            return s.getsockname()[1]

    def connect_to_server(self):
        """Connects to the server and registers the peer."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((self.server_ip, 5000))  # Connect to the server (port should match server's port)
            # Send the peer's name, IP, and port information
            peer_info = f"{self.peer_name},{self.peer_ip},{self.peer_port}"
            client.sendall(peer_info.encode())
            
            # Receive the acknowledgment from the server
            response = client.recv(1024).decode()
            print(response)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python createPeer.py  <peer_name>")
        sys.exit(1)
    
    server_ip = "192.168.0.103"
    peer_name = sys.argv[1]
    
    peer = CreatePeer(server_ip, peer_name)
    peer.connect_to_server()
