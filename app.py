import streamlit as st
import pandas as pd
import json
from sql_connection import get_connection
from queries import queries  # << Import your queries dictionary

# ------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------
st.set_page_config(page_title="Harvard Artifacts", layout="wide")
st.markdown("<h1 style='text-align: center;'>🎨 Harvard Artifact Explorer</h1>", unsafe_allow_html=True)

# ------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------
if "data" not in st.session_state:
    st.session_state.data = None

if "query_result" not in st.session_state:
    st.session_state.query_result = None

# ------------------------------------------------------
# DATABASE CONNECTION
# ------------------------------------------------------
conn = get_connection()
cursor = conn.cursor()

# ------------------------------------------------------
# 1️⃣ CLASSIFICATION SELECTION
# ------------------------------------------------------
classification = st.selectbox(
    "Select a Classification",
    ["Paintings", "Sculpture", "Prints"]
)

# ------------------------------------------------------
# 2️⃣ COLLECT DATA (JSON)
# ------------------------------------------------------
def collect_data(classification):
    try:
        with open(f"{classification}.json", "r") as f:
            raw = json.load(f)

        df = pd.DataFrame(raw).head(2500)
        st.session_state.data = df
        st.success(f"{len(df)} records collected successfully!")
    except Exception as e:
        st.error(f"❌ File not found / API failed: {e}")

if st.button("📥 Collect Data"):
    collect_data(classification)

# ------------------------------------------------------
# 3️⃣ JSON PREVIEW (first 10)
# ------------------------------------------------------
if st.session_state.data is not None:

    col1, col2, col3 = st.columns(3)

    # -----------------------
    # METADATA
    # -----------------------
    with col1:
        st.write("### 🧾 METADATA")
        metadata_cols = ["id", "title", "culture", "period", "century"]
        available_meta = [c for c in metadata_cols if c in st.session_state.data.columns]
        with st.expander("Show Metadata (first 10)"):
            metadata_list = [
                {col: row[col] for col in available_meta} 
                for _, row in st.session_state.data[available_meta].head(10).iterrows()
            ]
            st.json(metadata_list)

    # -----------------------
    # MEDIA
    # -----------------------
    with col2:
        st.write("### 🖼 MEDIA")
        media_cols = ["id", "imagecount", "mediacount", "colorcount"]
        available_media = [c for c in media_cols if c in st.session_state.data.columns]
        with st.expander("Show Media (first 10)"):
            if len(available_media) > 1:
                media_list = [
                    {col: row[col] for col in available_media} 
                    for _, row in st.session_state.data[available_media].head(10).iterrows()
                ]
                st.json(media_list)
            else:
                st.warning("⚠ No media fields found in JSON")

    # -----------------------
    # COLORS
    # -----------------------
    with col3:
        st.write("### 🎨 COLORS")
        with st.expander("Show Colors (first 10)"):
            if "colors" in st.session_state.data.columns:
                colors_list = []
                for _, row in st.session_state.data[["id", "colors"]].head(10).iterrows():
                    if isinstance(row["colors"], list) and row["colors"]:
                        colors_list.append({
                            "id": row["id"],
                            "colors": row["colors"][:10]
                        })
                    else:
                        colors_list.append({"id": row["id"], "colors": []})
                st.json(colors_list)
            else:
                st.warning("⚠ No color field found in JSON")

st.write("---")

# ------------------------------------------------------
# 4️⃣ INSERT INTO SQL & SHOW TABLES
# ------------------------------------------------------
def insert_sql(df):
    inserted_meta = 0
    updated_meta = 0

    # -------- Metadata Table --------
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO artifact_metadata(id, title, culture)
            VALUES (%s,%s,%s)
            ON DUPLICATE KEY UPDATE
            title = VALUES(title),
            culture = VALUES(culture)
        """, (row["id"], row["title"], row["culture"]))
        if cursor.rowcount == 1:
            inserted_meta += 1
        elif cursor.rowcount == 2:
            updated_meta += 1

    # -------- Media Table --------
    inserted_media = 0
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO artifact_media(objectid, imagecount, mediacount, colorcount)
            VALUES (%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
            imagecount=VALUES(imagecount),
            mediacount=VALUES(mediacount),
            colorcount=VALUES(colorcount)
        """, (
            row["id"],
            row.get("imagecount", 0),
            row.get("mediacount", 0),
            row.get("colorcount", 0)
        ))
        if cursor.rowcount > 0:
            inserted_media += 1

    # -------- Colors Table --------
    inserted_colors = 0
    if "colors" in df.columns:
        for _, row in df.iterrows():
            if isinstance(row["colors"], list) and row["colors"]:
                for color in row["colors"]:
                    cursor.execute("""
                        INSERT INTO artifact_colors(objectid, color, spectrum, hue, percent, css3)
                        VALUES (%s,%s,%s,%s,%s,%s)
                        ON DUPLICATE KEY UPDATE
                        color=VALUES(color),
                        spectrum=VALUES(spectrum),
                        hue=VALUES(hue),
                        percent=VALUES(percent),
                        css3=VALUES(css3)
                    """, (
                        row["id"],
                        color.get("color"),
                        color.get("spectrum"),
                        color.get("hue"),
                        color.get("percent"),
                        color.get("css3")
                    ))
                    inserted_colors += 1

    conn.commit()
    st.success(f"Metadata: Inserted {inserted_meta}, Updated {updated_meta} | Media: {inserted_media} | Colors: {inserted_colors}")

    # Clear JSON after insert
    st.session_state.data = None

    # -------- Show Scrollable Tables Side by Side --------
    st.subheader("📂 SQL Table Preview")
    col_meta, col_media, col_colors = st.columns(3)

    # Metadata
    with col_meta:
        st.write("### 🧾 Metadata")
        cursor.execute("SELECT * FROM artifact_metadata LIMIT 50;")
        df_meta = pd.DataFrame(cursor.fetchall(), columns=[c[0] for c in cursor.description])
        st.dataframe(df_meta, use_container_width=True, height=250)

    # Media
    with col_media:
        st.write("### 🖼 Media")
        cursor.execute("SELECT * FROM artifact_media LIMIT 50;")
        df_media = pd.DataFrame(cursor.fetchall(), columns=[c[0] for c in cursor.description])
        st.dataframe(df_media, use_container_width=True, height=250)

    # Colors
    with col_colors:
        st.write("### 🎨 Colors")
        cursor.execute("SELECT * FROM artifact_colors LIMIT 50;")
        df_colors = pd.DataFrame(cursor.fetchall(), columns=[c[0] for c in cursor.description])
        st.dataframe(df_colors, use_container_width=True, height=250)

if st.button("🚀 Insert into SQL"):
    if st.session_state.data is not None:
        insert_sql(st.session_state.data)
    else:
        st.warning("⚠ Collect data first")

st.write("---")

# ------------------------------------------------------
# 5️⃣ QUERY SECTION
# ------------------------------------------------------
st.subheader("📊 SQL Query & Visualization")

query_choice = st.selectbox("Select a Query", list(queries.keys()))

if st.button("🧾 Run Query"):
    try:
        # If query needs artifact ID input
        if query_choice == "All colors used for a given artifact ID":
            artifact_id = st.text_input("Enter artifact ID:")
            if artifact_id:
                cursor.execute(queries[query_choice], (artifact_id,))
            else:
                st.warning("Enter an artifact ID to run this query.")
                st.stop()
        else:
            cursor.execute(queries[query_choice])

        rows = cursor.fetchall()
        result_df = pd.DataFrame(rows, columns=[c[0] for c in cursor.description])
        st.dataframe(result_df, use_container_width=True, height=300)
    except Exception as e:
        st.error(f"Error executing query: {e}")

# ------------------------------------------------------
# CLOSE CONNECTION
# ------------------------------------------------------
# conn.close()  # Keep connection open until app ends
