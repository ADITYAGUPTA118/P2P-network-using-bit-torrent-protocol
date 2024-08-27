import socket
import threading
from constants import PORT, INITIAL_REPUTATION
from Peer import Peer
from DistributedHashTable import DistributedHashTable
import json

class BitTorrentServer:
    def __init__(self):
        self.port = PORT
        self.initial_reputation = INITIAL_REPUTATION
        self.peers = {}
        self.reputations = {}  # Dictionary to store peer reputations
        self.dht = DistributedHashTable()  # Initialize DHT
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def handle_client(self, conn, addr):
        """Handles a new peer connection and requests."""
        print(f"New connection from {addr}")

        # Receive the request
        request = conn.recv(1024).decode()
        
        if request == "GET_PEERS":
            # Handle request for peer list
            response = self.get_peers_list()
            conn.sendall(response.encode())
        elif request == "GET_DHT":
            # Handle request for DHT
            response = self.get_dht()
            conn.sendall(response.encode())
        elif request == "GET_CHUNK_MAPPING":
            #Handle request for DHT Chunk Mapping
            print(request)
            response = self.get_chunk_mapping()
            conn.sendall(response.encode())
        elif request == "GET_REPUTATIONS":
            # Handle request for peer reputations
            response = self.get_reputations()
            conn.sendall(response.encode())
        else:
            peer_id = f"{addr[0]}:{addr[1]}"
            peer_name = f"Peer_{addr[0]}_{addr[1]}"

            if peer_id not in self.peers:
                # Add new Peer object
                new_peer = Peer(name=peer_name, ip=addr[0], port=addr[1])
                self.peers[peer_id] = new_peer
                self.reputations[peer_id] = self.initial_reputation  # Initialize reputation
                print(f"Added new peer: {new_peer}, with initial reputation: {self.initial_reputation}")
            else:
                print(f"Peer {peer_id} already exists: {self.peers[peer_id]}")

            # Send back acknowledgment
            conn.sendall(f"Connected to the tracker. Your ID: {peer_id}".encode())

        # Close the connection
        conn.close()

    def get_peers_list(self):
        """Returns the list of peers along with their reputations."""
        names = [peer.name for peer in self.peers.values()]
        ids = [peer.peer_id for peer in self.peers.values()]
        reputations = [self.reputations.get(peer.peer_id, self.initial_reputation) for peer in self.peers.values()]
        return json.dumps({"names": names, "ids": ids, "reputations": reputations})

    def get_dht(self):
        """Returns the DHT as a JSON string."""
        return self.dht.save()  # Ensure this method returns a JSON string
    
    def get_chunk_mapping(self):
        """Returns the DHT as a JSON string."""
        return self.dht.save_chunk_table()  # Ensure this method returns a JSON string

    def get_reputations(self):
        """Returns the reputation of all peers."""
        return json.dumps(self.reputations)

    def start_server(self):
        """Starts the server to listen for incoming peer connections."""
        self.server.bind(("0.0.0.0", self.port))
        self.server.listen()
        print(f"Server listening on port {self.port}...")

        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()
            print(f"Active connections: {threading.active_count() - 1}")

if __name__ == "__main__":
    tracker_server = BitTorrentServer()
    tracker_server.start_server()
