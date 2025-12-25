# Image Metadata Cleaning Guide

This guide explains how to clean sensitive metadata from images before committing them to Git.

## Why Clean Metadata?

Image files (especially from smartphones) contain EXIF metadata that may include:
- **GPS coordinates** - exact location where photo was taken
- **Timestamp** - exact date and time
- **Camera/phone model** - device information
- **Software versions** - editing tools used
- **Author information** - photographer name
- **Copyright data** - ownership information

## Filename Format

Images are renamed to: `sock-{8-char-guid}-0.jpg`

Examples:
- `sock-a1b2c3d4-0.jpg`
- `sock-e5f6a7b8-0.jpg`

The `-0` suffix allows you to manually rename multiple pictures of the same sock:
- `sock-a1b2c3d4-0.jpg` (first picture)
- `sock-a1b2c3d4-1.jpg` (second picture, renamed manually)
- `sock-a1b2c3d4-2.jpg` (third picture, renamed manually)

## Using the Cleanup Script

### Quick Start

1. Place your images in the `model/images/` directory
2. Run the cleanup script:

```bash
cd model
python clean_image_metadata.py
```

3. Review the cleaned images (now named `sock-{guid}.jpg`)
4. When prompted, choose whether to delete the original files
5. Add `filename_mapping.json` to `.gitignore` (contains original names)

### What the Script Does

1. **Removes all EXIF metadata** - GPS, timestamps, camera info, etc.
2. **Renames files** - Changes to `sock-{8-char-guid}-0.jpg` format to hide original timestamps
3. **Creates mapping file** - Saves `filename_mapping.json` with original names (keep private!)
4. **Optimizes images** - Re-saves as JPEG with quality=95

### Example Output

```
Processing [1/31]: PXL_20251214_192708921.jpg
  ✓ Saved as: sock-a1b2c3d4-0.jpg
Processing [2/31]: PXL_20251214_192712389.jpg
  ✓ Saved as: sock-b2c3d4e5-0.jpg
...
✓ Created mapping file: filename_mapping.json
✓ Successfully processed 31 image(s)
```

## Important Notes

### Before Committing

1. **Review cleaned images** - Make sure they look correct
2. **Check metadata removed** - Use `exiftool` or image properties
3. **Update .gitignore** - Ensure `filename_mapping.json` is excluded
4. **Delete originals** - Original files contain metadata in filename

### Keep Private

- `filename_mapping.json` - Maps GUIDs back to original filenames (contains timestamps)
- Original image files - Contain full EXIF metadata

### Add to .gitignore

```gitignore
# Image metadata cleanup
model/images/filename_mapping.json
model/images/PXL_*.jpg  # Original Pixel phone images
```

## Managing Multiple Pictures of Same Sock

After running the script, all images will have `-0` suffix. If you have multiple pictures of the same sock, you can manually rename them:

1. Identify which images show the same sock
2. Choose one base GUID (e.g., `a1b2c3d4`)
3. Rename the files:
   - `sock-a1b2c3d4-0.jpg` (keep first as is)
   - Rename `sock-e5f6a7b8-0.jpg` → `sock-a1b2c3d4-1.jpg`
   - Rename `sock-9c8d7e6f-0.jpg` → `sock-a1b2c3d4-2.jpg`

This groups pictures of the same sock together while keeping unique identifiers.

## Verify Metadata Removal

### Using exiftool (recommended)

Install exiftool:
```bash
# Windows (using Chocolatey)
choco install exiftool

# macOS
brew install exiftool

# Linux
sudo apt-get install libimage-exiftool-perl
```

Check a file:
```bash
exiftool model/images/sock-*.jpg
```

Should show minimal metadata (no GPS, camera info, etc.)

### Using Python

```python
from PIL import Image

img = Image.open('model/images/sock-example.jpg')
exif_data = img.getexif()
print(f"EXIF tags: {len(exif_data)}")  # Should be 0
```

## Manual Alternative

If you prefer to manually clean metadata:

### Using ImageMagick

```bash
# Remove all metadata
magick input.jpg -strip output.jpg
```

### Using exiftool

```bash
# Remove all metadata
exiftool -all= input.jpg
```

### Using Python/Pillow

```python
from PIL import Image

img = Image.open('input.jpg')
# Remove EXIF by saving without it
img.save('output.jpg', 'JPEG', quality=95, exif=b'')
```

## Security Checklist

Before committing images to Git:

- [ ] Run `clean_image_metadata.py` script
- [ ] Verify metadata removed with `exiftool`
- [ ] Check images don't contain sensitive visual content
- [ ] Add `filename_mapping.json` to `.gitignore`
- [ ] Delete original files with metadata
- [ ] Review renamed files have no identifying patterns
- [ ] Commit only the `sock-{guid}.jpg` files

## Troubleshooting

### Script fails with "No module named 'PIL'"

Install Pillow:
```bash
pip install Pillow
```

### Images look different after processing

The script converts all images to RGB JPEG. If you need to preserve:
- PNG transparency: Modify script to keep PNG format
- Original format: Change the save format in the script

### Want to keep original filenames

Modify the script to skip renaming but still strip metadata:
```python
# In the script, replace:
new_filename = f"sock-{new_guid}.jpg"
# With:
new_filename = image_file.name
```

(Note: Original filenames from Pixel phones contain timestamps!)
