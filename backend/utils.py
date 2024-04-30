import json
import chardet
import re
import base64
from io import BytesIO
import random
from PIL import Image, ImageDraw


def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        data = open(path, "rb").read()
        charset = chardet.detect(data)["encoding"]
        with open(path, "r", encoding=charset) as f:
            return f.read()


def read_record(path):
    with open(path, "r") as f:
        for line in f:
            line = json.loads(line.strip())
            yield line


def write_json_record(path, records):
    with open(path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")


def read_json(path):
    return json.loads(read_file(path))


def write_json(path, obj):
    write_file(path, json.dumps(obj))


def base64_to_image(base64_str, image_path=None):
    base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
    byte_data = base64.b64decode(base64_data)
    image_data = BytesIO(byte_data)
    img = Image.open(image_data)
    if image_path:
        img.save(image_path)
    return img


def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue())
    return img_str


def random_color():
    def r():
        return random.randint(0, 255)

    return '#%02X%02X%02X' % (r(), r(), r())


def draw_rect(image, rect):
    draw = ImageDraw.Draw(image)
    leftx = rect['x']
    lefty = rect['y']
    rightx = rect['x'] + rect['width']
    righty = rect['y'] + rect['height']
    draw.rectangle([(leftx, lefty), (rightx, righty)], outline=random_color())
    return image
