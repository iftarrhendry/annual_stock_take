import streamlit as st
import pandas as pd
import base64


# ==========================================
# 1. PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Annual Stock Take",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# THEME / CSS
# ==========================================

st.markdown("""
<style>
.stApp {
    background-color: #fffafa;
}

section[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 2px solid #d71920;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #b5122b;
}

h1, h2, h3 {
    color: #b5122b;
}

div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HEADER
# ==========================================

def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(
            image_file.read()
        ).decode()


logo_base64 = get_base64_image(
    "assets/logo.png"
)


header_html = f"""
<div style="
display:flex;
align-items:center;
gap:24px;
background:linear-gradient(135deg,#ffffff 0%,#fff5f5 100%);
border-left:7px solid #d71920;
padding:22px 28px;
border-radius:16px;
box-shadow:0 4px 14px rgba(180,0,20,0.08);
margin-bottom:25px;
">

<div style="
width:110px;
display:flex;
align-items:center;
justify-content:center;
">
<img
src="data:image/png;base64,{logo_base64}"
style="
max-width:100px;
max-height:65px;
object-fit:contain;
">
</div>

<div>
<div style="
font-size:30px;
font-weight:700;
color:#b5122b;
">
Annual Stock Take Dashboard
</div>

<div style="
font-size:15px;
color:#666666;
margin-top:4px;
">
Monitoring and scheduling dashboard for Annual Stock Take
</div>
</div>

</div>
"""

st.html(header_html)

# ==========================================
# 3. LOAD EXCEL
# ==========================================

file_path = "data/DATA_AST_LSI.xlsx"

df = pd.read_excel(
    file_path,
    header=[0, 1]
)


# ==========================================
# 4. CLEAN HEADER
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


# Menghilangkan enter / line break
# pada nama kolom
df.columns = [
    col.replace("\n", " ").strip()
    for col in df.columns
]


# ==========================================
# 5. CLEAN DATA
# ==========================================

# Hapus baris yang seluruh isinya kosong
df = df.dropna(
    how="all"
).reset_index(drop=True)


# Pastikan AST Date dibaca sebagai tanggal
df["AST Date"] = pd.to_datetime(
    df["AST Date"],
    errors="coerce"
)


# Mengisi BATCH yang kosong akibat merged cell Excel
df["BATCH"] = df["BATCH"].ffill()


# ==========================================
# 6. CREATE SCHEDULE DATA
# ==========================================

# Hanya mengambil baris yang punya AST Date
schedule_df = df[
    df["AST Date"].notna()
].copy()


# Tanggal hari ini
today = pd.Timestamp.today().normalize()


# Menghitung countdown
schedule_df["Days Left"] = (
    schedule_df["AST Date"] - today
).dt.days


# ==========================================
# 7. SIDEBAR
# ==========================================

with st.sidebar:

    st.header("Dashboard Filter")

    st.caption(
        "Filter jadwal Annual Stock Take"
    )

    st.divider()


    # --------------------------
    # BATCH FILTER
    # --------------------------

    batch_list = (
        ["All Batch"]
        + sorted(
            schedule_df["BATCH"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
    )

    selected_batch = st.selectbox(
        "Batch",
        batch_list
    )


    # --------------------------
    # STORE FILTER
    # --------------------------

    store_list = (
        ["All Store"]
        + sorted(
            schedule_df["STORE"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
    )

    selected_store = st.selectbox(
        "Store",
        store_list
    )

# ==========================================
# 8. FILTER DATA
# ==========================================

filtered_schedule = schedule_df.copy()


# Filter Batch
if selected_batch != "All Batch":

    filtered_schedule = filtered_schedule[
        filtered_schedule["BATCH"].astype(str)
        == selected_batch
    ]


# Filter Store
if selected_store != "All Store":

    filtered_schedule = filtered_schedule[
        filtered_schedule["STORE"].astype(str)
        == selected_store
    ]

# ==========================================
# 9. NEXT AST CALCULATION
# ==========================================

upcoming_schedule = filtered_schedule[
    filtered_schedule["AST Date"] >= today
].copy()


upcoming_schedule = upcoming_schedule.sort_values(
    by="AST Date"
)


# ==========================================
# 10. NEXT AST DISPLAY
# ==========================================

st.subheader("Next Annual Stock Take")


if not upcoming_schedule.empty:

    next_ast = upcoming_schedule.iloc[0]

    next_store = next_ast["STORE"]
    next_date = next_ast["AST Date"]
    next_batch = next_ast["BATCH"]
    next_day = next_ast["AST Day"]
    next_coord = next_ast["Coord"]
    days_left = next_ast["Days Left"]


    next_ast_html = f"""
    <div style="
        background: linear-gradient(
            135deg,
            #ffffff 0%,
            #fff4f4 100%
        );
        border: 2px solid #d71920;
        border-radius: 18px;
        padding: 28px;
        margin-top: 10px;
        margin-bottom: 24px;
        box-shadow: 0 5px 18px rgba(215,25,32,0.10);
    ">

        <div style="
            font-size: 14px;
            font-weight: 700;
            color: #d71920;
            letter-spacing: 1px;
            margin-bottom: 22px;
        ">
            NEXT ANNUAL STOCK TAKE
        </div>


        <div style="
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 24px;
        ">

            <div>
                <div style="
                    font-size: 12px;
                    color: #777777;
                    font-weight: 600;
                ">
                    STORE
                </div>

                <div style="
                    font-size: 22px;
                    color: #222222;
                    font-weight: 700;
                    margin-top: 5px;
                ">
                    {next_store}
                </div>
            </div>


            <div>
                <div style="
                    font-size: 12px;
                    color: #777777;
                    font-weight: 600;
                ">
                    BATCH
                </div>

                <div style="
                    font-size: 22px;
                    color: #222222;
                    font-weight: 700;
                    margin-top: 5px;
                ">
                    {next_batch}
                </div>
            </div>


            <div>
                <div style="
                    font-size: 12px;
                    color: #777777;
                    font-weight: 600;
                ">
                    AST DATE
                </div>

                <div style="
                    font-size: 22px;
                    color: #222222;
                    font-weight: 700;
                    margin-top: 5px;
                ">
                    {next_date.strftime("%d %b %Y")}
                </div>
            </div>


            <div>
                <div style="
                    font-size: 12px;
                    color: #777777;
                    font-weight: 600;
                ">
                    COUNTDOWN
                </div>

                <div style="
                    font-size: 32px;
                    color: #d71920;
                    font-weight: 800;
                    margin-top: 2px;
                ">
                    {days_left} Days
                </div>
            </div>

        </div>


        <div style="
            border-top: 1px solid #f1c5c8;
            margin-top: 24px;
            padding-top: 16px;
            display: flex;
            gap: 50px;
            font-size: 14px;
            color: #555555;
        ">

            <div>
                <strong>AST Day:</strong>
                {next_day}
            </div>

            <div>
                <strong>Coordinator:</strong>
                {next_coord}
            </div>

        </div>

    </div>
    """

    st.html(next_ast_html)


else:

    st.info(
        "Tidak ada jadwal AST berikutnya "
        "untuk filter yang dipilih."
    )


st.divider()


# ==========================================
# 11. SCHEDULE OVERVIEW
# ==========================================

st.subheader("AST Schedule")


display_columns = [
    "BATCH",
    "CORP",
    "Cd Store",
    "STORE",
    "AST Date",
    "AST Day",
    "Coord",
    "Member1",
    "Member2",
    "Member3",
    "Days Left"
]


# Cek apakah hasil filter kosong
if filtered_schedule.empty:

    st.warning(
        "Tidak ada data yang sesuai dengan filter."
    )

else:

    # Membuat salinan data untuk ditampilkan
    display_df = filtered_schedule[
        display_columns
    ].copy()

    # Mengurutkan berdasarkan AST Date
    display_df = display_df.sort_values(
        by="AST Date"
    )

    # Menampilkan tabel
    st.dataframe(
    display_df,
    hide_index=True,
    use_container_width=True,
    height=500,
    column_config={
        "AST Date": st.column_config.DateColumn(
            "AST Date",
            format="DD MMM YYYY"
        ),

        "Days Left": st.column_config.NumberColumn(
            "Days Left",
            format="%d Days"
        )
    }
)