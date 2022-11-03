import base64
from dash import html
from pathlib import Path
from typing import Dict, Optional
import yaml


def get_project_path() -> Path:
    return Path('tmt_analyzer_dash')

# DO WE NEED THIS FUNCTION???/
def read_yaml(file_path: Path) -> Optional[Dict[str, dict]]:
    if file_path.is_file():
        with file_path.open(mode='r') as file:
            return yaml.safe_load(file)
    return None


def encode_image(path: Path) -> html.Img:
    encoded_image = base64.b64encode(open(path, 'rb').read())
    return html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), height='49%')
