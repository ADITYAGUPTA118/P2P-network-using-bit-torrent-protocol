# import sys
# import socket
# import json
# import threading
# import os
# import math
# from DistributedHashTable import DistributedHashTable

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
#     """Fetch data (peers or DHT) from the central server."""
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

# def divide_file_into_chunks(file_path, chunk_size=32 * 1024):
#     """Divide the file into chunks."""
#     chunks = []
#     with open(file_path, 'rb') as file:
#         while chunk := file.read(chunk_size):
#             chunks.append(chunk)
#     return chunks

# # def store_chunks_on_peers(chunks, peers, dht, file_key, reputations):
# #     """Distribute chunks to peers based on reputation and update DHT."""
# #     total_reputation = sum(reputations.values())
# #     for i, chunk in enumerate(chunks):
# #         # Select peer based on reputation proportion
# #         peer = max(peers, key=lambda p: reputations[f"{p['ip']}:{p['port']}"])
# #         peer_id = f"{peer['ip']}:{peer['port']}"
        
# #         try:
# #             with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
# #                 s.connect((peer['ip'], peer['port']))
# #                 s.sendall(chunk)
# #                 response = s.recv(1024).decode()
# #                 if response == "ACK":
# #                     dht.add_entry(file_key, i, peer_id)
# #                     print(f"Chunk {i} stored on {peer_id}")
# #                 else:
# #                     print(f"Failed to store chunk {i} on {peer_id}")
# #                     reputations[peer_id] -= 1  # Decrease reputation on failure
# #         except socket.error as e:
# #             print(f"Error sending chunk {i} to {peer_id}: {e}")
# #             reputations[peer_id] -= 1  # Decrease reputation on failure

# def store_chunks_on_peers(chunks, peers, dht, file_key, reputations):
#     """Distribute chunks to peers based on reputation and update DHT."""
#     total_reputation = sum(reputations.values())
#     total_chunks = len(chunks)
    
#     # Calculate the number of chunks each peer should get
#     peer_chunk_counts = {}
#     remaining_chunks = total_chunks  # Tracks chunks left to allocate
    
#     for peer in peers:
#         peer_id = f"{peer['ip']}:{peer['port']}"
#         peer_reputation = reputations[peer_id]
        
#         # Calculate chunks to allocate to this peer based on its reputation
#         chunks_for_peer = math.floor((peer_reputation / total_reputation) * total_chunks)
#         peer_chunk_counts[peer_id] = chunks_for_peer
#         remaining_chunks -= chunks_for_peer
    
#     # Distribute any remaining chunks (due to rounding down)
#     while remaining_chunks > 0:
#         # Find the peer with the highest reputation that hasn't received all its chunks
#         peer_id = max(peer_chunk_counts, key=lambda p: reputations[p] if peer_chunk_counts[p] < total_chunks else -1)
#         peer_chunk_counts[peer_id] += 1
#         remaining_chunks -= 1

#     # Distribute the chunks according to the calculated counts
#     chunk_index = 0
#     for peer in peers:
#         peer_id = f"{peer['ip']}:{peer['port']}"
#         for _ in range(peer_chunk_counts[peer_id]):
#             chunk = chunks[chunk_index]
#             try:
#                 with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#                     s.connect((peer['ip'], peer['port']))
#                     s.sendall(chunk)
#                     response = s.recv(1024).decode()
#                     if response == "ACK":
#                         dht.add_entry(file_key, chunk_index, peer_id)
#                         print(f"Chunk {chunk_index} stored on {peer_id}")
#                     else:
#                         print(f"Failed to store chunk {chunk_index} on {peer_id}")
#                         reputations[peer_id] -= 1  # Decrease reputation on failure
#             except socket.error as e:
#                 print(f"Error sending chunk {chunk_index} to {peer_id}: {e}")
#                 reputations[peer_id] -= 1  # Decrease reputation on failure
            
#             chunk_index += 1

# def process_peers_data(peers_data):
#     """Convert peers_data into a list of dictionaries with IP and port."""
#     peers = []
#     for peer_id in peers_data["ids"]:
#         ip, port = peer_id.split(":")
#         peers.append({"ip": ip, "port": int(port)})
#     return peers

# def main():
#     if len(sys.argv) != 2:
#         print("Usage: python uploadChunks.py <file_key>")
#         sys.exit(1)

#     file_key = sys.argv[1]
#     server_ip = "192.168.0.103"  # Replace with the actual server IP
#     server_port = 5000  # Replace with the actual server port
    
#     # Fetch peer list, DHT, and reputations from the server
#     peers_data = fetch_from_server(server_ip, server_port, "GET_PEERS")
#     dht_data = fetch_from_server(server_ip, server_port, "GET_DHT")
#     chunk_mapping =fetch_from_server(server_ip,server_port,"GET_CHUNK_MAPPING")
#     reputations_data = fetch_from_server(server_ip, server_port, "GET_REPUTATIONS")
#     print(reputations_data)
#     # Process peers_data
#     peers = process_peers_data(peers_data)
#     reputations = reputations_data
    
#     # Start peer servers in separate threads
#     for peer in peers:
#         threading.Thread(target=start_peer_server, args=(peer['ip'], peer['port'])).start()

#     # Divide the file into chunks
#     file_path = "statement.pdf"  # Replace with the actual file path
#     chunks = divide_file_into_chunks(file_path)
    
#     # Load DHT from server data
#     dht = DistributedHashTable()
#     dht.load(dht_data)
#     dht.load_chunk_table(chunk_mapping)

#     # Store chunks on peers based on reputation
#     store_chunks_on_peers(chunks, peers, dht, file_key, reputations)
    
#     # Optionally save DHT to a file for future reference
#     with open('chunksToPeer.json', 'w') as f:
#         f.write(dht.save())

#     with open('PeerToChunk.json', 'w') as f:
#         f.write(dht.save_chunk_table())

# if __name__ == "__main__":
#     main()

import sys
import socket
import json
import threading
import os
import math
import hashlib
from DistributedHashTable import DistributedHashTable

def generate_hash(file_key, chunk_number):
    """Generate a hash value based on the file_key and chunk_number."""
    data = f"{file_key}_{chunk_number}".encode()
    return hashlib.sha256(data).hexdigest()

def start_peer_server(peer_ip, peer_port):
    """Start a server on the peer to listen for incoming chunks."""
    def handle_client(conn, addr):
        """Handle incoming chunk."""
        chunk_data = conn.recv(4096)
        
        # Extract the metadata and chunk data
        file_key, chunk_number, actual_chunk_data = chunk_data.split(b":", 2)
        # print(f"file key {file_key}, chunk_index {chunk_number}")
        file_key = file_key.decode()
        chunk_number = chunk_number.decode()
        hash_value = generate_hash(file_key, chunk_number)
        
        directory = f"peer_{peer_ip}_{peer_port}"
        os.makedirs(directory, exist_ok=True)
        
        file_name = f"{directory}/received_chunk_{hash_value}"
        with open(file_name, 'wb') as f:
            f.write(actual_chunk_data)  # Write the binary chunk data
        
        conn.sendall(b"ACK")
        conn.close()

    peer_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_server.bind((peer_ip, peer_port))
    peer_server.listen()
    print(f"Peer server listening on {peer_ip}:{peer_port}...")

    while True:
        conn, addr = peer_server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

def fetch_from_server(server_ip, server_port, request_type):
    """Fetch data (peers or DHT) from the central server."""
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

def divide_file_into_chunks(file_path, chunk_size=32 * 1024):
    """Divide the file into chunks."""
    chunks = []
    with open(file_path, 'rb') as file:
        while chunk := file.read(chunk_size):
            chunks.append(chunk)
    return chunks


def store_chunks_on_peers(chunks, peers, dht, file_key, reputations):
    """Distribute chunks to peers based on reputation and update DHT."""
    total_reputation = sum(reputations.values())
    total_chunks = len(chunks)
    
    # Calculate the number of chunks each peer should get
    peer_chunk_counts = {}
    remaining_chunks = total_chunks  # Tracks chunks left to allocate
    
    for peer in peers:
        peer_id = f"{peer['ip']}:{peer['port']}"
        peer_reputation = reputations[peer_id]
        
        # Calculate chunks to allocate to this peer based on its reputation
        chunks_for_peer = math.floor((peer_reputation / total_reputation) * total_chunks)
        peer_chunk_counts[peer_id] = chunks_for_peer
        remaining_chunks -= chunks_for_peer
    
    # Distribute any remaining chunks (due to rounding down)
    while remaining_chunks > 0:
        # Find the peer with the highest reputation that hasn't received all its chunks
        peer_id = max(peer_chunk_counts, key=lambda p: reputations[p] if peer_chunk_counts[p] < total_chunks else -1)
        peer_chunk_counts[peer_id] += 1
        remaining_chunks -= 1

    # Distribute the chunks according to the calculated counts
    chunk_index = 0
    for peer in peers:
        peer_id = f"{peer['ip']}:{peer['port']}"
        for _ in range(peer_chunk_counts[peer_id]):
            chunk = chunks[chunk_index]
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((peer['ip'], peer['port']))
                    
                    # Prepare the message with metadata and chunk data
                    message = f"{file_key}:{chunk_index}:".encode() + chunk
                    
                    s.sendall(message)
                    response = s.recv(1024).decode()
                    if response == "ACK":
                        dht.add_entry(file_key, chunk_index, peer_id)
                        print(f"Chunk {chunk_index} stored on {peer_id}")
                    else:
                        print(f"Failed to store chunk {chunk_index} on {peer_id}")
                        reputations[peer_id] -= 1  # Decrease reputation on failure
            except socket.error as e:
                print(f"Error sending chunk {chunk_index} to {peer_id}: {e}")
                reputations[peer_id] -= 1  # Decrease reputation on failure
            
            chunk_index += 1

def process_peers_data(peers_data):
    """Convert peers_data into a list of dictionaries with IP and port."""
    peers = []
    for peer_id in peers_data["ids"]:
        ip, port = peer_id.split(":")
        peers.append({"ip": ip, "port": int(port)})
    return peers

def main():
    if len(sys.argv) != 2:
        print("Usage: python uploadChunks.py <file_key>")
        sys.exit(1)

    file_key = sys.argv[1]
    server_ip = "192.168.0.103"  # Replace with the actual server IP
    server_port = 5000  # Replace with the actual server port
    
    # Fetch peer list, DHT, and reputations from the server
    peers_data = fetch_from_server(server_ip, server_port, "GET_PEERS")
    dht_data = fetch_from_server(server_ip, server_port, "GET_DHT")
    chunk_mapping =fetch_from_server(server_ip,server_port,"GET_CHUNK_MAPPING")
    reputations_data = fetch_from_server(server_ip, server_port, "GET_REPUTATIONS")
    print(reputations_data)
    # Process peers_data
    peers = process_peers_data(peers_data)
    reputations = reputations_data
    
    # Start peer servers in separate threads
    for peer in peers:
        threading.Thread(target=start_peer_server, args=(peer['ip'], peer['port'])).start()

    # Divide the file into chunks
    file_path = "large_random_file.bin"  # Replace with the actual file path
    chunks = divide_file_into_chunks(file_path)
    
    # Load DHT from server data
    dht = DistributedHashTable()
    dht.load(dht_data)
    dht.load_chunk_table(chunk_mapping)

    # Store chunks on peers based on reputation
    store_chunks_on_peers(chunks, peers, dht, file_key, reputations)
    
    # Optionally save DHT to a file for future reference
    with open('chunksToPeer.json', 'w') as f:
        f.write(dht.save())

    with open('PeerToChunk.json', 'w') as f:
        f.write(dht.save_chunk_table())

if __name__ == "__main__":
    main()
