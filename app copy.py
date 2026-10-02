import streamlit as st
import pandas as pd
from datetime import date


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Annual Stock Take",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# 2. HEADER
# ==========================================

st.title("📦 Annual Stock Take Dashboard")
st.caption("Monitoring stock variance and inventory reconciliation")
st.divider()


# ==========================================
# 3. DUMMY DATA
# ==========================================

data = {
    "Store": [
        "Pakuwon", "Pakuwon", "Pakuwon",
        "Solo Baru", "Solo Baru", "Solo Baru",
        "Bintaro", "Bintaro", "Bintaro"
    ],

    "Item": [
        "Apple", "Orange", "Milk",
        "Bread", "Chicken", "Rice",
        "Coffee", "Sugar", "Egg"
    ],

    "System Stock": [
        100, 50, 30,
        40, 80, 120,
        60, 90, 70
    ],

    "Physical Stock": [
        95, 55, 30,
        37, 75, 125,
        58, 95, 68
    ]
}

df = pd.DataFrame(data)

# Dummy jadwal Annual Stock Take
ast_schedule = {
    "Store": [
        "Pakuwon",
        "Solo Baru",
        "Bintaro"
    ],
    "AST Date": [
        date(2026, 10, 10),
        date(2026, 10, 18),
        date(2026, 10, 25)
    ],
    "Coordinator": [
        "Andi",
        "Budi",
        "Citra"
    ],
    "Member": [
        8,
        6,
        10
    ]
}

schedule_df = pd.DataFrame(ast_schedule)

# ==========================================
# 4. DATA PROCESSING
# ==========================================

df["Variance"] = (
    df["Physical Stock"]
    - df["System Stock"]
)


# ==========================================
# 5. SIDEBAR
# ==========================================

store_list = ["All Store"] + list(
    df["Store"].unique()
)

item_list = ["All Item"] + list(
    df["Item"].unique()
)


with st.sidebar:

    st.title("⚙️ Dashboard Control")

    st.caption(
        "Gunakan filter untuk menyesuaikan data."
    )

    st.divider()

    selected_store = st.selectbox(
        "Store",
        store_list
    )

    selected_item = st.selectbox(
        "Item",
        item_list
    )

    variance_filter = st.selectbox(
        "Variance Status",
        [
            "All",
            "Negative",
            "Zero",
            "Positive"
        ]
    )

    st.divider()

    sort_column = st.selectbox(
        "Sort By",
        [
            "Item",
            "System Stock",
            "Physical Stock",
            "Variance"
        ]
    )

    sort_order = st.selectbox(
        "Sort Order",
        [
            "Ascending",
            "Descending"
        ]
    )


# ==========================================
# 6. FILTERING
# ==========================================

filtered_df = df.copy()


# Filter Store
if selected_store != "All Store":

    filtered_df = filtered_df[
        filtered_df["Store"] == selected_store
    ]


# Filter Item
if selected_item != "All Item":

    filtered_df = filtered_df[
        filtered_df["Item"] == selected_item
    ]


# Filter Variance
if variance_filter == "Negative":

    filtered_df = filtered_df[
        filtered_df["Variance"] < 0
    ]

elif variance_filter == "Zero":

    filtered_df = filtered_df[
        filtered_df["Variance"] == 0
    ]

elif variance_filter == "Positive":

    filtered_df = filtered_df[
        filtered_df["Variance"] > 0
    ]


# ==========================================
# 7. SORTING
# ==========================================

ascending_order = (
    sort_order == "Ascending"
)

filtered_df = filtered_df.sort_values(
    by=sort_column,
    ascending=ascending_order
)

# ==========================================
# 7B. NEXT AST CALCULATION
# ==========================================

today = date.today()

if selected_store == "All Store":
    selected_schedule = schedule_df.copy()
else:
    selected_schedule = schedule_df[
        schedule_df["Store"] == selected_store
    ].copy()

upcoming_schedule = selected_schedule[
    selected_schedule["AST Date"] >= today
]

upcoming_schedule = upcoming_schedule.sort_values(
    by="AST Date"
)

if not upcoming_schedule.empty:

    next_ast = upcoming_schedule.iloc[0]

    next_store = next_ast["Store"]
    next_date = next_ast["AST Date"]
    next_coordinator = next_ast["Coordinator"]
    next_member = next_ast["Member"]

    days_left = (next_date - today).days

# ==========================================
# NEXT ANNUAL STOCK TAKE
# ==========================================

st.subheader("Next Annual Stock Take")

if not upcoming_schedule.empty:

    with st.container(border=True):

        col_ast1, col_ast2, col_ast3, col_ast4 = st.columns(4)

        with col_ast1:
            st.caption("Store")
            st.subheader(next_store)

        with col_ast2:
            st.caption("AST Date")
            st.subheader(
                next_date.strftime("%d %B %Y")
            )

        with col_ast3:
            st.caption("Countdown")
            st.subheader(
                f"{days_left} Days"
            )

        with col_ast4:
            st.caption("Coordinator")
            st.subheader(next_coordinator)

        st.caption(
            f"Total member: {next_member}"
        )

else:

    st.info(
        "Tidak ada jadwal Annual Stock Take berikutnya."
    )

st.divider()

# ==========================================
# 8. KPI CALCULATION
# ==========================================

total_item = len(filtered_df)

total_system_stock = (
    filtered_df["System Stock"].sum()
)

total_physical_stock = (
    filtered_df["Physical Stock"].sum()
)

total_variance = (
    filtered_df["Variance"].sum()
)


negative_count = len(
    filtered_df[
        filtered_df["Variance"] < 0
    ]
)

zero_count = len(
    filtered_df[
        filtered_df["Variance"] == 0
    ]
)

positive_count = len(
    filtered_df[
        filtered_df["Variance"] > 0
    ]
)


# ==========================================
# 9. DASHBOARD OVERVIEW
# ==========================================

st.subheader("Inventory Overview")


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Items",
        total_item
    )

with col2:
    st.metric(
        "System Stock",
        total_system_stock
    )

with col3:
    st.metric(
        "Physical Stock",
        total_physical_stock
    )

with col4:
    st.metric(
        "Total Variance",
        total_variance
    )


st.write("")


status1, status2, status3 = st.columns(3)

with status1:
    st.metric(
        "Negative Variance",
        negative_count
    )

with status2:
    st.metric(
        "Balanced",
        zero_count
    )

with status3:
    st.metric(
        "Positive Variance",
        positive_count
    )


st.divider()


# ==========================================
# 10. CHART
# ==========================================

with st.container(border=True):

    st.subheader(
        "System Stock vs Physical Stock"
    )

    if filtered_df.empty:

        st.warning(
            "Tidak ada data yang sesuai dengan filter."
        )

    else:

        chart_data = (
            filtered_df
            .set_index("Item")[
                [
                    "System Stock",
                    "Physical Stock"
                ]
            ]
        )

        st.bar_chart(chart_data)


# ==========================================
# 11. DATA TABLE
# ==========================================

with st.container(border=True):

    st.subheader("Stock Take Detail")

    st.dataframe(
        filtered_df,
        hide_index=True
    )