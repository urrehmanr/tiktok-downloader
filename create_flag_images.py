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
    },
    # Turkish flag - Red with white crescent and star
    'tr': {
        'description': 'Turkish flag - Red with white crescent and star',
        'background': (227, 10, 23),  # Red
        'custom_draw': 'turkish'
    },
    # Vietnamese flag - Red with yellow star
    'vi': {
        'description': 'Vietnamese flag - Red with yellow star in center',
        'background': (218, 37, 29),  # Red
        'custom_draw': 'vietnamese'
    },
    # Thai flag - Red, white, blue horizontal stripes
    'th': {
        'description': 'Thai flag - Red, white, blue horizontal stripes',
        'stripes': [
            {'color': (237, 28, 36), 'height': FLAG_HEIGHT // 6},  # Red
            {'color': (255, 255, 255), 'height': FLAG_HEIGHT // 6},  # White
            {'color': (0, 32, 91), 'height': FLAG_HEIGHT // 3},  # Blue (middle stripe is twice as tall)
            {'color': (255, 255, 255), 'height': FLAG_HEIGHT // 6},  # White
            {'color': (237, 28, 36), 'height': FLAG_HEIGHT // 6},  # Red
        ]
    },
    # Polish flag - White (top) and red (bottom)
    'pl': {
        'description': 'Polish flag - White (top) and red (bottom)',
        'stripes': [
            {'color': (255, 255, 255), 'height': FLAG_HEIGHT // 2},  # White top half
            {'color': (220, 20, 60), 'height': FLAG_HEIGHT // 2}   # Red bottom half
        ]
    },
    # Ukrainian flag - Blue (top) and yellow (bottom)
    'uk': {
        'description': 'Ukrainian flag - Blue (top) and yellow (bottom)',
        'stripes': [
            {'color': (0, 87, 183), 'height': FLAG_HEIGHT // 2},  # Blue top half
            {'color': (255, 215, 0), 'height': FLAG_HEIGHT // 2}  # Yellow bottom half
        ]
    },
    # Dutch flag - Red, white, blue horizontal stripes
    'nl': {
        'description': 'Dutch flag - Red, white, blue horizontal stripes',
        'stripes': [
            {'color': (174, 28, 40), 'height': FLAG_HEIGHT // 3},  # Red
            {'color': (255, 255, 255), 'height': FLAG_HEIGHT // 3},  # White
            {'color': (33, 70, 139), 'height': FLAG_HEIGHT // 3}   # Blue
        ]
    },
    # Romanian flag - Blue, yellow, red vertical stripes
    'ro': {
        'description': 'Romanian flag - Blue, yellow, red vertical stripes',
        'custom_draw': 'romanian'
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
    
    # Custom drawing for specific flags
    if 'custom_draw' in flag_spec:
        if flag_spec['custom_draw'] == 'turkish':
            # Turkish flag
            # White crescent and star
            crescent_center_x = FLAG_WIDTH * 0.35
            crescent_center_y = FLAG_HEIGHT * 0.5
            crescent_radius = FLAG_HEIGHT * 0.3
            
            # Draw crescent (white circle with smaller red circle offset)
            draw.ellipse((
                crescent_center_x - crescent_radius, 
                crescent_center_y - crescent_radius,
                crescent_center_x + crescent_radius,
                crescent_center_y + crescent_radius
            ), fill=(255, 255, 255))
            
            # Offset circle to create crescent
            offset = crescent_radius * 0.35
            draw.ellipse((
                crescent_center_x - crescent_radius + offset, 
                crescent_center_y - crescent_radius,
                crescent_center_x + crescent_radius + offset,
                crescent_center_y + crescent_radius
            ), fill=(227, 10, 23))  # Same as background color
            
            # Draw star
            star_center_x = FLAG_WIDTH * 0.5
            star_center_y = FLAG_HEIGHT * 0.5
            draw_star(draw, star_center_x, star_center_y, FLAG_HEIGHT * 0.15, (255, 255, 255))
        
        elif flag_spec['custom_draw'] == 'vietnamese':
            # Draw yellow star in the center
            draw_star(draw, FLAG_WIDTH // 2, FLAG_HEIGHT // 2, FLAG_HEIGHT // 4, (255, 255, 0))
        
        elif flag_spec['custom_draw'] == 'romanian':
            # Romanian flag - vertical stripes
            stripe_width = FLAG_WIDTH // 3
            # Blue stripe
            draw.rectangle([(0, 0), (stripe_width, FLAG_HEIGHT)], fill=(0, 43, 127))
            # Yellow stripe
            draw.rectangle([(stripe_width, 0), (stripe_width * 2, FLAG_HEIGHT)], fill=(252, 209, 22))
            # Red stripe
            draw.rectangle([(stripe_width * 2, 0), (FLAG_WIDTH, FLAG_HEIGHT)], fill=(206, 17, 38))
    
    # Save the flag image
    output_path = os.path.join(OUTPUT_DIR, f"{lang_code}.png")
    img.save(output_path)
    print(f"Saved flag image for {lang_code} to {output_path}")

# Fix for Ukrainian flag - Create it again explicitly to ensure it's generated
print("Ensuring Ukrainian flag is generated...")
# Ukrainian flag - Blue (top) and yellow (bottom)
img = Image.new('RGB', (FLAG_WIDTH, FLAG_HEIGHT), color=(255, 255, 255))
draw = ImageDraw.Draw(img)
# Blue top half
draw.rectangle([(0, 0), (FLAG_WIDTH, FLAG_HEIGHT // 2)], fill=(0, 87, 183))
# Yellow bottom half
draw.rectangle([(0, FLAG_HEIGHT // 2), (FLAG_WIDTH, FLAG_HEIGHT)], fill=(255, 215, 0))
# Save the Ukrainian flag
output_path = os.path.join(OUTPUT_DIR, "uk.png")
img.save(output_path)
print(f"Saved Ukrainian flag to {output_path}")

print("Flag image creation complete!") 