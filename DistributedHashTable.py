# import json

# class DistributedHashTable:
#     def __init__(self):
#         self.table = {}
#         self.table2 = {}

#     def add_entry(self, file_key, chunk_index, peer_id):
#         if file_key not in self.table:
#             self.table[file_key] = {}
#             self.table2[file_key]={}
#         self.table[file_key][chunk_index] = peer_id
#         self.table2[file_key][peer_id]=chunk_index

#     def get_entry(self, file_key, chunk_index):
#         return self.table.get(file_key, {}).get(chunk_index)
    
#     def get_chunk_entry(self, file_key, peer_id):
#         return self.table2.get(file_key,{}).get(peer_id)

#     def save(self):
#         """Convert the DHT table to a JSON string."""
#         return json.dumps(self.table)
    
#     def save_chunk_table(self):
#         """Convert the DHT table to a JSON string."""
#         return json.dumps(self.table2)

#     def load(self, json_data):
#         """Load the DHT table from a JSON string."""
#         if isinstance(json_data, str):
#             self.table = json.loads(json_data)
#         elif isinstance(json_data, dict):
#             self.table = json_data
#         else:
#             raise TypeError("Expected a JSON string or dictionary for loading DHT")
        
#     def load_chunk_table(self, json_data):
#         """Load the DHT table from a JSON string."""
#         if isinstance(json_data, str):
#             self.table2 = json.loads(json_data)
#         elif isinstance(json_data, dict):
#             self.table2 = json_data
#         else:
#             raise TypeError("Expected a JSON string or dictionary for loading DHT")


import json

class DistributedHashTable:
    def __init__(self):
        self.table = {}
        self.table2 = {}

    def add_entry(self, file_key, chunk_index, peer_id):
        if file_key not in self.table:
            self.table[file_key] = {}
            self.table2[file_key] = {}

        # Store chunk_index -> peer_id in table 1
        self.table[file_key][chunk_index] = peer_id

        # Store peer_id -> list of chunk_indices in table 2
        if peer_id not in self.table2[file_key]:
            self.table2[file_key][peer_id] = []
        self.table2[file_key][peer_id].append(chunk_index)

    def get_entry(self, file_key, chunk_index):
        return self.table.get(file_key, {}).get(chunk_index)
    
    def get_chunk_entry(self, file_key, peer_id):
        return self.table2.get(file_key, {}).get(peer_id)

    def save(self):
        """Convert the DHT table to a JSON string."""
        return json.dumps(self.table)
    
    def save_chunk_table(self):
        """Convert the DHT table to a JSON string."""
        return json.dumps(self.table2)

    def load(self, json_data):
        """Load the DHT table from a JSON string."""
        if isinstance(json_data, str):
            self.table = json.loads(json_data)
        elif isinstance(json_data, dict):
            self.table = json_data
        else:
            raise TypeError("Expected a JSON string or dictionary for loading DHT")
        
    def load_chunk_table(self, json_data):
        """Load the DHT table from a JSON string."""
        if isinstance(json_data, str):
            self.table2 = json.loads(json_data)
        elif isinstance(json_data, dict):
            self.table2 = json_data
        else:
            raise TypeError("Expected a JSON string or dictionary for loading DHT")
