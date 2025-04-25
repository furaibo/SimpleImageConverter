from PIL import Image
from pathlib import Path


def convert_image_file(input_path: Path, save_path: Path, size_limit: tuple):
    # 値の初期化
    img = Image.open(input_path)
    resize_required = False
    new_size = (img.width, img.height)

    # サイズ制限値の取得
    width_limit = size_limit[0]
    height_limit = size_limit[1]

    # リサイズ時のサイズ判定
    if img.width > width_limit and img.height > height_limit:
        resize_required = True
        width_ratio = width_limit / img.width
        height_ratio = height_limit / img.height
        shrink_ratio = min(width_ratio, height_ratio)
        new_size = (int(img.width * shrink_ratio), int(img.height * shrink_ratio))
    elif img.width > width_limit:
        resize_required = True,
        new_size = (width_limit, int(img.height * (width_limit / img.width)))
    elif img.height > height_limit:
        resize_required = True
        new_size = (int(img.width * (height_limit / img.height)), height_limit)

    # アルファチャンネルを含むPNG形式への対処
    if input_path.suffix == ".png" and save_path.suffix != ".png":
        img = img.convert('RGB')

    # リサイズ・変換・保存処理
    if resize_required:
        img_resize = img.resize(new_size)
        img_resize.save(save_path)
    else:
        img.save(save_path)
