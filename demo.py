import easyocr
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageFont, ImageDraw, ImageColor

transparent = (0,0,0,0)

def handle_field(field: list, draw: ImageDraw):
    # Get data
    coords = field[0]
    text = field[1]
    confidence = field[2]
    a=coords[0]
    b=coords[1]
    c=coords[2]
    d=coords[3]
    # a --- b
    # |     |
    # d --- c
    width = c[0] - a[0]
    height = d[1] - a[1]
    # Draw rectangle
    draw.rectangle([(a[0], a[1]), (c[0], c[1])],None,"red",2)
    
def main():
    img_path = "demo/ja1.png"
    
    # Perform OCR
    reader = easyocr.Reader(['ja', 'en'])
    result = reader.readtext(img_path)
    print(result)
    
    with Image.open(img_path) as img:
        draw = ImageDraw.Draw(img)
        for field in result:
            handle_field(field, draw)
            
        img.save('result.png')
    
main()