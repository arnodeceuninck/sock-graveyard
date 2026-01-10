"""add_color_palette_to_socks

Revision ID: 008
Revises: 007
Create Date: 2026-01-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base
import json
import os
from PIL import Image
from collections import Counter
from sklearn.cluster import KMeans
import numpy as np


# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None

Base = declarative_base()


class Sock(Base):
    __tablename__ = 'socks'
    id = sa.Column(sa.Integer, primary_key=True)
    image_no_bg_path = sa.Column(sa.String)
    color_palette = sa.Column(sa.String)


def extract_color_palette(image: Image.Image, num_colors: int = 5):
    """Extract dominant and distinctive colors from an image."""
    try:
        if image.mode == 'RGBA':
            pixels = []
            for x in range(image.width):
                for y in range(image.height):
                    pixel = image.getpixel((x, y))
                    if pixel[3] > 128:
                        pixels.append(pixel[:3])
            
            if not pixels:
                return []
            
            pixels_array = np.array(pixels)
        else:
            image_rgb = image.convert('RGB')
            pixels_array = np.array(image_rgb).reshape(-1, 3)
        
        initial_colors = min(15, len(pixels_array))
        if len(pixels_array) < initial_colors:
            initial_colors = max(1, len(pixels_array))
        
        kmeans = KMeans(n_clusters=initial_colors, random_state=42, n_init=10)
        kmeans.fit(pixels_array)
        
        colors = kmeans.cluster_centers_
        labels = kmeans.labels_
        label_counts = Counter(labels)
        
        def color_distance(c1, c2):
            return np.sqrt(np.sum((c1 - c2) ** 2))
        
        def color_saturation(color):
            r, g, b = color / 255.0
            max_val = max(r, g, b)
            min_val = min(r, g, b)
            if max_val == 0:
                return 0
            return (max_val - min_val) / max_val
        
        color_data = []
        for i in range(len(colors)):
            color = colors[i]
            frequency = label_counts[i]
            saturation = color_saturation(color)
            score = (frequency ** 0.7) * (1 + saturation * 2)
            color_data.append({
                'color': color,
                'frequency': frequency,
                'saturation': saturation,
                'score': score
            })
        
        color_data.sort(key=lambda x: x['score'], reverse=True)
        
        high_sat_colors = [d for d in color_data if d['saturation'] > 0.4]
        low_sat_colors = [d for d in color_data if d['saturation'] <= 0.4]
        
        selected_colors = []
        min_distance = 30
        
        for data in high_sat_colors:
            color = data['color']
            is_distinct = True
            for selected in selected_colors:
                if color_distance(color, selected) < min_distance:
                    is_distinct = False
                    break
            
            if is_distinct:
                selected_colors.append(color)
            
            if len(selected_colors) >= num_colors:
                break
        
        for data in low_sat_colors:
            if len(selected_colors) >= num_colors:
                break
                
            color = data['color']
            is_distinct = True
            for selected in selected_colors:
                if color_distance(color, selected) < min_distance:
                    is_distinct = False
                    break
            
            if is_distinct:
                selected_colors.append(color)
        
        hex_colors = []
        for color in selected_colors:
            r, g, b = color.astype(int)
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            hex_colors.append(hex_color)
        
        return hex_colors
    except Exception as e:
        print(f"Failed to extract color palette: {str(e)}")
        return []


def upgrade():
    # Add color_palette column to socks table
    op.add_column('socks', sa.Column('color_palette', sa.String(), nullable=True))
    
    # Generate color palettes for existing socks with no-background images
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    
    try:
        # Get all socks that have a no-background image but no color palette
        socks = session.query(Sock).filter(
            Sock.image_no_bg_path.isnot(None),
            Sock.color_palette.is_(None)
        ).all()
        
        print(f"Processing {len(socks)} existing socks for color palette extraction...")
        
        for sock in socks:
            try:
                if os.path.exists(sock.image_no_bg_path):
                    with Image.open(sock.image_no_bg_path) as img:
                        color_palette = extract_color_palette(img, num_colors=5)
                        if color_palette:
                            sock.color_palette = json.dumps(color_palette)
                            print(f"Generated color palette for sock {sock.id}: {color_palette}")
                else:
                    print(f"Image file not found for sock {sock.id}: {sock.image_no_bg_path}")
            except Exception as e:
                print(f"Failed to process sock {sock.id}: {str(e)}")
                continue
        
        session.commit()
        print(f"Completed color palette generation for {len(socks)} socks")
    except Exception as e:
        print(f"Error during color palette migration: {str(e)}")
        session.rollback()
    finally:
        session.close()


def downgrade():
    # Remove color_palette column from socks table
    op.drop_column('socks', 'color_palette')
