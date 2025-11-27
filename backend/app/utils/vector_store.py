import faiss  # type: ignore
import numpy as np
import os
import pickle

INDEX_FILE = "vector_store.index"
ID_MAP_FILE = "id_map.pkl"

class VectorStore:
    def __init__(self):
        # 384 is the dimension of 'all-MiniLM-L6-v2'
        self.dimension = 384
        self.index = faiss.IndexFlatL2(self.dimension)
        self.id_map = {}  # Maps integer ID (0,1,2) -> Chunk UUID ("c1-...")
        
        self.load_index()

    def add_vectors(self, vectors: list, chunk_ids: list):
        """
        vectors: List of list of floats
        chunk_ids: List of strings (UUIDs)
        """
        if not vectors:
            return
            
        np_vectors = np.array(vectors).astype('float32')
        
        # Current count is the starting ID for these new vectors
        start_id = self.index.ntotal
        
        # Add to FAISS
        # Pylance often struggles with C++ bindings, so we ignore the error
        self.index.add(np_vectors) # type: ignore
        
        # Update map
        for i, chunk_id in enumerate(chunk_ids):
            self.id_map[start_id + i] = chunk_id
            
        self.save_index()

    def search(self, query_vector: list, k: int = 5):
        """Returns list of (chunk_id, distance)"""
        np_vector = np.array([query_vector]).astype('float32')
        
        # D = distances, I = indices (IDs)
        # Pylance expects C++ inputs, but Python wrapper returns tuple. Ignore error.
        D, I = self.index.search(np_vector, k) # type: ignore
        
        results = []
        for i, idx in enumerate(I[0]):
            if idx != -1 and idx in self.id_map:
                results.append((self.id_map[idx], float(D[0][i])))
                
        return results

    def save_index(self):
        faiss.write_index(self.index, INDEX_FILE)
        with open(ID_MAP_FILE, "wb") as f:
            pickle.dump(self.id_map, f)

    def load_index(self):
        if os.path.exists(INDEX_FILE) and os.path.exists(ID_MAP_FILE):
            self.index = faiss.read_index(INDEX_FILE)
            with open(ID_MAP_FILE, "rb") as f:
                self.id_map = pickle.load(f)

# Global instance
vector_store = VectorStore()