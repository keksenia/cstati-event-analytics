from pathlib import Path
import pandas as pd


def read_csv_robust(path: Path, nrows: int | None = None) -> pd.DataFrame:
    """
    Read CSV with fallback encodings and automatic separator detection.

    Used for raw event exports with potentially different encodings and separators.
    All columns are read as strings to avoid accidental type coercion.
    """
    encodings = ["utf-8-sig", "utf-8", "cp1251"]
    last_error = None

    for encoding in encodings:
        try:
            return pd.read_csv(
                path,
                dtype=str,
                encoding=encoding,
                sep=None,
                engine="python",
                nrows=nrows,
                on_bad_lines="skip",
            )
        except Exception as error:
            last_error = error

    raise RuntimeError(f"Failed to read {path.name}: {last_error}")


def load_manual_csv(path: Path) -> pd.DataFrame:
    """
    Load a manual CSV file such as event_metadata.csv or event_aliases.csv.

    Tries comma and semicolon separators first, then falls back to automatic parsing.
    """
    if not path.exists():
        raise FileNotFoundError(f"Manual file not found: {path}")

    for sep in [",", ";"]:
        try:
            df = pd.read_csv(path, dtype=str, sep=sep)
            df.columns = [col.strip() for col in df.columns]

            if len(df.columns) > 1:
                return df
        except Exception:
            pass

    df = pd.read_csv(path, dtype=str, sep=None, engine="python", on_bad_lines="skip")
    df.columns = [col.strip() for col in df.columns]

    return df


def load_processed_table(directory: Path, name: str) -> pd.DataFrame:
    """
    Load a processed public table from parquet or csv.

    The function first tries parquet, then csv.
    """
    parquet_path = directory / f"{name}.parquet"
    csv_path = directory / f"{name}.csv"

    if parquet_path.exists():
        return pd.read_parquet(parquet_path)

    if csv_path.exists():
        return pd.read_csv(csv_path)

    raise FileNotFoundError(
        f"Neither {name}.parquet nor {name}.csv was found in {directory}"
    )


def clean_filename_event_name(path: Path) -> str:
    """
    Convert raw file name into inferred event name.

    Example:
    'Копия Анализ аудитории - Посвят'25.csv' -> 'Посвят'25'
    """
    name = path.stem
    prefix = "Копия Анализ аудитории - "

    if name.startswith(prefix):
        name = name[len(prefix):]

    return name.strip()

