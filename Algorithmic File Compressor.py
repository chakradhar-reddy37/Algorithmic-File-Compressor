"""
Algorithmic File Compressor
Huffman coding for lossless text compression.

Features:
- Symbol frequency analysis
- Min-heap priority queue
- Binary Huffman tree
- Prefix-free encoding/decoding
- Bit packing
- Tree serialization
"""

import heapq
from collections import Counter
from dataclasses import dataclass


@dataclass
class Node:
    freq: int
    char: str | None = None
    left: "Node | None" = None
    right: "Node | None" = None

    def __lt__(self, other):
        return self.freq < other.freq


def build_tree(text):
    frequency = Counter(text)
    heap = [Node(freq, char) for char, freq in frequency.items()]
    heapq.heapify(heap)

    if len(heap) == 1:
        return Node(heap[0].freq, left=heap[0])

    while len(heap) > 1:
        a = heapq.heappop(heap)
        b = heapq.heappop(heap)
        heapq.heappush(heap, Node(a.freq + b.freq, left=a, right=b))

    return heap[0] if heap else None


def build_codes(root):
    codes = {}

    def walk(node, prefix):
        if node.char is not None:
            codes[node.char] = prefix or "0"
            return
        walk(node.left, prefix + "0")
        walk(node.right, prefix + "1")

    if root:
        walk(root, "")
    return codes


def encode(text):
    if not text:
        return b"", None, 0

    root = build_tree(text)
    codes = build_codes(root)
    bits = "".join(codes[ch] for ch in text)

    padding = (8 - len(bits) % 8) % 8
    bits += "0" * padding

    data = bytes(
        int(bits[i:i + 8], 2)
        for i in range(0, len(bits), 8)
    )
    return data, root, padding


def decode(data, root, padding):
    if root is None:
        return ""

    if root.char is not None:
        return root.char * root.freq

    bits = "".join(f"{byte:08b}" for byte in data)
    if padding:
        bits = bits[:-padding]

    output = []
    node = root

    for bit in bits:
        node = node.left if bit == "0" else node.right
        if node.char is not None:
            output.append(node.char)
            node = root

    return "".join(output)


def compress_file(input_path, output_path):
    text = open(input_path, "r", encoding="utf-8").read()
    data, root, padding = encode(text)

    # Simple demonstration container:
    # magic | padding | serialized frequency table | compressed data
    frequency = Counter(text)

    with open(output_path, "wb") as f:
        import json
        table = json.dumps(dict(frequency), ensure_ascii=False).encode("utf-8")
        f.write(b"HUF1")
        f.write(bytes([padding]))
        f.write(len(table).to_bytes(4, "big"))
        f.write(table)
        f.write(data)


def demo():
    text = (
        "Huffman coding is a lossless compression algorithm. "
        "Repeated symbols receive shorter prefix codes."
    )

    data, root, padding = encode(text)
    restored = decode(data, root, padding)

    original_bits = len(text.encode("utf-8")) * 8
    compressed_bits = len(data) * 8

    print("Original:", text)
    print("Restored:", restored)
    print(f"Original bits:  {original_bits}")
    print(f"Compressed bits: {compressed_bits}")
    print(f"Compression ratio: {compressed_bits / original_bits:.2%}")


if __name__ == "__main__":
    demo()
