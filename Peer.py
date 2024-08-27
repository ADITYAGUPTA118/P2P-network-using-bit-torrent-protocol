# import socket
# import threading

# class Peer:
#     def __init__(self, name, ip, port):
#         self.name = name
#         self.peer_id = f"{ip}:{port}"
#         self.files = []

#     def add_file(self, file_name):
#         if file_name not in self.files:
#             self.files.append(file_name)
    
#     def __str__(self):
#         return f"Peer(name={self.name}, peer_id={self.peer_id}, files={self.files})"

#     def handle_client(conn, addr, file_chunks):
#         """Handle incoming requests."""
#         request = conn.recv(1024).decode()
#         print(f"request {request}")
#         if request.startswith("HAVE_KEY"):
#             file_key = request.split(":")[1]
#             if file_key in file_chunks:
#                 conn.sendall(f"Peer {addr} HAS_KEY {file_key}".encode())
#             else:
#                 conn.sendall(f"Peer {addr} DOES_NOT_HAVE_KEY {file_key}".encode())
#         elif request.startswith("GET_CHUNK"):
#             file_key, chunk_index = request.split(":")[1:]
#             chunk_index = int(chunk_index)
#             if file_key in file_chunks and chunk_index < len(file_chunks[file_key]):
#                 chunk_data = file_chunks[file_key][chunk_index]
#                 conn.sendall(chunk_data)
#             else:
#                 conn.sendall(b"ERROR")
#         else:
#             conn.sendall(b"UNKNOWN_REQUEST")
#         conn.close()

#     def start_peer_server(self,peer_ip, peer_port, file_chunks):
#         """Start a server on the peer to listen for incoming requests."""
#         peer_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         peer_server.bind((peer_ip, peer_port))
#         peer_server.listen()
#         print(f"Peer server listening on {peer_ip}:{peer_port}...")

#         while True:
#             conn, addr = peer_server.accept()
#             thread = threading.Thread(target=self.handle_client, args=(conn, addr, file_chunks))
#             thread.start()

import socket
import threading
import hashlib
import os

class Peer:
    def __init__(self, name, ip, port):
        self.name = name
        self.peer_id = f"{ip}:{port}"
        self.files = []

    def add_file(self, file_name):
        if file_name not in self.files:
            self.files.append(file_name)
    
    def __str__(self):
        return f"Peer(name={self.name}, peer_id={self.peer_id}, files={self.files})"

    def generate_hash(self,file_key, chunk_number):
        """Generate a hash value based on the file_key and chunk_number."""
        data = f"{file_key}_{chunk_number}".encode()
        return hashlib.sha256(data).hexdigest()

    def handle_client(self, conn, addr, file_chunks):
        """Handle incoming requests."""
        request = conn.recv(1024).decode()
        print(f"Received request: {request} from {addr}")
        
        if request.startswith("HAVE_KEY"):
            file_key = request.split(":")[1]
            if file_key in file_chunks:
                conn.sendall(f"Peer {self.peer_id} HAS_KEY {file_key}".encode())
            else:
                conn.sendall(f"Peer {self.peer_id} DOES_NOT_HAVE_KEY {file_key}".encode())

        elif request.startswith("GET_CHUNK"):
            file_key, chunk_index = request.split(":")[1:]
            chunk_index = int(chunk_index)

            # Generate the hash to locate the correct file
            hash_value = self.generate_hash(file_key, chunk_index)
            directory = f"peer_{self.peer_id.replace(':', '_')}"
            file_name = f"{directory}/received_chunk_{hash_value}"

            if os.path.exists(file_name):
                with open(file_name, 'rb') as f:
                    chunk_data = f.read()
                    conn.sendall(chunk_data)
                    print(f"Sent chunk {chunk_index} from file {file_key} to {addr}")
            else:
                print(f"Chunk {chunk_index} for file {file_key} not found.")
                conn.sendall(b"ERROR")

        else:
            conn.sendall(b"UNKNOWN_REQUEST")

        conn.close()

    def start_peer_server(self, peer_ip, peer_port, file_chunks):
        """Start a server on the peer to listen for incoming requests."""
        peer_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_server.bind((peer_ip, peer_port))
        peer_server.listen()
        print(f"Peer server listening on {peer_ip}:{peer_port}...")

        while True:
            conn, addr = peer_server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr, file_chunks))
            thread.start()