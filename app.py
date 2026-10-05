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
    # AMBIL NEXT SCHEDULE
    # ==========================================

    next_ast = upcoming_schedule.iloc[0]

    next_batch = next_ast["BATCH"]
    next_date = next_ast["AST Date"]
    next_day = next_ast["AST Day"]
    next_coord = next_ast["Coord"]

    # ==========================================
    # COUNTDOWN
    # AST Date dianggap mulai pukul 00:00
    # ==========================================

    now = pd.Timestamp.now()

    target_datetime = pd.Timestamp(
        next_date
    ).normalize()

    time_left = target_datetime - now

    if time_left.total_seconds() <= 0:

        countdown_number = "TODAY"
        countdown_label = "AST DAY"

    else:

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

        countdown_number = (
            f"{days}D {hours:02d}H {minutes:02d}M"
        )

        countdown_label = "TIME LEFT"

    # ==========================================
    # STORE VIEW / BATCH VIEW
    # ==========================================

    if selected_store != "All Store":

        card_title = "YOUR NEXT ANNUAL STOCK TAKE"

        store_name = selected_store

        store_members = [
            next_ast["Member1"],
            next_ast["Member2"],
            next_ast["Member3"]
        ]

        store_members = [
            str(member).strip()
            for member in store_members
            if pd.notna(member)
            and str(member).strip() not in ["", "-", "nan"]
        ]

        team_text = (
            " • ".join(store_members)
            if store_members
            else "-"
        )

        main_identity_html = f"""
        <div>

            <div style="
                font-size:10px;
                font-weight:800;
                color:#999999;
                letter-spacing:0.9px;
                margin-bottom:5px;
            ">
                STORE
            </div>

            <div style="
                font-size:30px;
                font-weight:800;
                color:#222222;
                line-height:1.15;
                margin-bottom:8px;
            ">
                {store_name}
            </div>

            <div style="
                margin-bottom:18px;
            ">

                <div style="
                    font-size:10px;
                    font-weight:800;
                    color:#a41728;
                    letter-spacing:0.8px;
                    margin-bottom:4px;
                ">
                    AST DATE
                </div>

                <div style="
                    font-size:22px;
                    font-weight:800;
                    color:#333333;
                ">
                    {next_date.strftime("%d %B %Y")}
                </div>

                <div style="
                    font-size:12px;
                    color:#777777;
                    margin-top:2px;
                ">
                    {next_day}
                </div>

            </div>

            <div style="
                display:flex;
                gap:12px;
                width:100%;
            ">

                <div style="
                    flex:1;
                    min-width:0;
                    background:#fffafa;
                    border:1px solid #f0dddd;
                    border-radius:12px;
                    padding:13px 14px;
                ">

                    <div style="
                        font-size:10px;
                        font-weight:800;
                        color:#a41728;
                        letter-spacing:0.7px;
                        margin-bottom:6px;
                    ">
                        COORDINATOR
                    </div>

                    <div style="
                        font-size:13px;
                        font-weight:600;
                        color:#444444;
                        overflow-wrap:anywhere;
                    ">
                        {next_coord}
                    </div>

                </div>

                <div style="
                    flex:1.4;
                    min-width:0;
                    background:#fffafa;
                    border:1px solid #f0dddd;
                    border-radius:12px;
                    padding:13px 14px;
                ">

                    <div style="
                        font-size:10px;
                        font-weight:800;
                        color:#a41728;
                        letter-spacing:0.7px;
                        margin-bottom:6px;
                    ">
                        TEAM
                    </div>

                    <div style="
                        font-size:12px;
                        color:#555555;
                        line-height:1.5;
                        overflow-wrap:anywhere;
                    ">
                        {team_text}
                    </div>

                </div>

            </div>

        </div>
        """

    else:

        card_title = "NEXT ANNUAL STOCK TAKE"

        next_batch_data = schedule_df[
            schedule_df["BATCH"].astype(str)
            == str(next_batch)
        ].copy()

        batch_stores = (
            next_batch_data["STORE"]
            .dropna()
            .astype(str)
            .drop_duplicates()
            .tolist()
        )

        store_html = ""

        for store in batch_stores:

            store_html += f"""
            <div style="
                background:#fff5f5;
                border:1px solid #f3d5d8;
                border-radius:10px;
                padding:10px 14px;
                font-size:13px;
                font-weight:600;
                color:#8f1d2d;
            ">
                {store}
            </div>
            """

        main_identity_html = f"""
        <div>

            <div style="
                font-size:10px;
                font-weight:800;
                color:#999999;
                letter-spacing:0.9px;
                margin-bottom:5px;
            ">
                AST DATE
            </div>

            <div style="
                font-size:27px;
                font-weight:800;
                color:#222222;
                margin-bottom:5px;
            ">
                {next_date.strftime("%d %B %Y")}
            </div>

            <div style="
                font-size:14px;
                color:#777777;
                margin-bottom:18px;
            ">
                {next_day}
            </div>

            <div style="
                font-size:10px;
                font-weight:800;
                color:#999999;
                letter-spacing:0.8px;
                margin-bottom:8px;
            ">
                STORES
            </div>

            <div style="
                display:grid;
                grid-template-columns:repeat(3, minmax(0,1fr));
                gap:10px;
            ">
                {store_html}
            </div>

        </div>
        """

    # ==========================================
    # NEXT AST CARD
    # ==========================================

    next_ast_html = f"""
    <div style="
        background:linear-gradient(
            135deg,
            #ffffff 0%,
            #fff8f8 100%
        );
        border:1px solid #eeeeee;
        border-top:5px solid #D71920;
        border-radius:18px;
        padding:24px 26px;
        box-shadow:0 7px 22px rgba(0,0,0,0.06);
        margin-top:5px;
        margin-bottom:20px;
    ">

        <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
            margin-bottom:22px;
        ">

            <div style="
                font-size:12px;
                font-weight:800;
                color:#D71920;
                letter-spacing:1px;
            ">
                {card_title}
            </div>

            <div style="
                background:#D71920;
                color:#ffffff;
                padding:7px 14px;
                border-radius:999px;
                font-size:11px;
                font-weight:800;
            ">
                BATCH {next_batch}
            </div>

        </div>

        <div style="
            display:flex;
            gap:24px;
            align-items:stretch;
            width:100%;
        ">

            <div style="
                flex:1;
                min-width:0;
            ">

                {main_identity_html}

            </div>

            <div style="
                width:280px;
                flex-shrink:0;
                background:linear-gradient(
                    145deg,
                    #C8141C 0%,
                    #D71920 55%,
                    #E12229 100%
                );
                border-radius:18px;
                padding:22px 18px;
                display:flex;
                flex-direction:column;
                justify-content:center;
                align-items:center;
                text-align:center;
                box-shadow:0 8px 22px rgba(215,25,32,0.18);
            ">

                <div style="
                    font-size:11px;
                    font-weight:700;
                    color:#ffe5e7;
                    letter-spacing:1px;
                    margin-bottom:9px;
                ">
                    {countdown_label}
                </div>

                <div style="
                    font-size:32px;
                    font-weight:900;
                    color:#ffffff;
                    line-height:1.15;
                    white-space:nowrap;
                    letter-spacing:-0.5px;
                ">
                    {countdown_number}
                </div>

                <div style="
                    width:50px;
                    height:2px;
                    background:#ffffff;
                    opacity:0.25;
                    margin:14px 0;
                    border-radius:10px;
                ">
                </div>

                <div style="
                    font-size:11px;
                    color:#ffe8e9;
                    line-height:1.5;
                ">
                    Countdown to Annual Stock Take
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
# 11. SCHEDULE OVERVIEW
# ==========================================

st.subheader("AST Schedule")
st.caption("Annual Stock Take schedule berdasarkan filter aktif.")

if filtered_schedule.empty:

    st.warning("Tidak ada data yang sesuai dengan filter.")

else:

    display_df = filtered_schedule.copy()

    # ==========================================
    # COMBINE TEAM MEMBERS
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
            and str(member).strip() not in ["", "-", "nan"]
        ]

        return " • ".join(members) if members else "-"


    display_df["Team"] = display_df.apply(
        combine_members,
        axis=1
    )


    # ==========================================
    # COUNTDOWN DISPLAY
    # ==========================================

    def get_countdown(row):

        days = row["Days Left"]
        status = row["Status"]

        if status == "Completed":
            return "Completed"

        elif status == "Today":
            return "Today"

        elif days == 1:
            return "1 day"

        else:
            return f"{days} days"


    display_df["Countdown"] = display_df.apply(
        get_countdown,
        axis=1
    )


    # ==========================================
    # SELECT COLUMNS
    # ==========================================

    display_df = display_df[
        [
            "BATCH",
            "STORE",
            "AST Date",
            "AST Day",
            "Coord",
            "Team",
            "Status",
            "Countdown"
        ]
    ].copy()


    # ==========================================
    # RENAME COLUMNS
    # ==========================================

    display_df = display_df.rename(
        columns={
            "BATCH": "Batch",
            "STORE": "Store",
            "AST Date": "AST Date",
            "AST Day": "Day",
            "Coord": "Coordinator"
        }
    )


    # ==========================================
    # SORT
    # ==========================================

    display_df = display_df.sort_values(
        by=["AST Date", "Batch", "Store"]
    )


    # ==========================================
    # HTML ESCAPE
    # ==========================================

    from html import escape


    # ==========================================
    # STATUS STYLE
    # ==========================================

    def status_badge(status):

        if status == "Today":

            return """
            <span style="
                display:inline-block;
                background:#D71920;
                color:#ffffff;
                padding:5px 11px;
                border-radius:999px;
                font-size:11px;
                font-weight:700;
            ">
                Today
            </span>
            """

        elif status == "Soon":

            return """
            <span style="
                display:inline-block;
                background:#fff0f1;
                color:#C51C27;
                border:1px solid #f3c8cc;
                padding:5px 11px;
                border-radius:999px;
                font-size:11px;
                font-weight:700;
            ">
                Soon
            </span>
            """

        elif status == "Completed":

            return """
            <span style="
                display:inline-block;
                background:#f1f1f1;
                color:#666666;
                padding:5px 11px;
                border-radius:999px;
                font-size:11px;
                font-weight:700;
            ">
                Completed
            </span>
            """

        else:

            return """
            <span style="
                display:inline-block;
                background:#fff8f8;
                color:#8f1d2d;
                border:1px solid #f0dfe1;
                padding:5px 11px;
                border-radius:999px;
                font-size:11px;
                font-weight:700;
            ">
                Upcoming
            </span>
            """


    # ==========================================
    # BUILD TABLE ROWS
    # ==========================================

    rows_html = ""

    for _, row in display_df.iterrows():

        status = str(row["Status"])

        ast_date = row["AST Date"]

        if pd.notna(ast_date):
            formatted_date = pd.Timestamp(
                ast_date
            ).strftime("%d %b %Y")
        else:
            formatted_date = "-"

        rows_html += f"""
        <tr>

            <td>
                <span style="
                    background:#fff1f2;
                    color:#a41728;
                    padding:5px 9px;
                    border-radius:8px;
                    font-size:12px;
                    font-weight:700;
                ">
                    {escape(str(row["Batch"]))}
                </span>
            </td>


            <td>
                <div style="
                    font-weight:700;
                    color:#2c2c2c;
                ">
                    {escape(str(row["Store"]))}
                </div>
            </td>


            <td>
                <div style="
                    font-weight:600;
                    color:#333333;
                ">
                    {formatted_date}
                </div>
            </td>


            <td>
                <span style="
                    color:#777777;
                    font-size:12px;
                ">
                    {escape(str(row["Day"]))}
                </span>
            </td>


            <td>
                <span style="
                    color:#444444;
                    font-weight:600;
                ">
                    {escape(str(row["Coordinator"]))}
                </span>
            </td>


            <td>
                <span style="
                    color:#666666;
                    font-size:12px;
                ">
                    {escape(str(row["Team"]))}
                </span>
            </td>


            <td>
                {status_badge(status)}
            </td>


            <td>
                <span style="
                    font-weight:700;
                    color:#8f1d2d;
                    font-size:12px;
                ">
                    {escape(str(row["Countdown"]))}
                </span>
            </td>

        </tr>
        """


    # ==========================================
    # FINAL HTML TABLE
    # ==========================================

    table_html = f"""
    <div style="
        background:#ffffff;
        border:1px solid #eeeeee;
        border-radius:16px;
        overflow:hidden;
        box-shadow:0 6px 20px rgba(0,0,0,0.05);
    ">

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
                ANNUAL STOCK TAKE SCHEDULE
            </div>

            <div style="
                color:#ffe8e9;
                font-size:11px;
                font-weight:600;
            ">
                {len(display_df)} schedule
            </div>

        </div>


        <div style="
            max-height:520px;
            overflow:auto;
        ">

            <table style="
                width:100%;
                border-collapse:collapse;
                font-family:Arial,sans-serif;
                font-size:13px;
            ">

                <thead>

                    <tr style="
                        background:#fff5f5;
                        border-bottom:1px solid #f0d6d9;
                    ">

                        <th style="
                            padding:13px 16px;
                            text-align:left;
                            color:#9b1c31;
                            font-size:11px;
                            font-weight:800;
                            letter-spacing:0.6px;
                            position:sticky;
                            top:0;
                            background:#fff5f5;
                            z-index:2;
                        ">
                            BATCH
                        </th>

                        <th style="
                            padding:13px 16px;
                            text-align:left;
                            color:#9b1c31;
                            font-size:11px;
                            font-weight:800;
                            letter-spacing:0.6px;
                            position:sticky;
                            top:0;
                            background:#fff5f5;
                            z-index:2;
                        ">
                            STORE
                        </th>

                        <th style="
                            padding:13px 16px;
                            text-align:left;
                            color:#9b1c31;
                            font-size:11px;
                            font-weight:800;
                            letter-spacing:0.6px;
                            position:sticky;
                            top:0;
                            background:#fff5f5;
                            z-index:2;
                        ">
                            AST DATE
                        </th>

                        <th style="
                            padding:13px 16px;
                            text-align:left;
                            color:#9b1c31;
                            font-size:11px;
                            font-weight:800;
                            letter-spacing:0.6px;
                            position:sticky;
                            top:0;
                            background:#fff5f5;
                            z-index:2;
                        ">
                            DAY
                        </th>

                        <th style="
                            padding:13px 16px;
                            text-align:left;
                            color:#9b1c31;
                            font-size:11px;
                            font-weight:800;
                            letter-spacing:0.6px;
                            position:sticky;
                            top:0;
                            background:#fff5f5;
                            z-index:2;
                        ">
                            COORDINATOR
                        </th>

                        <th style="
                            padding:13px 16px;
                            text-align:left;
                            color:#9b1c31;
                            font-size:11px;
                            font-weight:800;
                            letter-spacing:0.6px;
                            position:sticky;
                            top:0;
                            background:#fff5f5;
                            z-index:2;
                        ">
                            TEAM
                        </th>

                        <th style="
                            padding:13px 16px;
                            text-align:left;
                            color:#9b1c31;
                            font-size:11px;
                            font-weight:800;
                            letter-spacing:0.6px;
                            position:sticky;
                            top:0;
                            background:#fff5f5;
                            z-index:2;
                        ">
                            STATUS
                        </th>

                        <th style="
                            padding:13px 16px;
                            text-align:left;
                            color:#9b1c31;
                            font-size:11px;
                            font-weight:800;
                            letter-spacing:0.6px;
                            position:sticky;
                            top:0;
                            background:#fff5f5;
                            z-index:2;
                        ">
                            COUNTDOWN
                        </th>

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

        table td {{
            padding:12px 16px;
            vertical-align:middle;
        }}

    </style>
    """

    st.html(table_html)