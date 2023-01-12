import pandas as pd
from pathlib import Path


def save_dict_as_csv(path: Path, dict_: dict, file_name: str):
    df = pd.DataFrame(dict_)
    df.to_csv(path / file_name, index=False)
