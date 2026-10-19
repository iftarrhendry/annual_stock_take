from pathlib import Path
import json
import pandas as pd

# ==========================================
# CONFIG
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXCEL_FILE = PROJECT_ROOT / "data" / "DATA_AST_LSI.xlsx"
OUTPUT_FILE = Path(__file__).resolve().parent / "data.json"

# ==========================================
# LOAD EXCEL
# mengikuti struktur app.py:
# pd.read_excel(..., header=[0, 1])
# ==========================================

df = pd.read_excel(
    EXCEL_FILE,
    header=[0, 1]
)

# ==========================================
# CLEAN HEADER
# ==========================================

new_columns = []

for col_level_1, col_level_2 in df.columns:

    if "Unnamed" not in str(col_level_2):
        new_columns.append(
            str(col_level_2).strip()
        )
    else:
        new_columns.append(
            str(col_level_1).strip()
        )

df.columns = new_columns

df.columns = [
    col.replace("\n", " ").strip()
    for col in df.columns
]

# ==========================================
# CLEAN DATA
# ==========================================

df = (
    df
    .dropna(how="all")
    .reset_index(drop=True)
)

df["AST Date"] = pd.to_datetime(
    df["AST Date"],
    errors="coerce"
)

df["BATCH"] = df["BATCH"].ffill()

# ==========================================
# CARI KOLOM WH LSI (H-14)
# ==========================================

wh_column = next(
    (
        col
        for col in df.columns
        if "WH LSI" in str(col)
        and "H-14" in str(col)
    ),
    None
)

if wh_column is None:
    raise KeyError(
        "Kolom WH LSI (H-14) tidak ditemukan."
    )

df[wh_column] = pd.to_datetime(
    df[wh_column],
    errors="coerce"
)

# ==========================================
# HANYA JADWAL YANG PUNYA AST DATE
# ==========================================

schedule_df = df[
    df["AST Date"].notna()
].copy()

schedule_df = schedule_df.sort_values(
    by=["AST Date", "BATCH", "STORE"]
)

# ==========================================
# HELPERS
# ==========================================

def clean_text(value):
    if pd.isna(value):
        return ""

    text = str(value).strip()

    if text.lower() == "nan":
        return ""

    return text


def date_to_iso(value):
    if pd.isna(value):
        return ""

    return pd.Timestamp(value).strftime(
        "%Y-%m-%d"
    )


# ==========================================
# BUILD JSON
# ==========================================

records = []

for _, row in schedule_df.iterrows():

    records.append(
        {
            "batch": clean_text(
                row["BATCH"]
            ),
            "store": clean_text(
                row["STORE"]
            ),
            "ast_date": date_to_iso(
                row["AST Date"]
            ),
            "wh_date": date_to_iso(
                row[wh_column]
            ),
            "coord": clean_text(
                row.get("Coord", "")
            ),
            "member1": clean_text(
                row.get("Member1", "")
            ),
            "member2": clean_text(
                row.get("Member2", "")
            ),
            "member3": clean_text(
                row.get("Member3", "")
            )
        }
    )

payload = {
    "meta": {
        "demo": False,
        "source": "DATA_AST_LSI.xlsx",
        "record_count": len(records)
    },
    "records": records
}

OUTPUT_FILE.write_text(
    json.dumps(
        payload,
        ensure_ascii=False,
        indent=2
    ),
    encoding="utf-8"
)

print(
    f"OK: {len(records)} jadwal ditulis ke "
    f"{OUTPUT_FILE}"
)
