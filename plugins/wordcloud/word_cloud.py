import sys
import base64
from io import BytesIO, StringIO
from pathlib import Path
from PIL import Image
from matplotlib.pyplot import axes

import numpy as np
from wordcloud import WordCloud, ImageColorGenerator
import jieba
# jieba.enable_parallel(4)

PARENT_PATH = Path(__file__).parent

def jieba_processing_txt(text, stopwords_path):
    mywordlist = []
    seg_list = jieba.cut(text, cut_all=False)
    liststr = "/ ".join(seg_list)

    with open(stopwords_path, encoding='utf-8') as f_stop:
        f_stop_text = f_stop.read()
        f_stop_seg_list = f_stop_text.splitlines()

    for myword in liststr.split('/'):
        if not (myword.strip() in f_stop_seg_list) and len(myword.strip()) > 1:
            mywordlist.append(myword)
    return ' '.join(mywordlist)

def gen_word_cloud(text: str, image_file: Path, font_path):
    image_color = np.array(Image.open(image_file))
    image_mask = np.where(image_color.sum(axis=2) == 255*3, 255, 0)
    wc = WordCloud(
        font_path=str(font_path),
        width=600,
        height=600,
        max_words=500,
        mask=image_mask,
        max_font_size=50,
        repeat=True,
        background_color='white',
        margin=2,
    )
    wc.generate(text)
    image_colors = ImageColorGenerator(image_color)
    wc.recolor(color_func=image_colors)
    return wc.to_image()


if __name__ == '__main__':
    text = ''
    try:
        while True:
            text += input()
    except EOFError:
        pass
    _stdout = sys.stdout
    with StringIO() as f:
        sys.stdout = f
        text = jieba_processing_txt(text, PARENT_PATH / 'stopwords.txt')
    sys.stdout = _stdout
    img = gen_word_cloud(
        text,
        PARENT_PATH / 'huaji.jpg',
        PARENT_PATH / 'SourceHanSansCN-Heavy.otf'
    )
    with BytesIO() as buffer:
        buffer.name = 'ciyun.png'
        img.save(buffer)
        buffer.seek(0)
        print( base64.b64encode(buffer.read()) )
