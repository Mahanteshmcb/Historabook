from datasketch import MinHash
import re

def create_minhash(text: str, num_perm: int = 128) -> list:
    """
    Creates a MinHash signature for the given text.
    Returns a list of integers (the signature).
    """
    m = MinHash(num_perm=num_perm)
    
    # Simple tokenization: split by whitespace, lowercase
    tokens = set(re.split(r'\W+', text.lower()))
    
    for token in tokens:
        if token:
            m.update(token.encode('utf8'))
            
    # Return the hash values as a standard list (so it can be stored as JSON)
    return m.hashvalues.tolist()