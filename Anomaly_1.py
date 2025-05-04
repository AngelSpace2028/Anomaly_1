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
    """Extract chunk size and XOR value from filename."""
    # Try different filename patterns
    patterns = [
        (r'_chunk(\d+)_xor([0-9a-fA-F]{2,})', lambda m: (int(m.group(1)), int(m.group(2), 16))),
        (r'_xor_(\d{1,3})', lambda m: (4, int(m.group(1)))),
        (r'_xor(\d{2,3})', lambda m: (4, int(m.group(1)))),
        (r'_x([0-9a-fA-F]{2})', lambda m: (4, int(m.group(1), 16)))
    ]
    
    for pattern, handler in patterns:
        match = re.search(pattern, filename)
        if match:
            return handler(match)
    return 4, 255  # Default fallback

def decode_variation_file(input_file, output_dir, file_counter):
    """Decode a single variation file."""
    try:
        with open(input_file, 'rb') as f:
            encoded = f.read()

        chunk_size, xor_val = extract_xor_info(os.path.basename(input_file))
        decoded = transform_with_pattern(encoded, chunk_size, xor_val)

        # Save with original filename + counter
        out_name = f"decoded_{Path(input_file).stem}_{file_counter:04d}.jpg"
        out_path = os.path.join(output_dir, out_name)

        with open(out_path, 'wb') as out_f:
            out_f.write(decoded)

        print(f"  ✓ Decoded: {Path(input_file).name} → {out_name}")
        return True

    except Exception as e:
        print(f"  ✗ Failed: {Path(input_file).name} ({str(e)})")
        return False

def encode_to_variations(input_file, output_dir):
    """Create XOR variations from a JPG file."""
    if not os.path.isfile(input_file):
        print("Error: Input must be a file")
        return 0

    with open(input_file, 'rb') as f:
        original_data = f.read()

    xor_folder = os.path.join(output_dir, f"{Path(input_file).stem}_xor_variations")
    os.makedirs(xor_folder, exist_ok=True)

    created_files = 0
    for xor_val in range(256):  # 0-255 XOR variations
        out_name = f"{Path(input_file).stem}_xor_{xor_val:03d}.bin"
        out_path = os.path.join(xor_folder, out_name)
        
        transformed = transform_with_pattern(original_data, 4, xor_val)
        with open(out_path, 'wb') as f:
            f.write(transformed)
        created_files += 1

    print(f"Created {created_files} XOR variations in:\n{xor_folder}")
    return created_files

def find_variation_folders(search_root):
    """Find all variation folders recursively."""
    folders = []
    for root, dirs, _ in os.walk(search_root):
        for dir_name in dirs:
            if dir_name.endswith(('_variations', '_xor_variations')):
                folders.append(os.path.join(root, dir_name))
    return folders

def process_all_variation_folders(input_dir, output_dir):
    """Process all found variation folders automatically."""
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

def main():
    print("XOR Anomaly Processor")
    print("=" * 40)
    print("1. Encode JPG to XOR variations")
    print("2. Decode from variations folder")
    print("3. Auto-find and decode ALL variation folders")
    
    choice = input("\nSelect option (1-3): ").strip()
    base_dir = os.path.expanduser("~/storage/emulated/0/Documents")

    if choice == '1':
        # Encoding mode
        input_file = input("Enter JPG file path: ").strip()
        if not os.path.isfile(input_file):
            print("File not found!")
            return
            
        output_dir = input(f"Output directory [{base_dir}]: ").strip() or base_dir
        count = encode_to_variations(input_file, output_dir)
        print(f"\nDone. Created {count} variation files.")

    elif choice in ('2', '3'):
        # Decoding modes
        if choice == '2':
            input_dir = input("Enter variations folder path: ").strip()
            if not os.path.isdir(input_dir):
                print("Folder not found!")
                return
            output_dir = os.path.dirname(input_dir)
            process_all_variation_folders(input_dir, output_dir)
        else:
            search_root = input(f"Search root directory [{base_dir}]: ").strip() or base_dir
            output_dir = search_root
            process_all_variation_folders(search_root, output_dir)

    else:
        print("Invalid option")

if __name__ == "__main__":
    main()