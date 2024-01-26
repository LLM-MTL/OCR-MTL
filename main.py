import os
from ocrmtl.ocrmtl import OcrMtl

def main():
    input_dir = ""
    output_dir = ""
    
    ocr = OcrMtl()
    from_code = "ja"
    to_code = "en"
    
    files = os.listdir(input_dir)
    # Filtering only the files.
    files = [f for f in files if os.path.isfile(input_dir+'/'+f)]
    num=1
    for file in files:
        progress = f"Image {num}/{len(files)} ({float(float(num)/float(len(files)))*100}%)"
        print(progress)
        ocr.Run(input_dir+'/'+file, output_dir+'/'+file, from_code, to_code)
        num+=1
    
main()
