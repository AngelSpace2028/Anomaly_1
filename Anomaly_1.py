import os
import re
from pathlib import Path

def transform_with_pattern(data, chunk_size=4, xor_value=0xFF):
    """Apply XOR transformation per chunk."""
    transformed = bytearray()
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        transformed.extend([b ^ xor_value & 0xFF for b in chunk])
    return transformed

def extract_xor_info(filename):
    """Extract chunk size and XOR value from filename using a single regex."""
    match = re.search(r'_chunk(\d+)_xor([0-9a-fA-F]{2,})|_xor_(\d{1,3})|_xor(\d{2,3})|_x([0-9a-fA-F]{2})', filename)
    if match:
        if match.group(1):
            chunk_size = int(match.group(1))
            xor_val = int(match.group(2), 16)
        elif match.group(3):
            chunk_size = 4
            xor_val = int(match.group(3))
        elif match.group(4):
            chunk_size = 4
            xor_val = int(match.group(4))
        else:
            chunk_size = 4
            xor_val = int(match.group(5), 16)
        return chunk_size, xor_val
    return 4, 255

def decode_variation_file(input_file, output_dir, file_counter):
    """Decode a single variation file."""
    try:
        with open(input_file, 'rb') as f:
            encoded = f.read()

        chunk_size, xor_val = extract_xor_info(os.path.basename(input_file))
        decoded = transform_with_pattern(encoded, chunk_size, xor_val)

        out_name = f"decoded_{Path(input_file).stem}_{file_counter:04d}.jpg"
        out_path = os.path.join(output_dir, out_name)

        with open(out_path, 'wb') as out_f:
            out_f.write(decoded)

        print(f"  ✓ Decoded: {Path(input_file).name} → {out_name}")
        return True

    except FileNotFoundError:
        print(f"  ✗ Error: File '{input_file}' not found.")
        return False
    except (IOError, OSError) as e:
        print(f"  ✗ Error: An I/O error occurred while processing '{input_file}': {e}")
        return False
    except Exception as e:
        print(f"  ✗ An unexpected error occurred: {e}")
        return False

def encode_to_variations(input_file, output_dir, chunk_size=255):
    """Encodes to XOR variations, saving only best zero and one variations."""
    if not os.path.isfile(input_file):
        print("Error: Input must be a file")
        return 0

    try:
        with open(input_file, 'rb') as f:
            original_data = f.read()

        xor_folder = os.path.join(output_dir, f"{Path(input_file).stem}_xor_variations")
        os.makedirs(xor_folder, exist_ok=True)

        best_zeros = None
        best_ones = None

        for xor_val in range(256):
            transformed = transform_with_pattern(original_data, chunk_size, xor_val)
            most_frequent, count_difference = check_zeros_ones(transformed)

            if most_frequent == 'zeros':
                if best_zeros is None or count_difference > best_zeros[2]:
                    best_zeros = (xor_val, transformed, count_difference)
            elif most_frequent == 'ones':
                if best_ones is None or count_difference > best_ones[2]:
                    best_ones = (xor_val, transformed, count_difference)

        files_saved = 0
        if best_zeros:
            out_name = f"{Path(input_file).stem}_chunk{chunk_size}_xor_{best_zeros[0]:03d}.bin"
            out_path = os.path.join(xor_folder, out_name)
            with open(out_path, 'wb') as f:
                f.write(best_zeros[1])
            print(f"Saved best zeros variation: {out_name}")
            files_saved += 1

        if best_ones:
            out_name = f"{Path(input_file).stem}_chunk{chunk_size}_xor_{best_ones[0]:03d}.bin"
            out_path = os.path.join(xor_folder, out_name)
            with open(out_path, 'wb') as f:
                f.write(best_ones[1])
            print(f"Saved best ones variation: {out_name}")
            files_saved += 1

        return files_saved


    except Exception as e:
        print(f"An error occurred during encoding: {e}")
        return 0


def find_variation_folders(search_root):
    folders = []
    for root, dirs, _ in os.walk(search_root):
        for dir_name in dirs:
            if dir_name.endswith(('_variations', '_xor_variations')):
                folders.append(os.path.join(root, dir_name))
    return folders

def process_all_variation_folders(input_dir, output_dir):
    variation_folders = find_variation_folders(input_dir)

    if not variation_folders:
        print("No variation folders found!")
        return 0

    print("\nFound variation folders:")
    for i, folder in enumerate(variation_folders, 1):
        print(f"  {i}. {folder}")

    total_decoded = 0
    decoded_dir = os.path.join(output_dir, "decoded_results")
    os.makedirs(decoded_dir, exist_ok=True)

    for folder in variation_folders:
        print(f"\nProcessing folder: {folder}")
        file_counter = 0
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                if decode_variation_file(file_path, decoded_dir, file_counter):
                    file_counter += 1
        total_decoded += file_counter
        print(f"Decoded {file_counter} files from this folder")

    print(f"\nTotal decoded files: {total_decoded}")
    print(f"Output directory: {decoded_dir}")
    return total_decoded

def check_zeros_ones(data):
    try:
        if isinstance(data, str):
            with open(data, 'rb') as f:
                data = f.read()
        zeros = data.count(b'\x00')
        ones = len(data) - zeros
        if zeros > ones:
            return 'zeros', zeros - ones
        elif ones > zeros:
            return 'ones', ones - zeros
        else:
            return 'equal', 0
    except FileNotFoundError:
        print(f"Error: File '{data}' not found.")
        return None, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

def check_variations(variations_folder):
    results = {}
    best_zeros = None
    best_ones = None

    for filename in os.listdir(variations_folder):
        filepath = os.path.join(variations_folder, filename)
        if os.path.isfile(filepath):
            most_frequent, count_difference = check_zeros_ones(filepath)
            if most_frequent is not None:
                results[filename] = (most_frequent, count_difference)
                if most_frequent == 'zeros':
                    if best_zeros is None or count_difference > best_zeros[1]:
                        best_zeros = (filename, count_difference)
                else:
                    if best_ones is None or count_difference > best_ones[1]:
                        best_ones = (filename, count_difference)

    return results, best_zeros, best_ones

def main():
    print("XOR Anomaly Processor")
    print("=" * 40)
    print("1. Encode JPG to XOR variations (chunk size 255, best zero/one only)")
    print("2. Decode from variations folder and check variations")
    print("3. Auto-find and decode ALL variation folders")
    print("4. Check Zeros and Ones in a file")

    choice = input("\nSelect option (1-4): ").strip()
    base_dir = os.path.expanduser("~/storage/emulated/0/Documents")

    if choice == '1':
        input_file = input("Enter JPG file path: ").strip()
        if not os.path.isfile(input_file):
            print("File not found!")
            return
        output_dir = input(f"Output directory [{base_dir}]: ").strip() or base_dir
        files_saved = encode_to_variations(input_file, output_dir)
        print(f"\nDone. Saved {files_saved} variation files.")

    elif choice == '2':
        input_dir = input("Enter variations folder path: ").strip()
        if not os.path.isdir(input_dir):
            print("Folder not found!")
            return
        output_dir = input(f"Output directory [{base_dir}]: ").strip() or base_dir
        process_all_variation_folders(input_dir, output_dir)
        print("\nDone.")

    elif choice == '3':
        search_root = input(f"Search root directory [{base_dir}]: ").strip() or base_dir
        output_dir = input(f"Output directory [{base_dir}]: ").strip() or base_dir
        process_all_variation_folders(search_root, output_dir)
        print("\nDone.")

    elif choice == '4':
        filepath = input("Enter the file path: ")
        most_frequent, count_difference = check_zeros_ones(filepath)
        if most_frequent is not None:
            print(f"The file '{filepath}' contains more {most_frequent}.")
            print(f"Difference: {count_difference}")

    else:
        print("Invalid option")

if __name__ == "__main__":
    main()
