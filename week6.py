import collections
import heapq
import struct
import time
import random
import string
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, Tuple, Union, Literal
from matplotlib.widgets import CheckButtons
from collections import deque
# Existing encoder implementations
def build_tree_codes(freq: Dict[int, int]) -> Dict[int, Tuple[int, int]]:
    pq = []
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
    codes = {}
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
def build_tree_codes_linear(freq_dict):
    # freq_dict: only symbols with count>0
    # 1) Seed leaves queue with (freq, symbol)
    leaves = deque(sorted((cnt, sym) for sym, cnt in freq_dict.items()))
    intern = deque()

    def pop_small():
        if not intern or (leaves and leaves[0][0] <= intern[0][0]):
            return leaves.popleft()
        else:
            return intern.popleft()

    # 2) Merge until one tree remains
    while len(leaves) + len(intern) > 1:
        f1, a = pop_small()
        f2, b = pop_small()
        intern.append((f1 + f2, (a, b)))

    # 3) Extract the root node
    root = (leaves or intern)[0][1]

    # 4) Walk it iteratively to assign codes
    codes = {}
    stack = [(root, 0, 0)]
    while stack:
        node, code, depth = stack.pop()
        if isinstance(node, int):
            codes[node] = (code, depth or 1)
        else:
            left, right = node
            # push right first so left ends up with the shorter stack
            stack.append((right, (code << 1) | 1, depth + 1))
            stack.append((left,  code << 1,       depth + 1))

    return codes
def huffman_encode_opt(data: bytes) -> bytes:
    if not data:
        return b""

    # 1) freq in a local list
    freq = [0] * 256
    for b in data:
        freq[b] += 1
    freq_dict = {i: f for i, f in enumerate(freq) if f > 0}

    # 2) build codes with linear‐time method
    codes = build_tree_codes_linear(freq_dict)

    # 3) flatten into arrays for O(1) lookup
    code_ints = [0] * 256
    code_lens = [0] * 256
    for sym, (ci, ln) in codes.items():
        code_ints[sym] = ci
        code_lens[sym] = ln

    # 4) header: use local variables
    hdr = bytearray()
    a = hdr.append
    a(len(codes))
    for sym in range(256):
        ln = code_lens[sym]
        if ln:
            a(sym); a(ln)
            cnt = freq[sym]
            a((cnt >> 24) & 0xFF)
            a((cnt >> 16) & 0xFF)
            a((cnt >> 8 ) & 0xFF)
            a(cnt & 0xFF)

    # 5) bit‐buffer: bind locals for speed
    bitbuf = bytearray()
    bb = bitbuf.append
    cur = 0
    bits = 0
    ci_arr = code_ints
    ln_arr = code_lens

    for b in data:
        ci = ci_arr[b]
        ln = ln_arr[b]
        cur = (cur << ln) | ci
        bits += ln
        # flush bytes
        while bits >= 8:
            bits -= 8
            bb((cur >> bits) & 0xFF)

    if bits:
        bb((cur << (8 - bits)) & 0xFF)

    a(bits)
    return bytes(hdr) + bytes(bitbuf)

def rle_encode_opt(data: Union[str, bytes]) -> bytes:
    """
    Run‐length encode the input, but only emit runs when the 
    encoded form (marker + length + byte = 3 bytes) is smaller
    than the literal form (run_len bytes). Otherwise, emit
    raw bytes as literals.

    Format:
      0x00, <run_len>, <byte>    – an encoded run
      0x01, <lit_len>, <bytes…>   – a literal block
    """
    if isinstance(data, str):
        data = data.encode('utf-8')

    out = bytearray()
    i, n = 0, len(data)
    overhead_bytes = 3      # marker + length + byte
    overhead_bits = overhead_bytes * 8

    while i < n:
        # 1) measure the next run (up to 255)
        run_byte = data[i]
        run_len = 1
        while run_len < 255 and i + run_len < n and data[i + run_len] == run_byte:
            run_len += 1

        literal_bits = run_len * 8
        encoded_bits = overhead_bits

        if encoded_bits < literal_bits:
            # encode this run in chunks ≤255
            remaining = run_len
            while remaining > 0:
                chunk = min(remaining, 255)
                out.extend((0x00, chunk, run_byte))
                remaining -= chunk
            i += run_len
        else:
            # collect a literal span: this run + any subsequent too-small runs
            lit_start = i
            i += run_len
            while i < n:
                next_byte = data[i]
                look_len = 1
                while look_len < 255 and i + look_len < n and data[i + look_len] == next_byte:
                    look_len += 1
                # stop if the next run would be worthwhile
                if overhead_bits < look_len * 8:
                    break
                i += look_len
            # emit literal block(s) of up to 255 bytes
            lit_chunk = data[lit_start:i]
            pos = 0
            while pos < len(lit_chunk):
                chunk = lit_chunk[pos:pos + 255]
                out.extend((0x01, len(chunk)))
                out.extend(chunk)
                pos += len(chunk)

    return bytes(out)


def rle_encode(data: Union[str, bytes]) -> bytes:
    """
    Run‐length encode the input, emitting (count, byte) for every run,
    even if count == 1. Runs longer than 255 are split.
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    out = bytearray()
    i, n = 0, len(data)
    while i < n:
        run_byte = data[i]
        # count how many times data[i] repeats, up to 255
        run_len = 1
        while run_len < 255 and i + run_len < n and data[i + run_len] == run_byte:
            run_len += 1
        # emit the run
        out.append(run_len)
        out.append(run_byte)
        # advance
        i += run_len
    return bytes(out)
def rle_encode_optimized(data: Union[str, bytes]) -> bytes:
    if isinstance(data, str):
        data = data.encode('utf-8')
    out = bytearray()
    i, n = 0, len(data)
    while i < n:
        # count how many times data[i] repeats (up to 255)
        run_byte = data[i]
        run_len = 1
        while run_len < 255 and i + run_len < n and data[i + run_len] == run_byte:
            run_len += 1

        # emit (count, byte)
        out.append(run_len)
        out.append(run_byte)

        # advance past the run
        i += run_len

    return bytes(out)


def make_bitmap(w: int, h: int, pattern: Literal['checker','stripes','random']='checker') -> bytes:
    if pattern == 'checker':
        return bytes(((x ^ y) & 1) for y in range(h) for x in range(w))
    elif pattern == 'stripes':
        return bytes((y & 1) for y in range(h) for x in range(w))
    elif pattern == 'random':
        return bytes(random.getrandbits(1) for _ in range(w*h))
    else:
        raise ValueError("pattern must be 'checker','stripes', or 'random'")


def make_text(n: int, repetitive: bool=False) -> bytes:
    if repetitive:
        letters = (string.ascii_uppercase + ' ').encode()
        out = bytearray()
        MIN_RUN, MAX_RUN = 8, 24
        while len(out) < n:
            byte = random.choice(letters)
            run_len = random.randint(MIN_RUN, MAX_RUN)
            out.extend([byte]*run_len)
        return bytes(out[:n])
    else:
        letters = (string.ascii_lowercase + ' ').encode()
        return bytes(random.choice(letters) for _ in range(n))


def benchmark_encoder(encoder, data):
    t0 = time.perf_counter()
    out = encoder(data)
    dt = (time.perf_counter() - t0) * 1e3
    return len(data), len(out), len(out)/len(data), dt



def phase_one():
    sizes = [2**k for k in range(10, 17)]  # 1 KB to 64 KB
    patterns = [
        ('striped_bitmap', lambda n: make_bitmap(int(n**0.5), int(n**0.5), 'stripes')),
        ('random_bitmap', lambda n: make_bitmap(int(n**0.5), int(n**0.5), 'random')),
        ('repetitive_text', lambda n: make_text(n, True)),
        ('random_text', lambda n: make_text(n, False)),
    ]

    # include both base & optimized encoders
    encoders = (
        huffman_encode,
        huffman_encode_opt,
        rle_encode,
        rle_encode_opt,
    )

    # collect benchmark results
    results = []
    for name, gen in patterns:
        for size in sizes:
            data = gen(size)
            for encoder in encoders:
                in_sz, out_sz, ratio, dt = benchmark_encoder(encoder, data)
                results.append((name, size, encoder.__name__, dt, ratio, out_sz))
                print(f"{name:15s} {encoder.__name__:18s} "
                      f"{in_sz:6d}->{out_sz:6d} ratio={ratio:.2f} time={dt:7.2f}ms")

    # build DataFrame with your desired columns
    df = pd.DataFrame(
        results,
        columns=['datatype', 'input_size', 'encoder', 'time_ms', 'ratio', 'output_size']
    )

    # write it out
    df.to_csv('results.csv', index=False)
    print("Wrote results.csv with columns: datatype,input_size,encoder,time_ms,ratio,output_size")

if __name__ == '__main__':
    phase_one()
