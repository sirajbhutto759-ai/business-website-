from PIL import Image, ImageDraw, ImageFont
import os

def create_app_icon():
    # Create multiple sizes for ICO format (16x16, 32x32, 48x48, 64x64, 128x128, 256x256)
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    images = []

    for size in sizes:
        w, h = size
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Rounded rectangle background (Navy / Dark Blue gradient feel)
        pad = int(w * 0.05)
        rect = [pad, pad, w - pad, h - pad]
        corner_radius = int(w * 0.2)

        # Background color: Deep Slate / Tech Blue
        draw.rounded_rectangle(rect, radius=corner_radius, fill=(15, 23, 42, 255), outline=(2, 132, 199, 255), width=max(1, int(w*0.03)))

        # Solar / Lightning Icon graphics
        center_x, center_y = w // 2, h // 2
        
        # Sun rays / Solar circle top right
        sun_r = int(w * 0.18)
        draw.ellipse([w*0.55, h*0.15, w*0.55 + sun_r*2, h*0.15 + sun_r*2], fill=(245, 158, 11, 230))

        # Lightning Bolt ⚡ in Gold / Yellow
        # Coordinates scaled to size
        points = [
            (int(w * 0.52), int(h * 0.22)),
            (int(w * 0.32), int(h * 0.52)),
            (int(w * 0.48), int(h * 0.52)),
            (int(w * 0.40), int(h * 0.82)),
            (int(w * 0.70), int(h * 0.45)),
            (int(w * 0.54), int(h * 0.45)),
        ]
        draw.polygon(points, fill=(234, 179, 8, 255))

        images.append(img)

    # Save as .ico file containing all sizes
    output_path = os.path.join(os.path.dirname(__file__), "app_icon.ico")
    images[0].save(output_path, format="ICO", sizes=[(im.width, im.height) for im in images], append_images=images[1:])
    print(f"Icon created successfully at: {output_path}")

if __name__ == "__main__":
    create_app_icon()
