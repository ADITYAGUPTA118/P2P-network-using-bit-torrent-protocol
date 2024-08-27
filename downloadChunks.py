# import sys
# import socket
# import json
# import os
# import threading

# def start_peer_server(peer_ip, peer_port):
#     """Start a server on the peer to listen for incoming chunks."""
#     def handle_client(conn, addr):
#         """Handle incoming chunk."""
#         chunk_data = conn.recv(4096)
#         directory = f"peer_{peer_ip}_{peer_port}"
#         os.makedirs(directory, exist_ok=True)
#         file_name = f"{directory}/received_chunk_{addr[0]}_{addr[1]}"
#         with open(file_name, 'wb') as f:
#             f.write(chunk_data)
#         conn.sendall(b"ACK")
#         conn.close()
    
#     peer_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     peer_server.bind((peer_ip, peer_port))
#     peer_server.listen()
#     print(f"Peer server listening on {peer_ip}:{peer_port}...")

#     while True:
#         conn, addr = peer_server.accept()
#         thread = threading.Thread(target=handle_client, args=(conn, addr))
#         thread.start()


# def fetch_from_server(server_ip, server_port, request_type):
#     """Fetch data (peers, reputations, or DHT) from the central server."""
#     try:
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#             s.connect((server_ip, server_port))
#             s.sendall(request_type.encode())
#             response = s.recv(4096).decode()
#             data = json.loads(response)
#             return data
#     except socket.error as e:
#         print(f"Failed to fetch data from server: {e}")
#         sys.exit(1)

# def download_chunks(file_key, peers):
#     """Request and download chunks of a file from peers."""
#     file_chunks = {}
#     print("peers2",peers)
#     for peer in peers:
#         peer_id = f"{peer['ip']}:{peer['port']}"
#         try:
#             with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#                 print(f"{peer['ip']},{peer['port']}")
#                 s.connect((peer['ip'], peer['port']))
#                 s.sendall(f"HAVE_KEY:{file_key}".encode())
#                 response = s.recv(1024).decode()
#                 print(response)
#                 if "HAS_KEY" in response:
#                     print("HAS_KEY")
#                     print(f"{peer_id} has the file key. Requesting chunks...")
                    
#                     for i in range(len(file_chunks)): 
#                         s.sendall(f"GET_CHUNK:{file_key}:{i}".encode())
#                         chunk = s.recv(4096)
#                         if chunk:
#                             file_chunks[i] = chunk
#                             print(f"Received chunk {i} from {peer_id}")
#                         else:
#                             print(f"Failed to receive chunk {i} from {peer_id}")
#                 else:
#                     print("Error fetching response")
#                     sys.exit(1)
#         except socket.error as e:
#             print(f"Failed to connect to peer {peer_id}: {e}")

#     # Reassemble the file
#     with open(f"{file_key}_downloaded", "wb") as f:
#         for i in sorted(file_chunks.keys()):
#             f.write(file_chunks[i])

#     print(f"File {file_key} downloaded successfully.")

# def process_peers_data(peers_data):
#     """Convert peers_data into a list of dictionaries with IP and port."""
#     peers = []
#     for peer_id in peers_data["ids"]:
#         ip, port = peer_id.split(":")
#         peers.append({"ip": ip, "port": int(port)})
#     return peers

# def main():
#     if len(sys.argv) != 2:
#         print("Usage: python downloadChunks.py <file_key>")
#         sys.exit(1)

#     file_key = sys.argv[1]
#     server_ip = "192.168.0.103"  # Replace with the actual server IP
#     server_port = 5000  # Replace with the actual server port

#     # Fetch peer list from the central server
#     peers_data = fetch_from_server(server_ip, server_port, "GET_PEERS")
#     print(f"peers data {peers_data}")
#     peers = process_peers_data(peers_data)
#     # Start peer servers in separate threads
#     for peer in peers:
#         threading.Thread(target=start_peer_server, args=(peer['ip'], peer['port'])).start()
#     print(f"peers {peers}")
#     # Download chunks
#     download_chunks(file_key, peers)

# if __name__ == "__main__":
#     main()



import sys
import socket
import json
import os
import threading
from Peer import Peer  # Assuming Peer class is in peer.py

def fetch_from_server(server_ip, server_port, request_type):
    """Fetch data (peers, reputations, or DHT) from the central server."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((server_ip, server_port))
            s.sendall(request_type.encode())
            response = s.recv(4096).decode()
            data = json.loads(response)
            return data
    except socket.error as e:
        print(f"Failed to fetch data from server: {e}")
        sys.exit(1)

# def download_chunks(file_key, peers):
#     """Request and download chunks of a file from peers."""
#     file_chunks = {}

#     for peer in peers:
#         peer_id = f"{peer['ip']}:{peer['port']}"
#         try:
#             with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#                 s.connect((peer['ip'], peer['port']))
#                 s.sendall(f"HAVE_KEY:{file_key}".encode())
#                 response = s.recv(1024).decode()
#                 if "HAS_KEY" in response:
#                     print(f"{peer_id} has the file key. Requesting chunks...")

#                     # You may need to adjust the range based on the actual number of chunks
#                     for i in range(10):  # Assuming 10 chunks, adjust as necessary
#                         s.sendall(f"GET_CHUNK:{file_key}:{i}".encode())
#                         chunk = s.recv(4096)
#                         if chunk:
#                             file_chunks[i] = chunk
#                             print(f"Received chunk {i} from {peer_id}")
#                         else:
#                             print(f"Failed to receive chunk {i} from {peer_id}")
#                 else:
#                     print("Error: Peer does not have the requested file key.")
#         except socket.error as e:
#             print(f"Failed to connect to peer {peer_id}: {e}")

#     # Reassemble the file
#     with open(f"{file_key}_downloaded", "wb") as f:
#         for i in sorted(file_chunks.keys()):
#             f.write(file_chunks[i])

#     print(f"File {file_key} downloaded successfully.")


import sys
import socket
import json
import os
import threading
import hashlib

def read_peer_to_chunk_mapping(file_key):
    """Read the PeerToChunk.json to find which peers have chunks of the file."""
    with open("PeerToChunk.json", "r") as f:
        peer_to_chunk = json.load(f)
    if file_key in peer_to_chunk:
        return peer_to_chunk[file_key]
    else:
        print(f"No peers found for file key: {file_key}")
        sys.exit(1)

def generate_hash(file_key, chunk_number):
    """Generate a hash value based on the file_key and chunk_number."""
    data = f"{file_key}_{chunk_number}".encode()
    return hashlib.sha256(data).hexdigest()

def download_chunks(file_key, peer_to_chunks):
    """Request and download chunks of a file from peers."""
    file_chunks = {}

    for peer_id, chunks in peer_to_chunks.items():
        ip, port = peer_id.split(":")
        print(f":: {ip} {port}")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip, int(port)))
                print(f"{peer_id} has the file key. Requesting chunks...")

                for i in chunks:
                    s.sendall(f"GET_CHUNK:{file_key}:{i}".encode())
                    chunk = s.recv(4096)
                    if chunk:
                        file_chunks[i] = chunk
                        print(f"Received chunk {i} from {peer_id}")
                    else:
                        print(f"Failed to receive chunk {i} from {peer_id}")
                
        except socket.error as e:
            print(f"Failed to connect to peer {peer_id}: {e}")

    # Reassemble the file
    with open(f"{file_key}_downloaded", "wb") as f:
        for i in sorted(file_chunks.keys()):
            f.write(file_chunks[i])

    print(f"File {file_key} downloaded successfully.")


def process_peers_data(peers_data):
    """Convert peers_data into a list of Peer objects."""
    peers = []
    for peer_id in peers_data["ids"]:
        ip, port = peer_id.split(":")
        peer = Peer(name=f"Peer-{ip}:{port}", ip=ip, port=int(port))
        peers.append(peer)
    return peers

def start_peer_servers(peers):
    """Start peer servers in separate threads."""
    for peer in peers:
        print(peer)
        # Each peer runs its server in a separate thread
        thread = threading.Thread(target=peer.start_peer_server, args=(peer.peer_id.split(":")[0], int(peer.peer_id.split(":")[1]), {}))
        thread.start()

def main():
    if len(sys.argv) != 2:
        print("Usage: python downloadChunks.py <file_key>")
        sys.exit(1)

    file_key = sys.argv[1]

    server_ip = "192.168.0.103"  # Replace with the actual server IP
    server_port = 5000  # Replace with the actual server port

#     # Fetch peer list from the central server
    peers_data = fetch_from_server(server_ip, server_port, "GET_PEERS")
    peers = process_peers_data(peers_data)

    # Start peer servers in separate threads
    start_peer_servers(peers)

    # Read peer-to-chunk mapping from PeerToChunk.json
    peer_to_chunks = read_peer_to_chunk_mapping(file_key)
    print(peer_to_chunks)
    # Download chunks
    download_chunks(file_key, peer_to_chunks)

if __name__ == "__main__":
    main()










# def download_chunks(file_key, peers):
#     """Request and download chunks of a file from peers."""
#     file_chunks = {}

#     for peer in peers:
#         peer_id = peer.peer_id  # Accessing peer_id directly from the Peer object
#         try:
#             with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#                 s.connect((peer.peer_id.split(":")[0], int(peer.peer_id.split(":")[1])))
#                 s.sendall(f"HAVE_KEY:{file_key}".encode())
#                 response = s.recv(1024).decode()
#                 if "HAS_KEY" in response:
#                     print(f"{peer_id} has the file key. Requesting chunks...")

#                     # You may need to adjust the range based on the actual number of chunks
#                     for i in range(10):  # Assuming 10 chunks, adjust as necessary
#                         s.sendall(f"GET_CHUNK:{file_key}:{i}".encode())
#                         chunk = s.recv(4096)
#                         if chunk:
#                             file_chunks[i] = chunk
#                             print(f"Received chunk {i} from {peer_id}")
#                         else:
#                             print(f"Failed to receive chunk {i} from {peer_id}")
#                 else:
#                     print("Error: Peer does not have the requested file key.")
#         except socket.error as e:
#             print(f"Failed to connect to peer {peer_id}: {e}")

#     # Reassemble the file
#     with open(f"{file_key}_downloaded", "wb") as f:
#         for i in sorted(file_chunks.keys()):
#             f.write(file_chunks[i])

#     print(f"File {file_key} downloaded successfully.")

# def process_peers_data(peers_data):
#     """Convert peers_data into a list of Peer objects."""
#     peers = []
#     for peer_id in peers_data["ids"]:
#         ip, port = peer_id.split(":")
#         peer = Peer(name=f"Peer-{ip}:{port}", ip=ip, port=int(port))
#         peers.append(peer)
#     return peers

# def start_peer_servers(peers):
#     """Start peer servers in separate threads."""
#     for peer in peers:
#         # Each peer runs its server in a separate thread
#         thread = threading.Thread(target=peer.start_peer_server, args=(peer.peer_id.split(":")[0], int(peer.peer_id.split(":")[1]), {}))
#         thread.start()

# def main():
#     if len(sys.argv) != 2:
#         print("Usage: python downloadChunks.py <file_key>")
#         sys.exit(1)

#     file_key = sys.argv[1]
#     server_ip = "192.168.0.103"  # Replace with the actual server IP
#     server_port = 5000  # Replace with the actual server port

# #     # Fetch peer list from the central server
#     peers_data = fetch_from_server(server_ip, server_port, "GET_PEERS")
#     peers = process_peers_data(peers_data)

#     # Start peer servers in separate threads
#     start_peer_servers(peers)

#     # Download chunks
#     download_chunks(file_key, peers)

# if __name__ == "__main__":
#     main()
