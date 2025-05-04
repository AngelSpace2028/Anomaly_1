import os
import paq  # Ensure you have this module or replace with actual PAQ interface
from pathlib import Path

def count_zeros_ones(data):
    bits = ''.join(f'{byte:08b}' for byte in data)
    return bits.count('0'), bits.count('1')

def create_best_zero_one_variation(input_file, output_dir):
    with open(input_file, 'rb') as f:
        original_data = f.read()

    base_name = Path(input_file).stem
    save_dir = os.path.join(output_dir, f"{base_name}_most_zeros_ones")
    
    if os.path.isfile(save_dir):
        print(f"Error: '{save_dir}' is a file, not a directory.")
        return 0
    os.makedirs(save_dir, exist_ok=True)

    best_score = -1
    best_data = None
    best_file_name = ""
    total_bytes = len(original_data)

    print("Evaluating variations for most zeros + ones...")

    for byte_pos in range(total_bytes):
        original_byte = original_data[byte_pos]
        for xor_val in range(256):
            modified_data = bytearray(original_data)
            modified_data[byte_pos] = original_byte ^ xor_val

            zeros, ones = count_zeros_ones(modified_data)
            score = zeros + ones

            if score > best_score:
                best_score = score
                best_data = bytes(modified_data)  # Ensure it's bytes for compression
                best_file_name = f"{base_name}_byte{byte_pos:04d}_xor{xor_val:03d}.bin"
                print(f"Improved: byte {byte_pos}, xor {xor_val} → score: {score}")

    if best_data:
        out_path = os.path.join(save_dir, best_file_name)
        with open(out_path, 'wb') as f:
            f.write(paq.compress(best_data))
        print(f"\nSaved best zero/one variation (compressed): {out_path}")
        return 1
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
    print("\nXOR Variation Evaluator")
    print("=========================")
    print("1. Save variation with most zeros + ones and compress (PAQ)")
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
        result = create_best_zero_one_variation(input_file, output_dir)
    elif choice == '2':
        result = extract_paq_compressed_file(input_file, output_dir)

    print(f"\nTotal saved: {result}")

if __name__ == "__main__":
    main()