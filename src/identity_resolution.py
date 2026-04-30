import re
import hmac
import hashlib
import pandas as pd

from .normalizers import (
    normalize_colname,
    clean_raw_value,
)


IDENTIFIER_PATTERNS = {
    "fio": [
        r"^фио$",
        r"фамил",
        r"^имя$",
        r"отчеств",
        r"full name",
        r"first name",
        r"last name",
        r"surname",
    ],
    "telegram": [
        r"telegram",
        r"телеграм",
        r"^tg$",
        r"tg @",
        r"^тг$",
        r"ник в телеграм",
        r"никнейм",
        r"nickname",
        r"username",
        r"t\.me",
    ],
    "phone": [
        r"телефон",
        r"номер телефона",
        r"phone",
        r"mobile",
    ],
    "email": [
        r"^email$",
        r"e-mail",
        r"почта",
        r"mail",
    ],
    "group": [
        r"группа",
        r"^group$",
    ],
    "program": [
        r"направ",
        r"программа",
        r"program",
        r"faculty",
        r"факультет",
    ],
    "course": [
        r"^курс$",
        r"^year$",
    ],
}


def is_unnamed_column(column: str) -> bool:
    """
    Check whether a column is an unnamed spreadsheet artifact.
    """
    return normalize_colname(column).startswith("unnamed")


def detect_identifier_columns(df: pd.DataFrame) -> dict[str, list[str]]:
    """
    Detect columns that likely contain identifiers or segmentation fields.

    Unnamed columns are skipped because they often produce false matches.
    """
    detected = {key: [] for key in IDENTIFIER_PATTERNS}

    for column in df.columns:
        column_norm = normalize_colname(column)

        if is_unnamed_column(column):
            continue

        for role, patterns in IDENTIFIER_PATTERNS.items():
            if any(re.search(pattern, column_norm) for pattern in patterns):
                detected[role].append(column)

    return detected


def coalesce_values(row: pd.Series, columns: list[str]) -> str | None:
    """
    Combine non-empty values from several columns into one string.
    """
    values = []

    for column in columns:
        if column in row.index:
            value = clean_raw_value(row[column])

            if value is not None:
                values.append(value)

    if not values:
        return None

    return " ".join(values)


def build_participant_key(row: pd.Series) -> tuple[str | None, str]:
    """
    Build internal participant key and identity confidence.

    Priority:
    1. Telegram
    2. Phone
    3. Email
    4. FIO signature + group/program/course
    5. FIO signature only
    """
    if pd.notna(row.get("telegram_norm")):
        return f"tg:{row['telegram_norm']}", "high"

    if pd.notna(row.get("phone_norm")):
        return f"phone:{row['phone_norm']}", "high"

    if pd.notna(row.get("email_norm")):
        return f"email:{row['email_norm']}", "high"

    fio = row.get("fio_signature")
    group = row.get("group_norm")
    program = row.get("program_norm")
    course = row.get("course_norm")

    if pd.notna(fio) and pd.notna(group):
        return f"fio_group:{fio}|{group}", "medium"

    if pd.notna(fio) and pd.notna(program) and pd.notna(course):
        return f"fio_program_course:{fio}|{program}|{course}", "medium"

    if pd.notna(fio) and pd.notna(program):
        return f"fio_program:{fio}|{program}", "medium"

    if pd.notna(fio):
        return f"fio_only:{fio}", "low"

    return None, "missing"


def hmac_sha256(value: str | None, salt: str) -> str | None:
    """
    Create HMAC-SHA256 hash for a private identity key.

    The salt must not be published.
    """
    if value is None or pd.isna(value):
        return None

    return hmac.new(
        salt.encode("utf-8"),
        str(value).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def find_strong_id_conflicts(identity_df: pd.DataFrame) -> pd.DataFrame:
    """
    Find cases where one strong identifier maps to multiple FIO signatures.

    Auxiliary sources should be removed before calling this function.
    """
    strong_id_long = []

    for id_col, id_type in [
        ("telegram_norm", "telegram"),
        ("phone_norm", "phone"),
        ("email_norm", "email"),
    ]:
        if id_col not in identity_df.columns:
            continue

        tmp = identity_df[
            identity_df[id_col].notna()
        ][[id_col, "fio_signature", "inferred_event_name", "source_file"]].copy()

        tmp = tmp.rename(columns={id_col: "identifier_value"})
        tmp["identifier_type"] = id_type

        strong_id_long.append(tmp)

    if not strong_id_long:
        return pd.DataFrame(
            columns=[
                "identifier_type",
                "identifier_value",
                "n_fio",
                "n_rows",
                "events",
            ]
        )

    strong_id_long_df = pd.concat(strong_id_long, ignore_index=True)

    conflicts = (
        strong_id_long_df
        .groupby(["identifier_type", "identifier_value"], dropna=False)
        .agg(
            n_fio=("fio_signature", "nunique"),
            n_rows=("fio_signature", "size"),
            events=(
                "inferred_event_name",
                lambda s: ", ".join(sorted(set(s.dropna().astype(str)))[:10]),
            ),
        )
        .reset_index()
    )

    conflicts = conflicts[
        conflicts["n_fio"] > 1
    ].sort_values(["n_fio", "n_rows"], ascending=False)

    return conflicts


def add_identity_conflict_flag(
    identity_df: pd.DataFrame,
    strong_id_conflicts: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add boolean identity_conflict_flag to identity records.
    """
    df = identity_df.copy()

    if strong_id_conflicts.empty:
        df["identity_conflict_flag"] = False
        return df

    conflict_values = set(
        strong_id_conflicts["identifier_value"]
        .dropna()
        .astype(str)
    )

    def has_conflict(row: pd.Series) -> bool:
        for column in ["telegram_norm", "phone_norm", "email_norm"]:
            value = row.get(column)

            if pd.notna(value) and str(value) in conflict_values:
                return True

        return False

    df["identity_conflict_flag"] = df.apply(has_conflict, axis=1)

    return df

