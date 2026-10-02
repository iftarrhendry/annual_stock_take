import pandas as pd

file_path = "data/DATA_AST_LSI.xlsx"

# Membaca Excel dengan 2 level header
df = pd.read_excel(
    file_path,
    header=[0, 1]
)

# ==========================================
# 1. MERAPIKAN NAMA KOLOM
# ==========================================

new_columns = []

for col_level_1, col_level_2 in df.columns:

    if "Unnamed" not in str(col_level_2):
        new_columns.append(str(col_level_2).strip())
    else:
        new_columns.append(str(col_level_1).strip())

df.columns = new_columns


# ==========================================
# 2. MERAPIKAN NAMA KOLOM
# ==========================================

df.columns = [
    col.replace("\n", " ").strip()
    for col in df.columns
]


# ==========================================
# 3. HAPUS BARIS YANG SEPENUHNYA KOSONG
# ==========================================

df = df.dropna(
    how="all"
).reset_index(drop=True)


# ==========================================
# 4. UBAH AST DATE MENJADI FORMAT TANGGAL
# ==========================================

df["AST Date"] = pd.to_datetime(
    df["AST Date"],
    errors="coerce"
)


# ==========================================
# 5. CEK HASIL
# ==========================================

print(df.head(10))

print("\nNama kolom:")
print(df.columns.tolist())

print("\nTipe data:")
print(df.dtypes)