import os
from pathlib import Path
import paq  # Replace with the actual PAQ module

def count_zeros_ones(data):
    ones = sum(byte.bit_count() for byte in data)
    zeros = len(data) * 8 - ones
    return zeros, ones

def create_best_two_byte_variation(input_file, output_dir):
    with open(input_file, 'rb') as f:
        original_data = f.read()

    base_name = Path(input_file).stem
    save_dir = os.path.join(output_dir, f"{base_name}_best_2byte_variation")

    if os.path.isfile(save_dir):
        print(f"Error: '{save_dir}' is a file, not a directory.")
        return 0
    os.makedirs(save_dir, exist_ok=True)

    best_score = -1
    best_data = None
    best_file_name = ""
    total_bytes = len(original_data)

    print("Evaluating 2-byte XOR variations (0 to 65535)...")

    for i in range(0, total_bytes - 1):  # Avoid last byte for 2-byte pair
        orig_pair = original_data[i:i+2]
        if len(orig_pair) < 2:
            continue
        orig_value = int.from_bytes(orig_pair, byteorder='big')

        for xor_val in range(65536):  # 0 to 65535
            modified_data = bytearray(original_data)
            new_val = orig_value ^ xor_val
            modified_data[i:i+2] = new_val.to_bytes(2, byteorder='big')

            zeros, ones = count_zeros_ones(modified_data)
            score = abs(zeros - ones)

            if score > best_score:
                best_score = score
                best_data = bytes(modified_data)
                best_file_name = f"{base_name}_pos{i:04d}_xor{xor_val:05d}.bin"
                print(f"Improved at pos {i}, xor {xor_val}: 0s={zeros}, 1s={ones}, score={score}")

    if best_data:
        out_path = os.path.join(save_dir, best_file_name)
        with open(out_path, 'wb') as f:
            f.write(paq.compress(best_data))
        print(f"\nBest variation saved (compressed): {out_path}")
        return 1

    print("No improvement found.")
    return 0

def extract_paq_compressed_file(input_file, output_dir):
    try:
        if os.path.isfile(output_dir):
            print(f"Error: '{output_dir}' is a file, not a directory.")
            return 0
        os.makedirs(output_dir, exist_ok=True)

        with open(input_file, 'rb') as f:
            compressed_data = f.read()
        decompressed_data = paq.decompress(compressed_data)

        output_name = input("Enter exact output file name (with .bin extension): ").strip()
        if not output_name:
            print("No output name provided. Extraction cancelled.")
            return 0

        output_path = os.path.join(output_dir, output_name)
        with open(output_path, 'wb') as f:
            f.write(decompressed_data)

        print(f"\nExtracted file saved as: {output_path}")
        return 1
    except Exception as e:
        print(f"\nDecompression failed: {e}")
        return 0

def main():
    print("\n2-Byte XOR Variation Evaluator")
    print("==============================")
    print("1. Save variation with highest 0/1 imbalance and compress (PAQ)")
    print("2. Extract (decompress) using PAQ")
    print("3. Exit")

    choice = input("Choose option (1-3): ").strip()
    if choice not in {'1', '2'}:
        print("Exiting.")
        return

    input_file = input("Enter input file path: ").strip()
    if not os.path.isfile(input_file):
        print("Error: File not found!")
        return

    output_dir = input("Enter output directory [default: current]: ").strip() or "."

    if choice == '1':
        result = create_best_two_byte_variation(input_file, output_dir)
    elif choice == '2':
        result = extract_paq_compressed_file(input_file, output_dir)

    print(f"\nTotal saved: {result}")

if __name__ == "__main__":
    main()