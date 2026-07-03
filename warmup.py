import os
os.environ["FLAGS_use_mkldnn"] = "0"

from paddleocr import PaddleOCR

print("PaddleOCR model indiriliyor / hazırlanıyor...")

ocr = PaddleOCR(
    use_angle_cls=False,
    lang="en",
    use_gpu=False
)

print("PaddleOCR hazır.")