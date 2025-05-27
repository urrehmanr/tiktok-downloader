#!/usr/bin/env python3
import os
from PIL import Image, ImageDraw
import math

# Output directory
OUTPUT_DIR = 'static/images/flags'

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Define flag dimensions to match existing flags (checking sizes of existing files)
FLAG_WIDTH = 100
FLAG_HEIGHT = 60

# Helper function to draw a 5-pointed star
def draw_star(draw, center_x, center_y, radius, color):
    points = []
    for i in range(5):
        # Outer points
        x = center_x + radius * math.sin(2 * math.pi * i / 5)
        y = center_y - radius * math.cos(2 * math.pi * i / 5)
        points.extend([x, y])
        
        # Inner points
        inner_radius = radius * 0.38
        x = center_x + inner_radius * math.sin(2 * math.pi * (i + 0.5) / 5)
        y = center_y - inner_radius * math.cos(2 * math.pi * (i + 0.5) / 5)
        points.extend([x, y])
    
    draw.polygon(points, fill=color)

# Helper function to draw a crescent moon
def draw_crescent(draw, center_x, center_y, radius, color):
    # Draw main circle
    draw.ellipse((
        center_x - radius, 
        center_y - radius,
        center_x + radius,
        center_y + radius
    ), fill=color)
    
    # Draw overlapping circle to create crescent effect
    offset = radius * 0.3
    draw.ellipse((
        center_x - radius + offset, 
        center_y - radius,
        center_x + radius + offset,
        center_y + radius
    ), fill=(0, 0, 128))  # Same color as canton

# Flag specifications
flags = {
    'id': {
        'description': 'Indonesian flag - red (top) and white (bottom)',
        'stripes': [
            {'color': (255, 0, 0), 'height': FLAG_HEIGHT // 2},  # Red top half
            {'color': (255, 255, 255), 'height': FLAG_HEIGHT // 2}  # White bottom half
        ]
    },
    'bn': {
        'description': 'Bangladesh flag - dark green with red circle',
        'background': (0, 106, 78),  # Dark green
        'circle': {'center': (FLAG_WIDTH//2, FLAG_HEIGHT//2), 'radius': FLAG_HEIGHT//3, 'color': (244, 42, 65)}  # Red circle
    },
    'ms': {
        'description': 'Malaysian flag - 14 alternating red and white stripes with blue canton and yellow symbols',
        'stripes': [
            {'color': (204, 0, 0), 'height': FLAG_HEIGHT // 14},  # Red
            {'color': (255, 255, 255), 'height': FLAG_HEIGHT // 14},  # White
            {'color': (204, 0, 0), 'height': FLAG_HEIGHT // 14},
            {'color': (255, 255, 255), 'height': FLAG_HEIGHT // 14},
            {'color': (204, 0, 0), 'height': FLAG_HEIGHT // 14},
            {'color': (255, 255, 255), 'height': FLAG_HEIGHT // 14},
            {'color': (204, 0, 0), 'height': FLAG_HEIGHT // 14},
            {'color': (255, 255, 255), 'height': FLAG_HEIGHT // 14},
            {'color': (204, 0, 0), 'height': FLAG_HEIGHT // 14},
            {'color': (255, 255, 255), 'height': FLAG_HEIGHT // 14},
            {'color': (204, 0, 0), 'height': FLAG_HEIGHT // 14},
            {'color': (255, 255, 255), 'height': FLAG_HEIGHT // 14},
            {'color': (204, 0, 0), 'height': FLAG_HEIGHT // 14},
            {'color': (255, 255, 255), 'height': FLAG_HEIGHT // 14},
        ],
        'canton': {'x': 0, 'y': 0, 'width': FLAG_WIDTH // 2, 'height': FLAG_HEIGHT // 2, 'color': (0, 0, 128)},  # Blue canton
        'has_crescent': True,
        'has_star': True
    }
}

# Create flags
for lang_code, flag_spec in flags.items():
    print(f"Creating flag for {lang_code}...")
    
    # Create a blank image
    img = Image.new('RGB', (FLAG_WIDTH, FLAG_HEIGHT), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    if 'stripes' in flag_spec:
        # Draw horizontal stripes
        y_pos = 0
        for stripe in flag_spec['stripes']:
            draw.rectangle([(0, y_pos), (FLAG_WIDTH, y_pos + stripe['height'])], fill=stripe['color'])
            y_pos += stripe['height']
    
    if 'background' in flag_spec:
        # Fill background color
        draw.rectangle([(0, 0), (FLAG_WIDTH, FLAG_HEIGHT)], fill=flag_spec['background'])
    
    if 'circle' in flag_spec:
        # Draw circle
        circle = flag_spec['circle']
        draw.ellipse((
            circle['center'][0] - circle['radius'],
            circle['center'][1] - circle['radius'],
            circle['center'][0] + circle['radius'],
            circle['center'][1] + circle['radius']
        ), fill=circle['color'])
    
    if 'canton' in flag_spec:
        # Draw canton (rectangle in top-left corner)
        canton = flag_spec['canton']
        draw.rectangle([(canton['x'], canton['y']), (canton['x'] + canton['width'], canton['y'] + canton['height'])], fill=canton['color'])
    
    # Special handling for Malaysian flag
    if lang_code == 'ms' and flag_spec.get('has_crescent', False):
        # Draw crescent moon
        draw_crescent(draw, FLAG_WIDTH // 6, FLAG_HEIGHT // 4, FLAG_HEIGHT // 8, (255, 204, 0))
        
    if lang_code == 'ms' and flag_spec.get('has_star', False):
        # Draw star
        draw_star(draw, FLAG_WIDTH // 4, FLAG_HEIGHT // 4, FLAG_HEIGHT // 12, (255, 204, 0))
    
    # Save the flag image
    output_path = os.path.join(OUTPUT_DIR, f"{lang_code}.png")
    img.save(output_path)
    print(f"Saved flag image for {lang_code} to {output_path}")

print("Flag image creation complete!") 