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

/* SIDEBAR PREMIUM */

section[data-testid="stSidebar"] {
    box-shadow: 4px 0 18px rgba(0,0,0,0.04);
}

section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding-top: 1.2rem;
    padding-left: 1rem;
    padding-right: 1rem;
}


/* Selectbox */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background-color: #fffafa;
    border: 1px solid #ead6d9;
    border-radius: 10px;
    min-height: 42px;
    transition: all 0.15s ease;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div:hover {
    border-color: #D71920;
    box-shadow: 0 0 0 2px rgba(215,25,32,0.06);
}


/* Label Selectbox */
section[data-testid="stSidebar"] .stSelectbox label {
    color: #7a1d2c;
    font-size: 12px;
    font-weight: 700;
}


/* Caption */
section[data-testid="stSidebar"] .stCaption {
    color: #888888;
}

h1, h2, h3 {
    color: #b5122b;
}

div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}
/* Membuat konten utama lebih compact */
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 1.5rem;
}

/* Mengurangi jarak vertikal antar komponen */
div[data-testid="stVerticalBlock"] {
    gap: 0.8rem;
}

/* Merapatkan judul */
h1, h2, h3 {
    margin-top: 0.3rem !important;
    margin-bottom: 0.5rem !important;
}

/* Divider lebih compact */
hr {
    margin-top: 0.6rem !important;
    margin-bottom: 0.8rem !important;
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

# Membuat status jadwal
def get_schedule_status(days_left):

    if days_left < 0:
        return "Completed"

    elif days_left == 0:
        return "Today"

    elif days_left <= 3:
        return "Soon"

    else:
        return "Upcoming"


schedule_df["Status"] = (
    schedule_df["Days Left"]
    .apply(get_schedule_status)
)

# ==========================================
# 6B. DISPLAY HELPERS
# ==========================================

from html import escape


def get_countdown_info(value):

    if pd.isna(value):

        return {
            "text": "-",
            "days": None,
            "level": "neutral"
        }

    now = pd.Timestamp.now()

    today = now.normalize()

    target = pd.Timestamp(value).normalize()


    # Hari ini
    if target == today:

        return {
            "text": "TODAY",
            "days": 0,
            "level": "urgent"
        }


    # Sudah lewat
    if target < today:

        return {
            "text": "Passed",
            "days": -1,
            "level": "neutral"
        }


    # Countdown
    total_minutes = int(
        (target - now).total_seconds() // 60
    )

    days, remainder = divmod(
        total_minutes,
        24 * 60
    )

    hours, minutes = divmod(
        remainder,
        60
    )


    if days > 0:

        countdown_text = (
            f"{days}D {hours:02d}H {minutes:02d}M"
        )

    else:

        countdown_text = (
            f"{hours:02d}H {minutes:02d}M"
        )


    # Conditional color
    if days < 10:

        level = "urgent"

    elif days <= 20:

        level = "warning"

    else:

        level = "safe"


    return {
        "text": countdown_text,
        "days": days,
        "level": level
    }

def get_days_left_text(value):

    if pd.isna(value):
        return "-"

    now = pd.Timestamp.now()
    target = pd.Timestamp(value).normalize()
    today = now.normalize()

    if target < today:
        return "Selesai"

    if target == today:
        return "Hari ini"

    days = (target - now).days

    if days == 1:
        return "1 hari lagi"

    return f"{days} hari lagi"

def countdown_badge_html(info):

    styles = {

        "urgent": {
            "background": "#fff0f1",
            "color": "#D71920",
            "border": "#f3c8cc"
        },

        "warning": {
            "background": "#fff7e8",
            "color": "#a96300",
            "border": "#f0d5a3"
        },

        "safe": {
            "background": "#edf8f1",
            "color": "#2f7d4a",
            "border": "#cbe6d4"
        },

        "neutral": {
            "background": "#f1f1f1",
            "color": "#777777",
            "border": "#dddddd"
        }
    }


    style = styles.get(
        info["level"],
        styles["neutral"]
    )


    return f"""
    <span style="
        display:inline-block;
        background:{style["background"]};
        color:{style["color"]};
        border:1px solid {style["border"]};
        padding:5px 10px;
        border-radius:999px;
        font-size:10px;
        font-weight:800;
        letter-spacing:0.2px;
        white-space:nowrap;
    ">
        {escape(str(info["text"]))}
    </span>
    """

def status_badge(status):

    if status == "Today":

        return """
        <span style="
            display:inline-block;
            background:#D71920;
            color:#ffffff;
            padding:5px 11px;
            border-radius:999px;
            font-size:10px;
            font-weight:800;
        ">
            Hari ini
        </span>
        """

    elif status == "Soon":

        return """
        <span style="
            display:inline-block;
            background:#fff0f1;
            color:#D71920;
            border:1px solid #f3c8cc;
            padding:5px 11px;
            border-radius:999px;
            font-size:10px;
            font-weight:800;
        ">
            Segera
        </span>
        """

    elif status == "Completed":

        return """
        <span style="
            display:inline-block;
            background:#f1f1f1;
            color:#777777;
            border:1px solid #dddddd;
            padding:5px 11px;
            border-radius:999px;
            font-size:10px;
            font-weight:800;
        ">
            Selesai
        </span>
        """

    else:

        return """
        <span style="
            display:inline-block;
            background:#edf8f1;
            color:#2f7d4a;
            border:1px solid #cbe6d4;
            padding:5px 11px;
            border-radius:999px;
            font-size:10px;
            font-weight:800;
        ">
            Akan datang
        </span>
        """

def format_excel_number(value, decimals=0):

    if pd.isna(value):

        return "-"


    original = str(value).strip()

    if original in ["", "-", "nan"]:

        return "-"


    # Deteksi tanda negatif
    is_negative = (
        "▲" in original
        or original.replace(" ", "").startswith("-")
    )


    # Bersihkan simbol
    raw = (
        original
        .replace("▲", "")
        .replace("−", "-")
        .replace(" ", "")
    )


    if raw.startswith("-"):

        raw = raw[1:]


    # Konversi format angka Indonesia / internasional
    if "," in raw and "." in raw:

        if raw.rfind(",") > raw.rfind("."):

            # Contoh: 1.234,5
            raw = raw.replace(".", "")
            raw = raw.replace(",", ".")

        else:

            # Contoh: 1,234.5
            raw = raw.replace(",", "")

    elif "," in raw:

        # Contoh: 36,1
        raw = raw.replace(",", ".")


    try:

        number = float(raw)

    except ValueError:

        return original


    formatted = f"{abs(number):,.{decimals}f}"


    # Format Indonesia
    formatted = (
        formatted
        .replace(",", "TEMP")
        .replace(".", ",")
        .replace("TEMP", ".")
    )


    if is_negative:

        return f"▲{formatted}"

    return formatted


def metric_value_html(value, decimals=0):

    formatted = format_excel_number(
        value,
        decimals
    )


    is_negative = formatted.startswith("▲")


    text_color = (
        "#D71920"
        if is_negative
        else "#444444"
    )


    return f"""
    <span style="
        color:{text_color};
        font-weight:700;
        font-size:12px;
        white-space:nowrap;
    ">
        {escape(formatted)}
    </span>
    """

# ==========================================
# 7. SIDEBAR
# ==========================================

with st.sidebar:

    # ==========================================
    # SIDEBAR HEADER
    # ==========================================

    st.html(f"""
    <div style="
        background:linear-gradient(
            135deg,
            #ffffff 0%,
            #fff5f5 100%
        );
        border:1px solid #f0dadd;
        border-left:4px solid #D71920;
        border-radius:14px;
        padding:15px 16px;
        margin-bottom:18px;
        box-shadow:0 4px 12px rgba(215,25,32,0.05);
    ">

        <div style="
            display:flex;
            align-items:center;
            gap:10px;
        ">

            <div style="
                width:38px;
                height:38px;
                display:flex;
                align-items:center;
                justify-content:center;
                background:#ffffff;
                border-radius:9px;
            ">
                <img
                    src="data:image/png;base64,{logo_base64}"
                    style="
                        max-width:32px;
                        max-height:28px;
                        object-fit:contain;
                    "
                >
            </div>

            <div>

                <div style="
                    font-size:14px;
                    font-weight:800;
                    color:#9b1c31;
                    letter-spacing:0.4px;
                ">
                    AST CONTROL
                </div>

                <div style="
                    font-size:11px;
                    color:#888888;
                    margin-top:2px;
                ">
                    Operations Dashboard
                </div>

            </div>

        </div>

    </div>
    """)


    # ==========================================
    # FILTER TITLE
    # ==========================================

    st.html("""
    <div style="
        margin-bottom:8px;
    ">

        <div style="
            font-size:13px;
            font-weight:800;
            color:#333333;
            letter-spacing:0.3px;
        ">
            Dashboard Filter
        </div>

        <div style="
            font-size:11px;
            color:#888888;
            margin-top:3px;
        ">
            Pilih batch atau store yang ingin ditampilkan.
        </div>

    </div>
    """)

    st.divider()


    # ==========================================
    # BATCH FILTER
    # ==========================================

    def batch_sort_key(value):

        try:
            return (0, float(value))

        except ValueError:
            return (1, str(value).lower())


    batch_values = (
        schedule_df["BATCH"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    batch_list = (
        ["All Batch"]
        + sorted(
            batch_values,
            key=batch_sort_key
        )
    )

    selected_batch = st.selectbox(
        "Batch",
        batch_list
    )


    # ==========================================
    # STORE FILTER
    # ==========================================

    if selected_batch == "All Batch":

        store_values = (
            schedule_df["STORE"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

    else:

        store_values = (
            schedule_df[
                schedule_df["BATCH"].astype(str)
                == selected_batch
            ]["STORE"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )


    store_list = (
        ["All Store"]
        + sorted(store_values)
    )

    selected_store = st.selectbox(
        "Store",
        store_list
    )
    # ==========================================
    # ACTIVE FILTER INFO
    # ==========================================

    if selected_batch == "All Batch" and selected_store == "All Store":

        filter_text = "Showing all schedules"

    elif selected_batch != "All Batch" and selected_store == "All Store":

        filter_text = f"Batch {selected_batch} selected"

    else:

        filter_text = f"{selected_store} selected"


    st.html(f"""
    <div style="
        background:#fff8f8;
        border:1px solid #f0dadd;
        border-radius:10px;
        padding:10px 12px;
        margin-top:14px;
    ">

        <div style="
            font-size:10px;
            font-weight:800;
            color:#a41728;
            letter-spacing:0.7px;
            margin-bottom:3px;
        ">
            ACTIVE FILTER
        </div>

        <div style="
            font-size:11px;
            color:#777777;
        ">
            {filter_text}
        </div>

    </div>
    """)

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
# 8B. SUMMARY KPI
# ==========================================

total_schedule = len(filtered_schedule)

upcoming_count = (
    filtered_schedule["Status"]
    .isin(["Upcoming", "Soon"])
    .sum()
)

soon_count = (
    filtered_schedule["Status"]
    .eq("Soon")
    .sum()
)

today_count = (
    filtered_schedule["Status"]
    .eq("Today")
    .sum()
)

completed_count = (
    filtered_schedule["Status"]
    .eq("Completed")
    .sum()
)


kpi_html = f"""
<div style="
    display:grid;
    grid-template-columns:repeat(auto-fit, minmax(190px, 1fr));
    gap:16px;
    margin-top:5px;
    margin-bottom:30px;
">

    <!-- TOTAL SCHEDULE -->
    <div style="
        background:#ffffff;
        border:1px solid #eeeeee;
        border-top:4px solid #9b1c31;
        border-radius:16px;
        padding:20px 22px;
        box-shadow:0 6px 18px rgba(0,0,0,0.05);
    ">
        <div style="
            font-size:12px;
            font-weight:700;
            color:#777777;
            letter-spacing:0.8px;
        ">
            TOTAL SCHEDULE
        </div>

        <div style="
            font-size:34px;
            font-weight:800;
            color:#222222;
            margin-top:7px;
        ">
            {total_schedule}
        </div>

        <div style="
            font-size:12px;
            color:#999999;
            margin-top:3px;
        ">
            Total AST pada filter aktif
        </div>
    </div>


    <!-- UPCOMING -->
    <div style="
        background:linear-gradient(135deg,#ffffff,#fff5f5);
        border:1px solid #f3d5d8;
        border-top:4px solid #D71920;
        border-radius:16px;
        padding:20px 22px;
        box-shadow:0 6px 18px rgba(215,25,32,0.07);
    ">
        <div style="
            font-size:12px;
            font-weight:700;
            color:#b5122b;
            letter-spacing:0.8px;
        ">
            UPCOMING
        </div>

        <div style="
            font-size:34px;
            font-weight:800;
            color:#D71920;
            margin-top:7px;
        ">
            {upcoming_count}
        </div>

        <div style="
            font-size:12px;
            color:#8b6a6d;
            margin-top:3px;
        ">
            {soon_count} schedule dalam ≤ 3 hari
        </div>
    </div>


    <!-- TODAY -->
    <div style="
        background:#D71920;
        border:1px solid #D71920;
        border-radius:16px;
        padding:20px 22px;
        box-shadow:0 7px 20px rgba(215,25,32,0.16);
    ">
        <div style="
            font-size:12px;
            font-weight:700;
            color:#ffe3e5;
            letter-spacing:0.8px;
        ">
            TODAY
        </div>

        <div style="
            font-size:34px;
            font-weight:800;
            color:#ffffff;
            margin-top:7px;
        ">
            {today_count}
        </div>

        <div style="
            font-size:12px;
            color:#ffe6e8;
            margin-top:3px;
        ">
            AST yang berlangsung hari ini
        </div>
    </div>


    <!-- COMPLETED -->
    <div style="
        background:#fafafa;
        border:1px solid #e6e6e6;
        border-top:4px solid #666666;
        border-radius:16px;
        padding:20px 22px;
        box-shadow:0 6px 18px rgba(0,0,0,0.04);
    ">
        <div style="
            font-size:12px;
            font-weight:700;
            color:#777777;
            letter-spacing:0.8px;
        ">
            COMPLETED
        </div>

        <div style="
            font-size:34px;
            font-weight:800;
            color:#444444;
            margin-top:7px;
        ">
            {completed_count}
        </div>

        <div style="
            font-size:12px;
            color:#999999;
            margin-top:3px;
        ">
            Schedule yang telah selesai
        </div>
    </div>

</div>
"""

st.html(kpi_html)

# ==========================================
# 8C. AST PROGRESS
# ==========================================

if total_schedule > 0:

    progress_percent = (
        completed_count / total_schedule
    ) * 100

else:

    progress_percent = 0


progress_html = f"""
<div style="
    background:#ffffff;
    border:1px solid #eeeeee;
    border-radius:16px;
    padding:18px 22px;
    box-shadow:0 5px 16px rgba(0,0,0,0.04);
    margin-top:2px;
    margin-bottom:22px;
">

    <div style="
        display:flex;
        justify-content:space-between;
        align-items:center;
        margin-bottom:10px;
    ">

        <div>
            <div style="
                font-size:12px;
                font-weight:800;
                color:#9b1c31;
                letter-spacing:0.7px;
            ">
                AST PROGRESS
            </div>

            <div style="
                font-size:13px;
                color:#777777;
                margin-top:3px;
            ">
                {completed_count} dari {total_schedule} schedule telah selesai
            </div>
        </div>

        <div style="
            font-size:18px;
            font-weight:800;
            color:#D71920;
        ">
            {progress_percent:.0f}%
        </div>

    </div>


    <div style="
        width:100%;
        height:10px;
        background:#f3eeee;
        border-radius:999px;
        overflow:hidden;
    ">

        <div style="
            width:{progress_percent:.2f}%;
            height:100%;
            background:linear-gradient(
                90deg,
                #9b1c31,
                #D71920
            );
            border-radius:999px;
        ">
        </div>

    </div>

</div>
"""

st.html(progress_html)

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

if not upcoming_schedule.empty:

    # ==========================================
    # BASIC INFORMATION
    # ==========================================

    next_ast = upcoming_schedule.iloc[0]

    next_batch = next_ast["BATCH"]
    next_date = next_ast["AST Date"]
    next_day = next_ast["AST Day"]

    # Warehouse column
    wh_column = next(
        (
            col
            for col in schedule_df.columns
            if "WH LSI" in str(col)
            and "H-14" in str(col)
        ),
        None
    )

    next_wh_date = (
        next_ast[wh_column]
        if wh_column is not None
        else pd.NaT
    )


    # ==========================================
    # FORMAT DATE
    # ==========================================

    def format_card_date(value):

        if pd.isna(value):
            return "-"

        return pd.Timestamp(value).strftime(
            "%d %B %Y"
        )


    # ==========================================
    # INDONESIAN COUNTDOWN
    # ==========================================

    def format_indonesian_countdown(value):

        if pd.isna(value):
            return {
                "text": "-",
                "days": None,
                "level": "neutral"
            }

        now = pd.Timestamp.now()
        target = pd.Timestamp(value).normalize()

        time_left = target - now

        if time_left.total_seconds() <= 0:

            if target.normalize() == now.normalize():

                return {
                    "text": "Hari ini",
                    "days": 0,
                    "level": "urgent"
                }

            return {
                "text": "Sudah lewat",
                "days": -1,
                "level": "neutral"
            }


        total_minutes = int(
            time_left.total_seconds() // 60
        )

        days, remainder = divmod(
            total_minutes,
            24 * 60
        )

        hours, minutes = divmod(
            remainder,
            60
        )


        if days > 0:

            text = (
                f"{days} hari "
                f"{hours} jam "
                f"{minutes} menit lagi"
            )

        elif hours > 0:

            text = (
                f"{hours} jam "
                f"{minutes} menit lagi"
            )

        else:

            text = (
                f"{minutes} menit lagi"
            )


        if days < 10:
            level = "urgent"

        elif days <= 20:
            level = "warning"

        else:
            level = "safe"


        return {
            "text": text,
            "days": days,
            "level": level
        }


    # Countdown AST
    ast_countdown = format_indonesian_countdown(
        next_date
    )

    # Countdown Warehouse
    wh_countdown = format_indonesian_countdown(
        next_wh_date
    )


    # ==========================================
    # COUNTDOWN COLOR
    # ==========================================

    countdown_colors = {

        "urgent": {
            "background": "#D71920",
            "soft": "#fff0f1",
            "text": "#D71920"
        },

        "warning": {
            "background": "#d98200",
            "soft": "#fff7e8",
            "text": "#a96300"
        },

        "safe": {
            "background": "#2f7d4a",
            "soft": "#edf8f1",
            "text": "#2f7d4a"
        },

        "neutral": {
            "background": "#777777",
            "soft": "#f1f1f1",
            "text": "#777777"
        }
    }


    countdown_style = countdown_colors[
        ast_countdown["level"]
    ]


    # ==========================================
    # STORE VIEW
    # ==========================================

    if selected_store != "All Store":

        store_name = str(selected_store)

        store_members = [
            next_ast["Member1"],
            next_ast["Member2"],
            next_ast["Member3"]
        ]

        store_members = [
            str(member).strip()
            for member in store_members
            if pd.notna(member)
            and str(member).strip()
            not in ["", "-", "nan"]
        ]

        team_text = (
            " • ".join(store_members)
            if store_members
            else "-"
        )

        card_title = "JADWAL AST BERIKUTNYA"


        content_html = f"""
        <div>

            <!-- STORE -->
            <div style="
                margin-bottom:16px;
            ">

                <div style="
                    font-size:10px;
                    font-weight:800;
                    color:#a41728;
                    letter-spacing:0.9px;
                    margin-bottom:5px;
                ">
                    STORE
                </div>

                <div style="
                    font-size:28px;
                    font-weight:800;
                    color:#222222;
                    line-height:1.15;
                ">
                    {store_name}
                </div>

                <div style="
                    font-size:12px;
                    color:#888888;
                    margin-top:4px;
                ">
                    Batch {next_batch}
                </div>

            </div>


            <!-- DATES -->
            <div style="
                display:grid;
                grid-template-columns:
                    repeat(2, minmax(0,1fr));
                gap:12px;
                margin-bottom:12px;
            ">

                <!-- WAREHOUSE -->
                <div style="
                    background:#ffffff;
                    border:1px solid #f0dddd;
                    border-radius:12px;
                    padding:14px;
                ">

                    <div style="
                        font-size:10px;
                        font-weight:800;
                        color:#a41728;
                        letter-spacing:0.8px;
                        margin-bottom:6px;
                    ">
                        WH LSI (H-14)
                    </div>

                    <div style="
                        font-size:18px;
                        font-weight:800;
                        color:#333333;
                    ">
                        {format_card_date(next_wh_date)}
                    </div>

                    <div style="
                        font-size:11px;
                        color:{countdown_colors[wh_countdown["level"]]["text"]};
                        font-weight:700;
                        margin-top:6px;
                    ">
                        {wh_countdown["text"]}
                    </div>

                </div>


                <!-- AST DATE -->
                <div style="
                    background:#ffffff;
                    border:1px solid #f0dddd;
                    border-radius:12px;
                    padding:14px;
                ">

                    <div style="
                        font-size:10px;
                        font-weight:800;
                        color:#a41728;
                        letter-spacing:0.8px;
                        margin-bottom:6px;
                    ">
                        AST DATE
                    </div>

                    <div style="
                        font-size:18px;
                        font-weight:800;
                        color:#333333;
                    ">
                        {format_card_date(next_date)}
                    </div>

                    <div style="
                        font-size:11px;
                        color:#777777;
                        margin-top:6px;
                    ">
                        {next_day}
                    </div>

                </div>

            </div>


            <!-- PEOPLE -->
            <div style="
                display:grid;
                grid-template-columns:
                    0.8fr 1.2fr;
                gap:12px;
            ">

                <!-- COORDINATOR -->
                <div style="
                    background:#fffafa;
                    border:1px solid #f0dddd;
                    border-radius:12px;
                    padding:14px;
                ">

                    <div style="
                        font-size:10px;
                        font-weight:800;
                        color:#a41728;
                        letter-spacing:0.8px;
                        margin-bottom:6px;
                    ">
                        COORDINATOR
                    </div>

                    <div style="
                        font-size:13px;
                        font-weight:600;
                        color:#444444;
                        line-height:1.45;
                    ">
                        {next_ast["Coord"]}
                    </div>

                </div>


                <!-- TEAM -->
                <div style="
                    background:#fffafa;
                    border:1px solid #f0dddd;
                    border-radius:12px;
                    padding:14px;
                ">

                    <div style="
                        font-size:10px;
                        font-weight:800;
                        color:#a41728;
                        letter-spacing:0.8px;
                        margin-bottom:6px;
                    ">
                        TEAM
                    </div>

                    <div style="
                        font-size:12px;
                        color:#555555;
                        line-height:1.5;
                    ">
                        {team_text}
                    </div>

                </div>

            </div>

        </div>
        """


    # ==========================================
    # BATCH VIEW
    # ==========================================

    else:

        card_title = "JADWAL AST BERIKUTNYA"


        next_batch_data = schedule_df[
            schedule_df["BATCH"].astype(str)
            == str(next_batch)
        ].copy()


        batch_store_data = (
            next_batch_data
            .drop_duplicates(
                subset=["STORE"]
            )
            .copy()
        )


        store_cards_html = ""


        for _, store_row in batch_store_data.iterrows():

            members = [
                store_row["Member1"],
                store_row["Member2"],
                store_row["Member3"]
            ]

            members = [
                str(member).strip()
                for member in members
                if pd.notna(member)
                and str(member).strip()
                not in ["", "-", "nan"]
            ]

            team_text = (
                " • ".join(members)
                if members
                else "-"
            )


            store_cards_html += f"""
            <div style="
                background:#fffafa;
                border:1px solid #f0dddd;
                border-radius:12px;
                padding:14px;
                min-width:0;
                min-height:145px;
            ">

                <div style="
                    font-size:13px;
                    font-weight:800;
                    color:#333333;
                    line-height:1.35;
                    margin-bottom:9px;
                ">
                    {store_row["STORE"]}
                </div>


                <div style="
                    height:1px;
                    background:#f2e1e3;
                    margin-bottom:10px;
                "></div>


                <div style="
                    font-size:9px;
                    font-weight:800;
                    color:#a41728;
                    letter-spacing:0.7px;
                    margin-bottom:4px;
                ">
                    COORDINATOR
                </div>

                <div style="
                    font-size:11px;
                    font-weight:600;
                    color:#444444;
                    line-height:1.4;
                ">
                    {store_row["Coord"]}
                </div>


                <div style="
                    font-size:9px;
                    font-weight:800;
                    color:#a41728;
                    letter-spacing:0.7px;
                    margin-top:10px;
                    margin-bottom:4px;
                ">
                    TEAM
                </div>

                <div style="
                    font-size:10px;
                    color:#666666;
                    line-height:1.45;
                    overflow-wrap:anywhere;
                ">
                    {team_text}
                </div>

            </div>
            """


        content_html = f"""
        <div>

            <!-- DATES -->
            <div style="
                display:grid;
                grid-template-columns:
                    repeat(2, minmax(0,1fr));
                gap:12px;
                margin-bottom:14px;
            ">

                <!-- WAREHOUSE -->
                <div style="
                    background:#ffffff;
                    border:1px solid #f0dddd;
                    border-radius:12px;
                    padding:14px;
                ">

                    <div style="
                        font-size:10px;
                        font-weight:800;
                        color:#a41728;
                        letter-spacing:0.8px;
                        margin-bottom:6px;
                    ">
                        WH LSI (H-14)
                    </div>

                    <div style="
                        font-size:18px;
                        font-weight:800;
                        color:#333333;
                    ">
                        {format_card_date(next_wh_date)}
                    </div>

                    <div style="
                        font-size:11px;
                        color:{countdown_colors[wh_countdown["level"]]["text"]};
                        font-weight:700;
                        margin-top:6px;
                    ">
                        {wh_countdown["text"]}
                    </div>

                </div>


                <!-- AST -->
                <div style="
                    background:#ffffff;
                    border:1px solid #f0dddd;
                    border-radius:12px;
                    padding:14px;
                ">

                    <div style="
                        font-size:10px;
                        font-weight:800;
                        color:#a41728;
                        letter-spacing:0.8px;
                        margin-bottom:6px;
                    ">
                        AST DATE
                    </div>

                    <div style="
                        font-size:18px;
                        font-weight:800;
                        color:#333333;
                    ">
                        {format_card_date(next_date)}
                    </div>

                    <div style="
                        font-size:11px;
                        color:#777777;
                        margin-top:6px;
                    ">
                        {next_day}
                    </div>

                </div>

            </div>


            <!-- STORES -->
            <div style="
                font-size:10px;
                font-weight:800;
                color:#999999;
                letter-spacing:0.8px;
                margin-bottom:8px;
            ">
                TOKO DALAM BATCH
            </div>


            <div style="
                display:grid;
                grid-template-columns:
                    repeat(3, minmax(0,1fr));
                gap:10px;
            ">
                {store_cards_html}
            </div>

        </div>
        """


    # ==========================================
    # MAIN CARD
    # ==========================================

    next_ast_html = f"""
    <style>

        .ast-card-main {{
            background:
                linear-gradient(
                    135deg,
                    #ffffff 0%,
                    #fff8f8 100%
                );

            border:1px solid #eeeeee;

            border-top:5px solid #D71920;

            border-radius:18px;

            padding:24px 26px;

            box-shadow:
                0 7px 22px
                rgba(0,0,0,0.06);

            margin-top:5px;
            margin-bottom:20px;
        }}


        .ast-card-header {{
            display:flex;
            justify-content:space-between;
            align-items:center;

            margin-bottom:20px;
        }}


        .ast-card-title {{
            font-size:12px;
            font-weight:800;
            color:#D71920;
            letter-spacing:1px;
        }}


        .ast-batch-badge {{
            background:#D71920;
            color:#ffffff;

            padding:7px 14px;

            border-radius:999px;

            font-size:11px;
            font-weight:800;
        }}


        .ast-card-body {{
            display:grid;

            grid-template-columns:
                minmax(0,1fr)
                300px;

            gap:22px;

            align-items:stretch;
        }}


        .ast-countdown {{
            background:linear-gradient(
                145deg,
                #C8141C 0%,
                #D71920 55%,
                #E12229 100%
            );

            border-radius:18px;

            padding:24px 18px;

            display:flex;
            flex-direction:column;

            justify-content:center;
            align-items:center;

            text-align:center;

            min-height:100%;

            box-shadow:
                0 8px 22px
                rgba(215,25,32,0.18);
        }}


        .ast-countdown-label {{
            font-size:11px;
            font-weight:700;

            color:#ffe5e7;

            letter-spacing:1px;

            margin-bottom:10px;
        }}


        .ast-countdown-number {{
            font-size:27px;
            font-weight:900;

            color:#ffffff;

            line-height:1.3;

            max-width:100%;

            word-break:break-word;
        }}


        .ast-countdown-line {{
            width:50px;
            height:2px;

            background:#ffffff;

            opacity:0.25;

            margin:15px 0;
        }}


        .ast-countdown-description {{
            font-size:11px;

            color:#ffe8e9;

            line-height:1.5;
        }}


        @media (max-width: 900px) {{

            .ast-card-body {{
                grid-template-columns:1fr;
            }}

            .ast-countdown {{
                min-height:180px;
            }}

            .stores-grid {{
                grid-template-columns:1fr;
            }}

        }}

    </style>


    <div class="ast-card-main">

        <!-- HEADER -->
        <div class="ast-card-header">

            <div class="ast-card-title">
                {card_title}
            </div>

            <div class="ast-batch-badge">
                BATCH {next_batch}
            </div>

        </div>


        <!-- BODY -->
        <div class="ast-card-body">

            <!-- LEFT -->
            <div>
                {content_html}
            </div>


            <!-- RIGHT -->
            <div class="ast-countdown">

                <div class="ast-countdown-label">
                    WAKTU MENUJU AST
                </div>

                <div class="ast-countdown-number">
                    {ast_countdown["text"]}
                </div>

                <div class="ast-countdown-line"></div>

                <div class="ast-countdown-description">
                    Annual Stock Take
                </div>

            </div>

        </div>

    </div>
    """

    st.html(next_ast_html)

else:

    st.info(
        "Tidak ada jadwal AST berikutnya untuk filter yang dipilih."
    )

st.divider()

# ==========================================
# 11. JADWAL AST
# ==========================================

st.subheader("Jadwal AST")
st.caption(
    "Jadwal persiapan gudang dan pelaksanaan Annual Stock Take."
)

if filtered_schedule.empty:

    st.warning(
        "Tidak ada data yang sesuai dengan filter."
    )

else:

    display_df = filtered_schedule.copy()


    # ==========================================
    # CARI KOLOM WH H-14
    # ==========================================

    wh_column = next(
        (
            col
            for col in schedule_df.columns
            if "WH LSI" in str(col)
            and "H-14" in str(col)
        ),
        None
    )


    # ==========================================
    # GABUNGKAN MEMBER MENJADI TIM
    # ==========================================

    def combine_members(row):

        members = [
            row["Member1"],
            row["Member2"],
            row["Member3"]
        ]

        members = [
            str(member).strip()
            for member in members
            if pd.notna(member)
            and str(member).strip()
            not in ["", "-", "nan"]
        ]

        return (
            " • ".join(members)
            if members
            else "-"
        )


    display_df["Team"] = display_df.apply(
        combine_members,
        axis=1
    )


    # ==========================================
    # URUTKAN
    # ==========================================

    display_df = display_df.sort_values(
        by=["AST Date", "BATCH", "STORE"]
    )


    # ==========================================
    # BANGUN BARIS TABEL
    # ==========================================

    rows_html = ""


    for _, row in display_df.iterrows():

        # ==========================================
        # WH H-14
        # ==========================================

        if wh_column is not None:

            wh_value = row[wh_column]

            wh_info = get_countdown_info(
                wh_value
            )

            wh_days_text = get_days_left_text(
                wh_value
            )

        else:

            wh_info = {
                "text": "-",
                "days": None,
                "level": "neutral"
            }

            wh_days_text = "-"


        # ==========================================
        # AST
        # ==========================================

        ast_value = row["AST Date"]

        ast_info = get_countdown_info(
            ast_value
        )

        ast_days_text = get_days_left_text(
            ast_value
        )


        # ==========================================
        # FORMAT TANGGAL AST
        # ==========================================

        if pd.notna(ast_value):

            formatted_date = pd.Timestamp(
                ast_value
            ).strftime("%d %b %Y")

        else:

            formatted_date = "-"


        # ==========================================
        # FORMAT ANGKA
        # ==========================================

        budget_html = metric_value_html(
            row["Budget 2026"],
            decimals=0
        )

        gap_html = metric_value_html(
            row["Gap"],
            decimals=0
        )

        gr_ly_html = metric_value_html(
            row["G/R LY"],
            decimals=1
        )


        # ==========================================
        # STATUS
        # ==========================================

        status_html = status_badge(
            str(row["Status"])
        )


        # ==========================================
        # BARIS
        # ==========================================

        rows_html += f"""
        <tr>

            <!-- BATCH -->
            <td>
                <span style="
                    display:inline-block;
                    background:#fff1f2;
                    color:#a41728;
                    padding:5px 9px;
                    border-radius:8px;
                    font-size:11px;
                    font-weight:800;
                ">
                    {escape(str(row["BATCH"]))}
                </span>
            </td>


            <!-- TOKO -->
            <td>
                <div style="
                    font-weight:700;
                    color:#2c2c2c;
                    line-height:1.35;
                ">
                    {escape(str(row["STORE"]))}
                </div>
            </td>


            <!-- WH -->
            <td>
                {countdown_badge_html({
                    "text": wh_days_text,
                    "days": wh_info["days"],
                    "level": wh_info["level"]
                })}
            </td>


            <!-- TANGGAL AST -->
            <td>
                <span style="
                    font-weight:700;
                    color:#333333;
                    white-space:nowrap;
                ">
                    {formatted_date}
                </span>
            </td>


            <!-- SISA WAKTU AST -->
            <td>
                {countdown_badge_html({
                    "text": ast_days_text,
                    "days": ast_info["days"],
                    "level": ast_info["level"]
                })}
            </td>


            <!-- KOORDINATOR -->
            <td>
                <span style="
                    color:#444444;
                    font-weight:600;
                    font-size:12px;
                    line-height:1.4;
                ">
                    {escape(str(row["Coord"]))}
                </span>
            </td>


            <!-- TIM -->
            <td>
                <span style="
                    color:#666666;
                    font-size:11px;
                    line-height:1.5;
                ">
                    {escape(str(row["Team"]))}
                </span>
            </td>


            <!-- ANGGARAN -->
            <td style="
                text-align:right;
                white-space:nowrap;
            ">
                {budget_html}
            </td>


            <!-- SELISIH -->
            <td style="
                text-align:right;
                white-space:nowrap;
            ">
                {gap_html}
            </td>


            <!-- G/R LY -->
            <td style="
                text-align:right;
                white-space:nowrap;
            ">
                {gr_ly_html}
            </td>


            <!-- STATUS -->
            <td>
                {status_html}
            </td>

        </tr>
        """


    # ==========================================
    # HEADER TABEL
    # ==========================================

    headers = [
        ("BATCH", "left"),
        ("TOKO", "left"),
        ("WH H-14", "left"),
        ("TANGGAL AST", "left"),
        ("SISA WAKTU", "left"),
        ("KOORDINATOR", "left"),
        ("TIM", "left"),
        ("ANGGARAN", "right"),
        ("SELISIH", "right"),
        ("G/R LY", "right"),
        ("STATUS", "left")
    ]


    header_html = ""


    for label, alignment in headers:

        header_html += f"""
        <th style="
            padding:12px 10px;
            text-align:{alignment};
            color:#9b1c31;
            font-size:10px;
            font-weight:800;
            letter-spacing:0.5px;
            white-space:nowrap;
            position:sticky;
            top:0;
            background:#fff5f5;
            z-index:2;
        ">
            {label}
        </th>
        """


    # ==========================================
    # TABEL
    # ==========================================

    table_html = f"""
    <div style="
        background:#ffffff;
        border:1px solid #eeeeee;
        border-radius:16px;
        overflow:hidden;
        box-shadow:0 6px 20px rgba(0,0,0,0.05);
        width:100%;
    ">

        <!-- HEADER -->
        <div style="
            background:linear-gradient(
                135deg,
                #a9172c 0%,
                #D71920 100%
            );

            padding:14px 18px;

            display:flex;
            justify-content:space-between;
            align-items:center;
        ">

            <div style="
                color:#ffffff;
                font-size:13px;
                font-weight:800;
                letter-spacing:0.6px;
            ">
                JADWAL ANNUAL STOCK TAKE
            </div>

            <div style="
                color:#ffe8e9;
                font-size:11px;
                font-weight:600;
            ">
                {len(display_df)} jadwal
            </div>

        </div>


        <!-- ISI TABEL -->
        <div style="
            max-height:520px;
            overflow-x:auto;
            overflow-y:auto;
        ">

            <table style="
                width:100%;
                min-width:1095px;
                border-collapse:collapse;
                font-family:Arial,sans-serif;
                font-size:12px;
                table-layout:auto;
            ">

                <thead>

                    <tr>
                        {header_html}
                    </tr>

                </thead>


                <tbody>

                    {rows_html}

                </tbody>

            </table>

        </div>

    </div>


    <style>

        table tbody tr {{
            border-bottom:1px solid #f1f1f1;
            transition:background 0.15s ease;
        }}


        table tbody tr:nth-child(even) {{
            background:#fffafa;
        }}


        table tbody tr:hover {{
            background:#fff1f2;
        }}


        table tbody td {{
            padding:11px 10px;
            vertical-align:middle;
        }}

    </style>
    """

    st.html(table_html)