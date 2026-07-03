import os
os.environ["FLAGS_use_mkldnn"] = "0"

from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=False, lang="en", use_gpu=False)

result = ocr.ocr("captcha.jpg", cls=False)
print(result)

texts = []
for line in result:
    if line:
        for item in line:
            texts.append(item[1][0])

print("OKUNAN:", "".join(texts).replace(" ", ""))