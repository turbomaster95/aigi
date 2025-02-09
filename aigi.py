import struct
import json
import argparse
from PIL import Image
import zlib
import io

def save_aigi(images: list, filename: str, metadata: dict = None):
    metadata = metadata or {}
    metadata_json = json.dumps(metadata).encode('utf-8')
    metadata_size = len(metadata_json)
    
    image_data_list = []
    for image in images:
        with io.BytesIO() as img_buffer:
            image = image.convert("RGBA")  # Ensure all colors including transparency are preserved
            image.save(img_buffer, format='PNG')
            img_data = img_buffer.getvalue()
            compressed_img_data = zlib.compress(img_data)
            image_data_list.append(compressed_img_data)
    
    with open(filename, 'wb') as f:
        f.write(b'AIGI')  # Signature
        f.write(struct.pack('B', 1))  # Version
        f.write(struct.pack('I', len(images)))  # Number of images
        f.write(struct.pack('I', metadata_size))
        f.write(metadata_json)
        
        for img_data in image_data_list:
            f.write(struct.pack('I', len(img_data)))  # Image size
            f.write(img_data)

def load_aigi(filename: str):
    with open(filename, 'rb') as f:
        signature = f.read(4)
        if signature != b'AIGI':
            raise ValueError("Invalid AIGI file format")
        
        version = struct.unpack('B', f.read(1))[0]
        num_images = struct.unpack('I', f.read(4))[0]
        metadata_size = struct.unpack('I', f.read(4))[0]
        metadata_json = f.read(metadata_size).decode('utf-8')
        metadata = json.loads(metadata_json)
        
        images = []
        for _ in range(num_images):
            img_size = struct.unpack('I', f.read(4))[0]
            compressed_img_data = f.read(img_size)
            img_data = zlib.decompress(compressed_img_data)
            image = Image.open(io.BytesIO(img_data)).convert("RGBA")
            images.append(image)
    
    return images, metadata

def main():
    parser = argparse.ArgumentParser(description="AIGI Image Format CLI Tool")
    parser.add_argument("command", choices=["save", "load"], help="Command to execute")
    parser.add_argument("filename", help="AIGI file name")
    parser.add_argument("--images", nargs='+', help="List of image files to save")
    parser.add_argument("--metadata", type=str, help="Metadata in JSON format")
    
    args = parser.parse_args()
    
    if args.command == "save":
        if not args.images:
            print("Error: No images provided.")
            return
        
        images = [Image.open(img) for img in args.images]
        metadata = json.loads(args.metadata) if args.metadata else {}
        save_aigi(images, args.filename, metadata)
        print(f"Saved {len(images)} images to {args.filename}")
    
    elif args.command == "load":
        images, metadata = load_aigi(args.filename)
        print(f"Loaded {len(images)} images from {args.filename}")
        print("Metadata:", json.dumps(metadata, indent=4))
        for i, img in enumerate(images):
            img.show(title=f"Image {i+1}")

if __name__ == "__main__":
    main()
