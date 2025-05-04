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
    """Option 1: Create XOR variations per byte, compress, and save only the best variation."""
    if not os.path.isfile(input_file):
        print("Error: Input must be a file")
        return 0

    with open(input_file, 'rb') as f:
        original_data = f.read()

    base_name = Path(input_file).stem
    xor_folder = os.path.join(output_dir, f"{base_name}_best_xor_variation")
    os.makedirs(xor_folder, exist_ok=True)

    best_score = -1
    best_data = None
    best_file_name = ""
    total_bytes = len(original_data)

    print(f"Processing {total_bytes} bytes with 256 XOR variations per byte...")

    for byte_pos in range(total_bytes):
        original_byte = original_data[byte_pos]

        for xor_val in range(256):
            modified_data = bytearray(original_data)
            modified_data[byte_pos] = original_byte ^ xor_val

            try:
                compressed = paq.compress(bytes(modified_data))  # convert to bytes
            except Exception as e:
                print(f"Compression error: {e}")
                continue

            zeros, ones = count_zeros_ones(compressed)
            score = zeros + ones

            if score > best_score:
                best_score = score
                best_data = bytes(modified_data)
                best_file_name = f"{base_name}_byte{byte_pos:04d}_xor{xor_val:03d}.bin"
                print(f"Improved: byte {byte_pos}, xor {xor_val} → bits: {score} (0s: {zeros}, 1s: {ones})")

    if best_data:
        out_path = os.path.join(xor_folder, best_file_name)
        with open(out_path, 'wb') as f:
            f.write(paq.compress(best_data))
        print(f"\nBest variation saved: {out_path}")
        return 1
    else:
        print("No variation produced a better result.")
        return 0

def extract_original_variation(input_file, output_file):
    """Option 2: Decompress a file that was compressed with zlib."""
    if not os.path.isfile(input_file):
        print("Error: File not found")
        return

    with open(input_file, 'rb') as f:
        compressed_data = f.read()

    try:
        decompressed_data = paq.decompress(compressed_data)
    except zlib.error as e:
        print(f"Decompression error: {e}")
        return

    with open(output_file, 'wb') as f:
        f.write(decompressed_data)

    print(f"Decompressed file saved as: {output_file}")

def main():
    print("Choose an option:")
    print("1. Compress (XOR variation with zlib)")
    print("2. Extract (zlib decompression)")
    choice = input("Enter 1 or 2: ").strip()

    if choice == '1':
        input_file = input("Enter input file path: ").strip()
        output_dir = input("Enter output directory [default: current]: ").strip() or "."
        os.makedirs(output_dir, exist_ok=True)
        result = create_byte_xor_best_variation(input_file, output_dir)
        print(f"\nTotal best files saved: {result}")

    elif choice == '2':
        input_file = input("Enter compressed file path: ").strip()
        output_file = input("Enter output (decompressed) file name: ").strip()
        extract_original_variation(input_file, output_file)

    else:
        print("Invalid option selected.")

if __name__ == "__main__":
    main()