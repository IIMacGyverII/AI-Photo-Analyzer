"""Generate application icon."""

from PIL import Image, ImageDraw

def create_icon():
    """Create a simple icon for the application."""
    # Create a 256x256 image with transparency
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a gradient background circle (dark purple/blue theme)
    for i in range(80):
        alpha = int(255 * (1 - i / 80))
        color = (88 + i, 91 + i, 150 + i, alpha)
        draw.ellipse([i, i, size-i, size-i], fill=color)
    
    # Draw main circle (camera lens style)
    draw.ellipse([40, 40, 216, 216], fill=(45, 47, 90, 255), outline=(166, 227, 161, 255), width=6)
    
    # Draw inner circles (aperture blades effect)
    center = size // 2
    draw.ellipse([80, 80, 176, 176], fill=(88, 91, 112, 255), outline=(166, 227, 161, 200), width=3)
    
    # Draw center dot (lens center)
    draw.ellipse([108, 108, 148, 148], fill=(249, 226, 175, 255))
    
    # Draw small accent circle (AI indicator)
    draw.ellipse([170, 60, 200, 90], fill=(166, 227, 161, 255), outline=(45, 47, 90, 255), width=3)
    
    # Save as PNG
    img.save('ollama_image_analyzer/resources/icon.png', 'PNG')
    print("✓ Created icon.png (256x256)")
    
    # Create smaller sizes
    for icon_size in [128, 64, 32, 16]:
        small = img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
        small.save(f'ollama_image_analyzer/resources/icon_{icon_size}.png', 'PNG')
        print(f"✓ Created icon_{icon_size}.png")
    
    # Create ICO file with multiple sizes
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save('ollama_image_analyzer/resources/icon.ico', format='ICO', sizes=ico_sizes)
    print("✓ Created icon.ico (multi-size)")

if __name__ == '__main__':
    create_icon()
    print("\n✓ All icon files generated successfully!")
