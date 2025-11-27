def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100):
    """
    Splits text into chunks of `chunk_size` characters with `overlap`.
    Simple sliding window approach.
    """
    if not text:
        return []
        
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        
        # Determine the slice
        chunk_content = text[start:end]
        chunks.append(chunk_content)
        
        # Stop if we reached the end
        if end >= text_len:
            break
            
        # Move the window forward, but step back by 'overlap' amount
        start += (chunk_size - overlap)
        
    return chunks