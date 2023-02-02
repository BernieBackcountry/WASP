import base64
from dash import html
from pathlib import Path


def get_project_path() -> Path:
    return Path.cwd().joinpath('wasp_tool_dash')


def encode_image(path: Path) -> html.Img:
    encoded_image = base64.b64encode(open(path, 'rb').read())
    return html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), height='49%')


def encode_image_pdf(path: Path) -> html.Img:
    encoded_image = base64.b64encode(open(path, 'rb').read())
    return html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), width='90%')
