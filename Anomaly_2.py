import os
import paq
from pathlib import Path

def count_zeros_ones(data):
    """Count the number of 0s and 1s in the binary representation of compressed data."""
    bits = ''.join(f'{byte:08b}' for byte in data)
    zeros = bits.count('0')
    ones = bits.count('1')
    return zeros, ones

def create_byte_xor_best_variation(input_file, output_dir):
    """Create XOR variations per byte, compress, and save only the best variation."""
    with open(input_file, 'rb') as f:
        original_data = f.read()

    base_name = Path(input_file).stem
    xor_folder = os.path.join(output_dir, f"{base_name}_xor_output")
    os.makedirs(xor_folder, exist_ok=True)

    best_score = -1
    best_combined_data = None
    best_byte_pos = None
    best_xor_val = None

    for byte_pos in range(len(original_data)):
        original_byte = original_data[byte_pos]
        for xor_val in range(256):
            modified = bytearray(original_data)
            modified[byte_pos] = original_byte ^ xor_val
            try:
                compressed = paq.compress(bytes(modified))
            except Exception as e:
                print(f"Compression error: {e}")
                continue

            zeros, ones = count_zeros_ones(compressed)
            score = zeros + ones
            if score > best_score:
                best_score = score
                best_combined_data = compressed
                best_byte_pos = byte_pos
                best_xor_val = xor_val
                print(f"Improved: byte {byte_pos}, xor {xor_val} → bits: {score} (0s: {zeros}, 1s: {ones})")

    if best_combined_data is not None:
        meta = best_byte_pos.to_bytes(4, 'big') + best_xor_val.to_bytes(1, 'big')
        with open(os.path.join(xor_folder, f"{base_name}_compressed.bin"), 'wb') as f:
            f.write(meta + best_combined_data)
        print(f"\nSaved compressed file with metadata at byte {best_byte_pos}, xor {best_xor_val}")
        return 1
    else:
        print("No variation improved the compression.")
        return 0

def extract_original_file(input_file, output_dir):
    """Extract original file using metadata and decompression."""
    with open(input_file, 'rb') as f:
        meta = f.read(5)
        byte_pos = int.from_bytes(meta[:4], 'big')
        xor_val = meta[4]
        compressed = f.read()

    try:
        decompressed = bytearray(paq.decompress(compressed))
    except Exception as e:
        print(f"Decompression error: {e}")
        return 0

    if byte_pos < len(decompressed):
        decompressed[byte_pos] ^= xor_val
    else:
        print("Metadata byte position is out of bounds.")
        return 0

    out_name = Path(input_file).stem + "_extracted.bin"
    out_path = os.path.join(output_dir, out_name)
    with open(out_path, 'wb') as f:
        f.write(decompressed)

    print(f"Extraction complete. Saved original file to: {out_path}")
    return 1

def main():
    print("Select an option:")
    print("1 - Compress with XOR variation")
    print("2 - Extract original file")
    option = input("Enter 1 or 2: ").strip()

    input_file = input("Enter input file path: ").strip()
    output_dir = input("Enter output directory [default: current]: ").strip() or "."

    if not os.path.isfile(input_file):
        print("File not found!")
        return

    os.makedirs(output_dir, exist_ok=True)

    if option == "1":
        result = create_byte_xor_best_variation(input_file, output_dir)
    elif option == "2":
        result = extract_original_file(input_file, output_dir)
    else:
        print("Invalid option.")
        return

    print(f"\nOperation finished. Success: {bool(result)}")

if __name__ == "__main__":
    main()