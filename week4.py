import collections, heapq, struct, time, random, stringx
from typing import Dict, List,Tuple,Union, Literal


def build_tree_codes(freq: Dict[int, int]) -> Dict[int, Tuple[int, int]]:
    """
    Build Huffman tree and return {symbol: (code_int, bit_len)}.
    Left child → 0, right child → 1.
    """
    pq: List[Tuple[int, int, object]] = []
    tie = 0
    for sym, fr in freq.items():
        heapq.heappush(pq, (fr, tie, sym))
        tie += 1

    while len(pq) > 1:
        fr1, _, a = heapq.heappop(pq)
        fr2, _, b = heapq.heappop(pq)
        heapq.heappush(pq, (fr1 + fr2, tie, (a, b)))
        tie += 1

    _, _, root = pq[0]

    codes: Dict[int, Tuple[int, int]] = {}

    def walk(node, code=0, depth=0):
        if isinstance(node, int):                    
            codes[node] = (code, depth or 1)         
        else:
            left, right = node
            walk(left,  code << 1,       depth + 1)   
            walk(right, (code << 1) | 1, depth + 1)  

    walk(root)
    return codes

def huffman_encode(data: bytes) -> bytes:
    """
    Compress data with Huffman tree.
    """
    if not data:
        return b""

    
    freq = collections.Counter(data)
    codes = build_tree_codes(freq)           

     
    hdr = bytearray([len(codes)])
    for sym, (code_int, ln) in codes.items():
        hdr.append(sym)                     
        hdr.append(ln)                       
        hdr.extend(struct.pack(">I", freq[sym]))   

    
    bitbuf, cur, bits = bytearray(), 0, 0
    for b in data:
        code_int, ln = codes[b]
        cur = (cur << ln) | code_int
        bits += ln
        while bits >= 8:                    
            bits -= 8
            bitbuf.append((cur >> bits) & 0xFF)

    if bits:                                 
        bitbuf.append((cur << (8 - bits)) & 0xFF)
    hdr.append(bits)                        

    return bytes(hdr) + bytes(bitbuf)




def rle_encode(data: Union[str, bytes], *, min_run: int = 3) -> bytes:
    if isinstance(data, str):
        data = data.encode("utf-8")
        if not data:
            return b""

    out = bytearray()
    i = 0
    n = len(data)

    while i < n:
        run_byte = data[i]
        run_len  = 1
        j        = i + 1
        while j < n and data[j] == run_byte:
            run_len += 1
            j += 1

        if run_len >= min_run:                  
            while run_len > 0:
                chunk = min(run_len, 255)
                out.extend((0x00, chunk, run_byte))
                run_len -= chunk
            i = j
        else:                                  
            lit_start = i
            i = j
            while i < n:
              look_byte = data[i]
              look_len  = 1
              k = i + 1
              while k < n and data[k] == look_byte:
                    look_len += 1
                    k += 1
              if look_len >= min_run:
                    break
              i += look_len

            lit_chunk = data[lit_start:i]
            pos = 0
            while pos < len(lit_chunk):
                chunk = lit_chunk[pos:pos+255]
                out.extend((0x01, len(chunk)))
                out.extend(chunk)
                pos += 255

    return bytes(out)

def make_bitmap(
    w: int,
    h: int,
    pattern: Literal["checker", "stripes", "random"] = "checker"
) -> bytes:
    """
    Generate a w×h 1-bit bitmap.

    Args:
        w, h (int):  width and height in pixels.
        pattern (str):  "checker", "stripes", or "random".

    Returns:
        bytes: pixel stream where each byte is 0 or 1.
    """
    if pattern == "checker":
        return bytes(((x ^ y) & 1) for y in range(h) for x in range(w))

    elif pattern == "stripes":
    # horizontal stripes – alternate every row
        return bytes((y & 1) for y in range(h) for x in range(w))

    elif pattern == "random":
        return bytes(random.getrandbits(1) for _ in range(w * h))

    else:
        raise ValueError("pattern must be 'checker', 'stripes', or 'random'")


def make_text(n: int, repetitive=False) -> bytes:
    """
    Generates a sequence of bytes representing text.

    Args:
        n (int): The desired length of the output byte sequence.
        repetitive (bool, optional): If True, generates repetitive patterns 
            using uppercase letters (A-Z) and spaces. If False, generates 
            non-repetitive text using lowercase letters (a-z) and spaces. 
            Defaults to False.

    Returns:
        bytes: A byte sequence of length n containing the generated text.
"""
    if repetitive:
            letters = (string.ascii_uppercase + " ").encode()  # pick from A-Z and space
            out = bytearray()

            MIN_RUN, MAX_RUN = 8, 24                     
            while len(out) < n:
                byte = random.choice(letters)          
                run_len = random.randint(MIN_RUN, MAX_RUN)
                out.extend([byte] * run_len)                
            return bytes(out[:n])                           
    else:
        letters = (string.ascii_lowercase + " ").encode()
        return bytes(random.choice(letters) for _ in range(n))


def benchmark(encoder: bytes, data: bytes) -> None:
    """
    Measures and prints the performance of a given encoder function.

    Args:
        encoder (Callable[[bytes], bytes]): A function that takes a bytes object as input
            and returns a bytes object as output (e.g., a compression or encoding function).
        data (bytes): The input data to be processed by the encoder.

    Prints:
        A formatted string containing:
        - The name of the encoder function.
        - The size of the input data in bytes.
        - The size of the encoded output in bytes.
        - The compression/encoding ratio (output size / input size).
        - The time taken to encode the data in milliseconds.
    """
    t0 = time.perf_counter()
    blob = encoder(data)
    dt = (time.perf_counter() - t0) * 1e3
    print(f"{encoder.__name__:15s}  "
          f"{len(data):8d} -> {len(blob):8d} "
          f"ratio={len(blob)/len(data):5.2f}  {dt:6.2f} ms")


if __name__ == "__main__":
    
    bmp = make_bitmap(255, 255, pattern="stripes")           
    rep_txt = make_text(20000, repetitive=True)
    random_txt = make_text(20000, repetitive=False)
    random_bmp = make_bitmap(255, 255, pattern="random")

    print("--- striped bitmap (stripes) ---")
    benchmark(huffman_encode, bmp)
    benchmark(rle_encode,bmp)

    print("\n--- repetitive text ---")
    benchmark(huffman_encode, rep_txt)
    benchmark(rle_encode, rep_txt)
    
    print("\n--- random text ---")
    benchmark(huffman_encode, random_txt)
    benchmark(rle_encode, random_txt)

    print("\n--- random bitmap ---")
    benchmark(huffman_encode, random_bmp)
    benchmark(rle_encode, random_bmp)

