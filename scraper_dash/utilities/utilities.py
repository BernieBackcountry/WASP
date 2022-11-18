import base64
from dash import html
from pathlib import Path
from typing import Dict, Optional


def get_project_path() -> Path:
    return Path('scraper_dash')


def get_data_path() -> Path:
    return Path('scraper_data') 


def encode_image(path: Path) -> html.Img:
    encoded_image = base64.b64encode(open(path, 'rb').read())
    return html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), height='49%')
