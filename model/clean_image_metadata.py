#!/usr/bin/env python3
"""
Script to remove sensitive metadata from images and rename them with GUIDs.

This script:
1. Removes all EXIF data (GPS location, camera info, timestamps, etc.)
2. Strips other metadata that could be sensitive
3. Renames files to sock-{guid}.jpg format
4. Creates a mapping file to track original filenames

Usage:
    python clean_image_metadata.py
"""

import os
import uuid
import json
from pathlib import Path
from PIL import Image
from datetime import datetime


def remove_metadata_and_rename(image_dir: str, output_dir: str = None, create_mapping: bool = True, auto_group: bool = False):
    """
    Remove all metadata from images and rename them.
    
    Args:
        image_dir: Directory containing images to process
        output_dir: Directory to save cleaned images (defaults to same as input)
        create_mapping: Whether to create a JSON file mapping new names to old names
        auto_group: If True, groups images by pairs (sorted by timestamp). 
                   Each pair gets the same GUID with -0 and -1 suffixes.
    """
    image_path = Path(image_dir)
    
    if output_dir is None:
        output_dir = image_dir
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Supported image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
    
    # Find all image files, excluding already cleaned ones
    image_files = [
        f for f in image_path.iterdir() 
        if f.is_file() and f.suffix.lower() in image_extensions
        and not f.name.startswith('sock-')  # Skip already cleaned files
    ]
    
    # Count skipped files for user feedback
    all_images = [
        f for f in image_path.iterdir() 
        if f.is_file() and f.suffix.lower() in image_extensions
    ]
    skipped_count = len(all_images) - len(image_files)
    
    if skipped_count > 0:
        print(f"Skipping {skipped_count} already cleaned file(s) (sock-*.jpg)")
    
    if not image_files:
        print(f"No image files found in {image_dir}")
        print("(Files starting with 'sock-' are skipped as already processed)")
        return
    
    # Sort by capture time (EXIF) if auto-grouping
    if auto_group:
        def get_capture_time(file_path):
            """Extract capture time from EXIF data, fall back to modification time."""
            try:
                with Image.open(file_path) as img:
                    exif_data = img.getexif()
                    if exif_data:
                        # Try DateTimeOriginal (when photo was taken)
                        if 36867 in exif_data:  # DateTimeOriginal
                            return datetime.strptime(exif_data[36867], '%Y:%m:%d %H:%M:%S')
                        # Try DateTime as fallback
                        if 306 in exif_data:  # DateTime
                            return datetime.strptime(exif_data[306], '%Y:%m:%d %H:%M:%S')
            except Exception:
                pass
            # Fall back to file modification time
            return datetime.fromtimestamp(file_path.stat().st_mtime)
        
        image_files.sort(key=get_capture_time)
        print(f"Found {len(image_files)} image(s) to process (sorted by capture time for auto-grouping)")
        if len(image_files) % 2 != 0:
            print(f"⚠ Warning: Odd number of images ({len(image_files)}). Last image will be unpaired.")
    else:
        print(f"Found {len(image_files)} image(s) to process")
    
    # Mapping of new filenames to original filenames
    filename_mapping = {}
    
    # Process each image
    for idx, image_file in enumerate(image_files, 1):
        try:
            print(f"Processing [{idx}/{len(image_files)}]: {image_file.name}")
            
            # Open the image
            with Image.open(image_file) as img:
                # Create a new image without metadata
                # Convert to RGB if necessary (handles transparency issues)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create a white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    if img.mode in ('RGBA', 'LA'):
                        background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
                        img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Generate GUID and filename
                if auto_group:
                    # For auto-grouping, pair consecutive images
                    pair_index = (idx - 1) // 2
                    sock_index = (idx - 1) % 2  # 0 or 1
                    
                    # Generate or reuse GUID for this pair
                    if sock_index == 0:
                        # First sock of pair - generate new GUID
                        full_guid = str(uuid.uuid4())
                        short_guid = full_guid.split('-')[0]
                        # Store for the second sock
                        if not hasattr(remove_metadata_and_rename, '_current_guid'):
                            remove_metadata_and_rename._current_guid = {}
                        remove_metadata_and_rename._current_guid[pair_index] = (full_guid, short_guid)
                    else:
                        # Second sock of pair - reuse GUID
                        full_guid, short_guid = remove_metadata_and_rename._current_guid[pair_index]
                    
                    new_filename = f"sock-{short_guid}-{sock_index}.jpg"
                else:
                    # Original behavior - unique GUID for each image
                    full_guid = str(uuid.uuid4())
                    short_guid = full_guid.split('-')[0]
                    new_filename = f"sock-{short_guid}-0.jpg"
                
                new_filepath = output_path / new_filename
                
                # Save without metadata
                # Using quality=95 for good quality, optimize=True to reduce size
                img.save(
                    new_filepath,
                    'JPEG',
                    quality=95,
                    optimize=True,
                    exif=b''  # Empty EXIF data
                )
                
                print(f"  ✓ Saved as: {new_filename}")
                
                # Store mapping
                filename_mapping[new_filename] = {
                    'original_name': image_file.name,
                    'processed_date': datetime.now().isoformat(),
                    'full_guid': full_guid,
                    'short_guid': short_guid
                }
                
                if auto_group:
                    filename_mapping[new_filename]['pair_index'] = pair_index
                    filename_mapping[new_filename]['sock_index'] = sock_index
                
        except Exception as e:
            print(f"  ✗ Error processing {image_file.name}: {e}")
            continue
    
    # Save the mapping file
    if create_mapping and filename_mapping:
        mapping_file = output_path / 'filename_mapping.json'
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(filename_mapping, f, indent=2, sort_keys=True)
        print(f"\n✓ Created mapping file: {mapping_file}")
        print(f"  (This file contains original filenames - don't commit it to Git!)")
    
    print(f"\n✓ Successfully processed {len(filename_mapping)} image(s)")
    print(f"✓ All metadata removed and images renamed")
    
    # Optionally, offer to delete original files
    if output_dir == image_dir:
        print("\n⚠ Original files are still in the directory.")
        print("  Review the cleaned images before deleting originals.")
        response = input("  Delete original files? (yes/no): ").strip().lower()
        if response == 'yes':
            for image_file in image_files:
                try:
                    image_file.unlink()
                    print(f"  Deleted: {image_file.name}")
                except Exception as e:
                    print(f"  Error deleting {image_file.name}: {e}")
            print("✓ Original files deleted")


def verify_metadata_removed(image_path: str):
    """
    Verify that an image has no EXIF metadata.
    
    Args:
        image_path: Path to the image file
    """
    try:
        with Image.open(image_path) as img:
            exif_data = img.getexif()
            if exif_data:
                print(f"⚠ Warning: {image_path} still contains EXIF data:")
                for tag_id, value in exif_data.items():
                    tag = Image.ExifTags.TAGS.get(tag_id, tag_id)
                    print(f"  {tag}: {value}")
                return False
            else:
                print(f"✓ {image_path} has no EXIF metadata")
                return True
    except Exception as e:
        print(f"✗ Error checking {image_path}: {e}")
        return False


if __name__ == "__main__":
    # Configuration
    IMAGE_DIR = "images"  # Relative to this script's location
    AUTO_GROUP = True  # Set to True to automatically pair consecutive images by timestamp
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    image_dir = script_dir / IMAGE_DIR
    
    print("=" * 60)
    print("Image Metadata Cleaner")
    print("=" * 60)
    print(f"Image directory: {image_dir}")
    if AUTO_GROUP:
        print("Auto-grouping: ENABLED (pairs will share GUIDs)")
    else:
        print("Auto-grouping: DISABLED (each image gets unique GUID)")
    print()
    
    if not image_dir.exists():
        print(f"Error: Directory '{image_dir}' does not exist")
        exit(1)
    
    # Process images
    remove_metadata_and_rename(str(image_dir), create_mapping=True, auto_group=AUTO_GROUP)
    
    print("\n" + "=" * 60)
    print("IMPORTANT REMINDERS:")
    print("=" * 60)
    print("1. Review the cleaned images before committing")
    print("2. Add 'filename_mapping.json' to .gitignore if not already present")
    print("3. The original filenames contain timestamps - keep mapping private")
    print("=" * 60)
