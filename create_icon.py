#!/usr/bin/env python3
"""
Create a pennant icon for the Scoreboard Data Manager
"""
from PIL import Image, ImageDraw

def create_pennant_icon(size=1024):
    """Create a pennant flag icon"""
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Define pennant colors - using sports/scoreboard theme
    # Main pennant color: Deep blue
    pennant_color = (25, 62, 117)  # Dark blue
    outline_color = (255, 193, 7)  # Gold/yellow outline
    pole_color = (139, 69, 19)  # Brown pole

    # Calculate dimensions
    margin = size * 0.1
    pole_width = size * 0.03
    pole_height = size * 0.8

    # Draw the pole
    pole_x = margin + pole_width / 2
    pole_top = margin
    pole_bottom = pole_top + pole_height
    draw.rectangle(
        [pole_x - pole_width/2, pole_top, pole_x + pole_width/2, pole_bottom],
        fill=pole_color
    )

    # Draw pennant (triangular flag)
    # Starting from pole, extending right
    pennant_start_y = margin + size * 0.15
    pennant_height = size * 0.4
    pennant_width = size * 0.65

    # Pennant points: (pole top of flag, tip of flag, pole bottom of flag)
    pennant_points = [
        (pole_x, pennant_start_y),  # Top left (on pole)
        (pole_x + pennant_width, pennant_start_y + pennant_height / 2),  # Right tip
        (pole_x, pennant_start_y + pennant_height)  # Bottom left (on pole)
    ]

    # Draw pennant with outline
    # First draw a slightly larger version for outline
    outline_width = 8
    outline_points = [
        (p[0] - outline_width/2 if i == 0 or i == 2 else p[0] + outline_width,
         p[1] - (outline_width if i == 0 else (-outline_width if i == 2 else 0)))
        for i, p in enumerate(pennant_points)
    ]
    draw.polygon(outline_points, fill=outline_color)

    # Draw main pennant
    draw.polygon(pennant_points, fill=pennant_color)

    # Add decorative stripes on the pennant
    stripe_color = (255, 255, 255)  # White stripes
    num_stripes = 3
    stripe_spacing = pennant_height / (num_stripes + 1)

    for i in range(1, num_stripes + 1):
        y_pos = pennant_start_y + i * stripe_spacing
        # Calculate stripe width at this height (narrows as we go right)
        progress = i * stripe_spacing / pennant_height
        stripe_width = pennant_width * (1 - progress)
        stripe_height = 3

        draw.rectangle(
            [pole_x, y_pos - stripe_height, pole_x + stripe_width, y_pos + stripe_height],
            fill=stripe_color
        )

    # Add a pole cap (finial)
    cap_radius = pole_width * 1.5
    draw.ellipse(
        [pole_x - cap_radius, pole_top - cap_radius,
         pole_x + cap_radius, pole_top + cap_radius],
        fill=outline_color
    )

    return img

# Create icon at multiple sizes for .icns format
sizes = [16, 32, 64, 128, 256, 512, 1024]

print("Creating pennant icons...")
for size in sizes:
    img = create_pennant_icon(size)
    filename = f"icon_{size}x{size}.png"
    img.save(filename, 'PNG')
    print(f"Created {filename}")

# Also create a main icon.png
main_icon = create_pennant_icon(1024)
main_icon.save("pennant_icon.png", 'PNG')
print("\nCreated pennant_icon.png (1024x1024)")

print("\nIcon creation complete!")
print("\nTo create .icns file on Mac, use:")
print("  mkdir pennant.iconset")
print("  cp icon_16x16.png pennant.iconset/icon_16x16.png")
print("  cp icon_32x32.png pennant.iconset/icon_16x16@2x.png")
print("  cp icon_32x32.png pennant.iconset/icon_32x32.png")
print("  cp icon_64x64.png pennant.iconset/icon_32x32@2x.png")
print("  cp icon_128x128.png pennant.iconset/icon_128x128.png")
print("  cp icon_256x256.png pennant.iconset/icon_128x128@2x.png")
print("  cp icon_256x256.png pennant.iconset/icon_256x256.png")
print("  cp icon_512x512.png pennant.iconset/icon_256x256@2x.png")
print("  cp icon_512x512.png pennant.iconset/icon_512x512.png")
print("  cp icon_1024x1024.png pennant.iconset/icon_512x512@2x.png")
print("  iconutil -c icns pennant.iconset")
