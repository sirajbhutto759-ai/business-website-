import os
from PIL import Image

def convert_logo_to_ico():
    png_path = r"c:\Users\siraj\Desktop\Siraj UPS\media\shop_logo\design-a-modern--professional-and-premium-logo-for.png"
    ico_path = r"c:\Users\siraj\Desktop\Siraj UPS\app_icon.ico"
    
    if os.path.exists(png_path):
        img = Image.open(png_path)
        # Convert to RGBA if needed
        img = img.convert("RGBA")
        
        # Save as multi-resolution ICO file
        sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
        resized_imgs = [img.resize(s, Image.Resampling.LANCZOS) for s in sizes]
        
        resized_imgs[0].save(
            ico_path,
            format="ICO",
            sizes=[(im.width, im.height) for im in resized_imgs],
            append_images=resized_imgs[1:]
        )
        print("Converted user logo PNG to app_icon.ico successfully!")
    else:
        print("PNG file not found!")

if __name__ == "__main__":
    convert_logo_to_ico()
