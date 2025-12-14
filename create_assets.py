"""Create placeholder PNG assets for Expo frontend"""
from PIL import Image, ImageDraw, ImageFont
import os

# Create assets directory if it doesn't exist
assets_dir = "frontend/assets"
os.makedirs(assets_dir, exist_ok=True)

# Create icon.png (1024x1024 - standard app icon size)
icon = Image.new('RGB', (1024, 1024), color='#8B4513')  # Brown color for sock theme
draw = ImageDraw.Draw(icon)
# Draw a simple sock shape
draw.ellipse([312, 312, 712, 712], fill='#F4E4C1', outline='#000000', width=5)
draw.text((400, 480), "🧦", fill='#000000', font=None)
icon.save(os.path.join(assets_dir, "icon.png"))
print(f"✓ Created {os.path.join(assets_dir, 'icon.png')}")

# Create adaptive-icon.png (same as icon for simplicity)
icon.save(os.path.join(assets_dir, "adaptive-icon.png"))
print(f"✓ Created {os.path.join(assets_dir, 'adaptive-icon.png')}")

# Create splash.png (1284x2778 - iPhone 13 Pro Max size)
splash = Image.new('RGB', (1284, 2778), color='#F4E4C1')
draw = ImageDraw.Draw(splash)
# Center position
center_x, center_y = 642, 1389
draw.ellipse([center_x-200, center_y-200, center_x+200, center_y+200], 
             fill='#8B4513', outline='#000000', width=5)
splash.save(os.path.join(assets_dir, "splash.png"))
print(f"✓ Created {os.path.join(assets_dir, 'splash.png')}")

# Create favicon.png (48x48 - standard favicon size)
favicon = Image.new('RGB', (48, 48), color='#8B4513')
draw = ImageDraw.Draw(favicon)
draw.ellipse([8, 8, 40, 40], fill='#F4E4C1', outline='#000000', width=2)
favicon.save(os.path.join(assets_dir, "favicon.png"))
print(f"✓ Created {os.path.join(assets_dir, 'favicon.png')}")

print("\n✅ All asset files created successfully!")
