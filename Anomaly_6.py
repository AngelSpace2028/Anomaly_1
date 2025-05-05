import os

def transform_with_pattern(data, chunk_size=4):
    """Apply XOR 0xFF transformation per chunk."""
    transformed = bytearray()
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        transformed.extend([b ^ 0xFF for b in chunk])
    return transformed

def is_prime(n):
    """Simple primality test."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n ** 0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

def find_nearest_prime_around(n):
    """Finds the closest prime near n (searches up and down)."""
    offset = 0
    while True:
        if is_prime(n - offset):
            return n - offset
        if is_prime(n + offset):
            return n + offset
        offset += 1

def encode_no_compression():
    print("\nSimple Encoder (XOR transformation + Zlib compression)")
    try:
        input_file = input("Enter input file: ").strip()
        output_base = input("Enter output base name (without .enc): ").strip()
    except EOFError:
        print("No input detected. Exiting encode mode.")
        return

    output_enc = output_base + ".enc"

    if not os.path.isfile(input_file):
        print(f"Error: File '{input_file}' does not exist.")
        return

    try:
        with open(input_file, 'rb') as f:
            original_data = f.read()

        # Apply XOR transformation
        transformed_data = transform_with_pattern(original_data)

        # Convert bytearray to bytes before compression
        transformed_data_bytes = bytes(transformed_data)

        # Apply Zlib compression
        compressed_data = (transformed_data_bytes)

        # Save to output file
        with open(output_enc, 'wb') as f:
            f.write(compressed_data)

        # Analyze file size
        size = len(compressed_data)
        half_size = size // 2
        nearby_prime = find_nearest_prime_around(half_size)
        print(f"Transformed and compressed file size: {size} bytes")
        print(f"Half of size: {half_size}")
        print(f"Nearest prime around {half_size} is: {nearby_prime}")

        print(f"Encoding complete. Output saved to {output_enc}")
    except Exception as e:
        print(f"An error occurred during encoding: {e}")

def decode_no_compression():
    print("\nSimple Decoder (Zlib decompression + XOR transformation)")
    try:
        input_enc = input("Enter encoded file (.enc): ").strip()
        output_file = input("Enter output file: ").strip()
    except EOFError:
        print("No input detected. Exiting decode mode.")
        return

    if not os.path.isfile(input_enc):
        print(f"Error: File '{input_enc}' does not exist.")
        return

    try:
        with open(input_enc, 'rb') as f:
            encoded_data = f.read()

        # Apply Zlib decompression
        decompressed_data = (encoded_data)

        # Apply XOR transformation (reverse)
        recovered_data = transform_with_pattern(decompressed_data)

        with open(output_file, 'wb') as f:
            f.write(recovered_data)

        print(f"Decoding complete. Output saved to {output_file}")
    except Exception as e:
        print(f"An error occurred during decoding: {e}")

if __name__ == "__main__":
    print("Software")
    print("Created by Jurijus Pacalovas.")
    print("File Encoding/Decoding System")
    print("Options:")
    print("1 - Encode file")
    print("2 - Decode file")

    try:
        choice = input("Enter 1 or 2: ").strip()
        if choice not in ('1', '2'):
            print("Invalid choice. Exiting.")
            exit()
    except EOFError:
        print("No input detected. Defaulting to Encode (1).")
        choice = '1'

    if choice == '1':
        encode_no_compression()
    elif choice == '2':
        decode_no_compression()