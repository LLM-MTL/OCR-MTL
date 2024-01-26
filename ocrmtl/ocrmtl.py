import re
import easyocr
import requests
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import argostranslate.package
import argostranslate.translate
from PIL import Image, ImageFont, ImageDraw, ImageColor

class OcrMtl:
    transparent = (0,0,0,0)

    def Run(self, img_path, out_path, from_code, to_code) -> str:
        # Perform OCR
        result = self.UseEasyocr(img_path)
        # Edit image
        with Image.open(img_path) as img:
            draw = ImageDraw.Draw(img)
            for field in result:
                self.handle_field(field, img, draw, from_code, to_code)
                
            img.save(out_path)

    def UseEasyocr(self, img_path) -> list:
        reader = easyocr.Reader(['ja', 'en'])
        return reader.readtext(img_path)

    def handle_field(self, field: list, img: Image, draw: ImageDraw, from_code, to_code):
        # Get data
        coords = field[0]
        text = field[1]
        confidence = field[2]
        
        # Filter non-japanese
        regex = r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f]"
        if not re.search(regex, text):
            return
        
        a=coords[0]
        b=coords[1]
        c=coords[2]
        d=coords[3]
        # a --- b
        # |     |
        # d --- c
        width = c[0] - a[0]
        height = d[1] - a[1]
        # Convert to rectange coords
        ra = a
        rb = b
        rc = c
        rd = d
        ra[1] = min(ra[1], rb[1])
        rb[1] = ra[1]
        rc[1] = max(rc[1], rd[1])
        rd[1] = rc[1]
        
        # Get Stats
        med_col, avg_col = self.get_texfield_stats(ra, rc, img)
        
        # Draw polygon
        draw.polygon([(a[0], a[1]), (b[0], b[1]), (c[0], c[1]), (d[0], d[1])],avg_col,None,0)
        
        # Translate
        t_text = ""
        try:
            r = requests.get(f'https://lingva.ml/api/v1/{from_code}/{to_code}/{text}')
            t_text = r.json()["translation"]
        except Exception as ex:
            print(ex)
        if len(t_text) == 0:
            t_text = text
        #print(f"I: '{text}' -> O: '{t_text}'")
        
        # Draw Text
        fnt = ImageFont.truetype("font/unifont-15.1.04.ttf", self.find_max_fontsize(ra, rc, t_text, draw))
        draw.multiline_text(ra, t_text, font=fnt, fill=med_col)
       
    def get_texfield_stats(self, a, c, img) -> tuple:
        cimg = img.crop(box=(a[0], a[1], c[0], c[1]))
        pixels = (c[0]-a[0])*(c[1]-a[1])
        colors = cimg.getcolors(maxcolors=int(pixels+1))
        
        max_item = (0, ())
        sum_r = 0
        sum_g = 0
        sum_b = 0
        for item in colors:
            cnt = item[0]
            color = item[1]
            # Calc medial color
            if cnt > max_item[0]:
                max_item = item
            # Calc avg color
            sum_r += color[0]
            sum_g += color[1]
            sum_b += color[2]
        
        return max_item[1], (int(sum_r/len(colors)), int(sum_g/len(colors)), int(sum_b/len(colors)), 255)
    
    def find_max_fontsize(self, a, c, text, draw) -> int:
        font_size = 1
        upper_bound = -1
        while upper_bound == -1:
            fnt = ImageFont.truetype("font/unifont-15.1.04.ttf", font_size)
            _, _, right, bottom = draw.multiline_textbbox(a, text, font=fnt)
            if right < c[0] and bottom < c[1]:
                font_size += 1
            else:
                upper_bound = font_size
        
        return upper_bound -1