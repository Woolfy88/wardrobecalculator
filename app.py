import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

st.set_page_config(page_title="Wardrobe Multi-Opening Calculator", layout="wide")

st.title("Wardrobe Door & Liner Calculator – Multi Opening")

st.caption(
    "Max door height 2431mm for made-to-measure doors. Per-opening dropdown options: 108mm, 90mm, 50mm, "
    "0mm (no dropdown), or a bespoke auto-calculated dropdown. Bottom liners are two 18mm boards "
    "(36mm total). There is an additional 54mm trackset tolerance that must be allowed within the "
    "opening height. In made-to-measure mode, side liners are fixed at 18mm each. In fixed 2223mm door mode, "
    "you choose door width (610 / 762 / 914mm) and number of doors, and the system calculates the "
    "side liner thickness (build-out per side) to suit overlap tolerances (2 doors = 75mm, "
    "3+ doors = 150mm). One row = one opening. All dimensions in mm."
)

# -----------------------------
# SYSTEM CONSTANTS
# -----------------------------
BOTTOM_LINER_THICKNESS = 36       # 2 x 18mm
SIDE_LINER_THICKNESS = 18         # default side liner thickness (mm) for made-to-measure mode
TRACKSET_TOLERANCE = 54           # extra allowance for trackset/hardware (mm)
MAX_DOOR_HEIGHT = 2431            # max made-to-measure door height
MAX_DROPDOWN_LIMIT = 400          # absolute max dropdown allowed

# Fixed door system
FIXED_DOOR_HEIGHT = 2223
FIXED_DOOR_WIDTH_OPTIONS = [610, 762, 914]   # mm

# Overlap tolerances for fixed systems (total extra span vs net width)
OVERLAP_TOLERANCES = {
    2: 75,
    3: 150,
    4: 150,
}
DEFAULT_FIXED_OVERLAP_TOLERANCE = 150  # used for 5, 6, etc.

# Per-opening top liner options (for made-to-measure mode, fixed sizes)
TOP_LINER_OPTIONS = {
    "108mm Dropdown": 108,
    "90mm Dropdown": 90,
    "50mm Dropdown": 50,
    "No dropdown (0mm)": 0,
}

# Label for bespoke option
BESPOKE_DROPDOWN_LABEL = "Bespoke dropdown (auto)"

# Made-to-measure door overlap (per meeting)
CUSTOM_DOOR_OVERLAP_MM = 25

# Door system options
DOOR_SYSTEM_OPTIONS = [
    "Made to measure doors",
    "Fixed 2223mm doors",
]


# ============================================================
# DIAGRAM DRAWING FUNCTION
# ============================================================
def draw_wardrobe_diagram(
    opening_width_mm: float,
    opening_height_mm: float,
    bottom_thk_mm: float,
    side_thk_mm: float,
    dropdown_height_mm: float,
    door_height_mm: float,
    num_doors: int,
    door_width_mm: float,
    dropdown_label: str = "",
):
    """Draw wardrobe front elevation with instructions and dimension arrows."""
    opening_width_mm = max(opening_width_mm, 1)
    opening_height_mm = max(opening_height_mm, 1)
    num_doors = max(int(num_doors), 1)
    side_thk_mm = max(side_thk_mm, 0)

    # Normalised relative coordinates (0–1 space)
    side_rel = side_thk_mm / opening_width_mm
    bottom_rel = bottom_thk_mm / opening_height_mm
    dropdown_rel = dropdown_height_mm / opening_height_mm if dropdown_height_mm > 0 else 0
    door_h_rel = door_height_mm / opening_height_mm if door_height_mm > 0 else 0

    fig, ax = plt.subplots(figsize=(4, 7))
    ax.set_xlim(-0.45, 1.45)
    ax.set_ylim(-0.25, 1.20)  # extended a bit to fit notes
    ax.set_aspect("equal")
    ax.axis("off")

    # -----------------------------
    # MAIN SHAPES
    # -----------------------------
    # Opening outline
    ax.add_patch(Rectangle((0, 0), 1, 1, fill=False, linewidth=2))

    # Side liners (left/right)
    ax.add_patch(
        Rectangle(
            (0, bottom_rel),
            side_rel,
            1 - bottom_rel,
            fill=True,
            alpha=0.25,
        )
    )
    ax.add_patch(
        Rectangle(
            (1 - side_rel, bottom_rel),
            side_rel,
            1 - bottom_rel,
            fill=True,
            alpha=0.25,
        )
    )

    # Bottom liner
    ax.add_patch(
        Rectangle(
            (side_rel, 0),
            1 - 2 * side_rel,
            bottom_rel,
            fill=True,
            alpha=0.25,
        )
    )

    # Dropdown (top liner)
    if dropdown_rel > 0:
        ax.add_patch(
            Rectangle(
                (side_rel, 1 - dropdown_rel),
                1 - 2 * side_rel,
                dropdown_rel,
                fill=True,
                alpha=0.25,
            )
        )

        # TOP LINER FIXING NOTE (with arrow)
        ax.annotate(
            "Drop-down to be fixed using\n"
            "metal stretcher brackets.\n"
            "2x into side liners and\n"
            "brackets every 600mm.",
            xy=(0.5, 1 - dropdown_rel / 2),       # target in dropdown
            xytext=(1.28, 1 - dropdown_rel / 2),  # text box position to the right
            fontsize=8,
            ha="left",
            va="center",
            bbox=dict(boxstyle="round,pad=0.45", fc="white", ec="black", lw=1),
            arrowprops=dict(arrowstyle="->", lw=1.3),
        )

    # -----------------------------
    # DOORS (dashed)
    # -----------------------------
    door_width_mm = max(door_width_mm, 0)
    door_width_rel = door_width_mm / opening_width_mm if opening_width_mm > 0 else 0

    # Clamp so doors don't visually extend beyond opening
    total_doors_span = num_doors * door_width_rel
    available_span = 1 - 2 * side_rel
    if total_doors_span > available_span and total_doors_span > 0:
        scale = available_span / total_doors_span
        door_width_rel *= scale

    x_start = side_rel
    for _ in range(num_doors):
        ax.add_patch(
            Rectangle(
                (x_start, bottom_rel),
                door_width_rel,
                door_h_rel,
                fill=False,
                linestyle="--",
                linewidth=1,
            )
        )
        x_start += door_width_rel

    # -----------------------------
    # SIDE LINER FIXING NOTE (LEFT) – NO ARROW
    # -----------------------------
    ax.annotate(
        "Side liners fixings -\n"
        "200mm in from either end\n"
        "and then two in the middle\n"
        "of the liner (equally spaced),\n"
        "so 4x fixings in total.",
        xy=(side_rel / 2, 0.5),
        xytext=(-0.34, 0.72),
        fontsize=8,
        ha="right",
        va="center",
        bbox=dict(boxstyle="round,pad=0.45", fc="white", ec="black", lw=1),
    )

    # -----------------------------
    # BOTTOM LINER / SUB-CILL FIXING NOTE – NO ARROW
    # -----------------------------
    ax.annotate(
        "Sub-cill to floor - fixing every 500mm\n"
        "Sub-cill to carpet - fixing every 200mm",
        xy=(0.5, bottom_rel / 2),
        xytext=(0.5, -0.20),
        fontsize=8,
        ha="center",
        va="top",
        bbox=dict(boxstyle="round,pad=0.45", fc="white", ec="black", lw=1),
    )

    # -----------------------------
    # BOTTOM TRACK FIXING NOTE (with arrow)
    # -----------------------------
    ax.annotate(
        "Bottom track fixing - 50-80mm in from ends\n"
        "and then every 800mm of track span.",
        xy=(0.5, bottom_rel + 0.02),
        xytext=(1.28, bottom_rel + 0.18),
        fontsize=8,
        ha="left",
        va="center",
        bbox=dict(boxstyle="round,pad=0.45", fc="white", ec="black", lw=1),
        arrowprops=dict(arrowstyle="->", lw=1.3),
    )

    # -----------------------------
    # TOP LABEL (Dropdown / Top Liner Label)
    # -----------------------------
    if dropdown_label:
        ax.text(
            0.5,
            1.05,  # slightly above the opening outline
            dropdown_label,
            fontsize=10,
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    # -----------------------------
    # DIMENSION ARROWS + LABELS (WITH "mm")
    # -----------------------------

    # HEIGHT arrow (vertical, left)
    ax.annotate(
        "",
        xy=(-0.20, 0),
        xytext=(-0.20, 1),
        arrowprops=dict(arrowstyle="<->", lw=1),
    )
    # Height label next to arrow (offset left)
    ax.text(
        -0.27,
        0.5,
        f"{int(opening_height_mm)}mm",
        rotation=90,
        fontsize=9,
        ha="center",
        va="center",
    )

    # WIDTH arrow (horizontal, bottom)
    ax.annotate(
        "",
        xy=(0, -0.06),
        xytext=(1, -0.06),
        arrowprops=dict(arrowstyle="<->", lw=1),
    )
    # Width label below the arrow
    ax.text(
        0.5,
        -0.10,
        f"{int(opening_width_mm)}mm",
        fontsize=9,
        ha="center",
        va="top",
    )

    return fig


# ============================================================
# DEFAULT DATA (single row)
# ============================================================
DEFAULT_DATA = pd.DataFrame([
    {
        "Job": "Job 1",
        "Opening": "Wardrobe A",
        "Width_mm": 2200,
        "Height_mm": 2600,
        "Doors": 3,
        "Door_System": "Made to measure doors",
        "Top_Liner_Option": "108mm Dropdown",
        "Fixed_Door_Width_mm": 762,   # ignored in made-to-measure mode
    },
])

if "openings_df" not in st.session_state:
    st.session_state["openings_df"] = DEFAULT_DATA.copy()

# ============================================================
# SIDEBAR CONSTANTS
# ============================================================
st.sidebar.subheader("System constants")
st.sidebar.write(f"Bottom liners total: **{BOTTOM_LINER_THICKNESS} mm**")
st.sidebar.write(f"Trackset tolerance: **{TRACKSET_TOLERANCE} mm** (headroom for trackset & framework)")
st.sidebar.write(f"Side liners default: **{SIDE_LINER_THICKNESS} mm** each (made-to-measure mode)")
st.sidebar.write("In fixed 2223mm mode, side liner thickness varies to suit door span + overlap tolerance.")
st.sidebar.write(f"Max made-to-measure door height: **{MAX_DOOR_HEIGHT} mm**")
st.sidebar.write(f"Max dropdown allowed: **{MAX_DROPDOWN_LIMIT} mm**")
st.sidebar.write("Top liner options for made-to-measure doors: 108mm, 90mm, 50mm, 0mm, or bespoke auto-calculated.")
st.sidebar.write("Fixed door system: 2223mm high, widths 610 / 762 / 914mm (user selects).")
st.sidebar.write("Fixed system overlap tolerances: 2 doors = 75mm, 3+ doors = 150mm.")


# ============================================================
# TABLE EDITOR
# ============================================================
st.subheader("1. Enter openings")

top_liner_choices = list(TOP_LINER_OPTIONS.keys()) + [BESPOKE_DROPDOWN_LABEL]

edited_df = st.data_editor(
    st.session_state["openings_df"],
    num_rows="dynamic",
    use_container_width=True,
    key="openings_table",
    column_config={
        "Width_mm": st.column_config.NumberColumn(
            "Width (mm)", min_value=300, step=10
        ),
        "Height_mm": st.column_config.NumberColumn(
            "Height (mm)", min_value=300, step=10
        ),
        "Doors": st.column_config.NumberColumn(
            "Number of doors", min_value=1, max_value=10, step=1
        ),
        "Door_System": st.column_config.SelectboxColumn(
            "Door system",
            options=DOOR_SYSTEM_OPTIONS,
            default="Made to measure doors",
        ),
        "Top_Liner_Option": st.column_config.SelectboxColumn(
            "Top liner option (made-to-measure only)",
            options=top_liner_choices,
            default="108mm Dropdown",
        ),
        "Fixed_Door_Width_mm": st.column_config.SelectboxColumn(
            "Fixed door width (mm) (fixed mode)",
            options=FIXED_DOOR_WIDTH_OPTIONS,
            default=762,
        ),
    },
)

st.session_state["openings_df"] = edited_df


# ============================================================
# CALCULATION FUNCTION
# ============================================================
def calculate_for_row(row: pd.Series) -> pd.Series:
    # Basic validation / clamping
    width = max(float(row["Width_mm"]), 1)
    height = max(float(row["Height_mm"]), 1)
    doors = max(int(row["Doors"]), 1)

    door_system = row.get("Door_System", "Made to measure doors")

    if door_system == "Fixed 2223mm doors":
        # -------------------------
        # FIXED DOOR SYSTEM MODE (user-selected width, user-selected doors, variable side liners)
        # -------------------------
        door_height = FIXED_DOOR_HEIGHT

        # User-selected fixed door width
        door_width = float(row.get("Fixed_Door_Width_mm", 762))
        if door_width not in FIXED_DOOR_WIDTH_OPTIONS:
            door_width = 762  # fallback

        # Top liner (dropdown) needed to hit opening height:
        # opening_height = bottom_liner + trackset_tolerance + door_height + dropdown
        dropdown_h_raw = height - BOTTOM_LINER_THICKNESS - TRACKSET_TOLERANCE - door_height

        height_status = "OK"

        if dropdown_h_raw < 0:
            dropdown_h = 0
            height_status = (
                "Opening too small for 2223mm door plus 36mm bottom liner and "
                f"{TRACKSET_TOLERANCE}mm trackset tolerance."
            )
        elif dropdown_h_raw > MAX_DROPDOWN_LIMIT:
            dropdown_h = MAX_DROPDOWN_LIMIT
            height_status = (
                f"Dropdown needed is {int(dropdown_h_raw)}mm – exceeds "
                f"max allowed {MAX_DROPDOWN_LIMIT}mm (including {TRACKSET_TOLERANCE}mm trackset tolerance)."
            )
        else:
            dropdown_h = dropdown_h_raw

        # Overlap tolerance based on number of doors
        tol = OVERLAP_TOLERANCES.get(doors, DEFAULT_FIXED_OVERLAP_TOLERANCE)

        # door_span - net_width = tol
        # net_width = width - 2 * side_t
        # => side_t = (width - door_span + tol) / 2
        door_span = doors * door_width
        side_thk_raw = (width - door_span + tol) / 2

        # Side thickness can't be negative
        if side_thk_raw < 0:
            side_thk = 0.0
        else:
            side_thk = side_thk_raw

        net_width = width - 2 * side_thk
        span_diff = door_span - (net_width + tol)  # if side_thk capped, this may not be 0

        build_out_per_side = max(side_thk - SIDE_LINER_THICKNESS, 0)

        issue_flag = "✅ OK" if height_status == "OK" else "🔴 Check height"

        return pd.Series({
            "Door_Height_mm": int(round(door_height)),
            "Door_Width_mm": int(round(door_width)),
            "Doors_Used": int(doors),
            "Dropdown_Height_mm": int(round(dropdown_h)),
            "Recommended_Dropdown_Height_mm": None,  # not applicable in fixed mode
            "Side_Liner_Thickness_mm": round(side_thk, 1),
            "Required_Buildout_Per_Side_mm": round(build_out_per_side, 1),
            "Net_Width_mm": int(round(net_width)),
            "Door_Span_mm": int(round(door_span)),
            "Overlap_Tolerance_mm": int(round(tol)),  # fixed system total tolerance
            "Span_Diff_mm": round(span_diff, 1),      # door_span - (net + tolerance)
            "Bottom_Liner_Length_mm": int(round(net_width)),
            "Side_Liner_Length_mm": int(round(height)),
            "Dropdown_Length_mm": int(round(net_width)),
            "Trackset_Tolerance_mm": int(TRACKSET_TOLERANCE),
            "Height_Status": height_status,
            "Issue": issue_flag,
        })

    else:
        # -------------------------
        # MADE TO MEASURE MODE (side liners fixed at 18mm)
        # -------------------------
        side_liner_thk = SIDE_LINER_THICKNESS
        net_width = width - 2 * side_liner_thk

        option = row.get("Top_Liner_Option", "108mm Dropdown")

        # Base usable height after bottom liners and trackset, BEFORE dropdown
        base_usable_height = height - BOTTOM_LINER_THICKNESS - TRACKSET_TOLERANCE

        # Handle bespoke vs fixed dropdown options
        if option == BESPOKE_DROPDOWN_LABEL:
            # Ideal dropdown to keep door height <= MAX_DOOR_HEIGHT and fill the opening:
            # ideal door height = min(MAX_DOOR_HEIGHT, base_usable_height)
            # ideal dropdown = base_usable_height - ideal door height
            ideal_door_height = min(MAX_DOOR_HEIGHT, base_usable_height)
            ideal_dropdown = max(base_usable_height - ideal_door_height, 0)

            # Actual dropdown limited by system max:
            dropdown_h = min(ideal_dropdown, MAX_DROPDOWN_LIMIT)

            raw_door_height = base_usable_height - dropdown_h
            raw_door_height = max(raw_door_height, 0)
            final_door_h = min(raw_door_height, MAX_DOOR_HEIGHT)

            if ideal_dropdown <= MAX_DROPDOWN_LIMIT and final_door_h <= MAX_DOOR_HEIGHT:
                height_status = "OK (bespoke dropdown auto-calculated for fit)"
            elif ideal_dropdown > MAX_DROPDOWN_LIMIT:
                height_status = (
                    f"Too tall for perfect fit with max {MAX_DROPDOWN_LIMIT}mm bespoke dropdown "
                    f"(ideal dropdown would be about {int(round(ideal_dropdown))}mm). "
                    f"Door height capped at {MAX_DOOR_HEIGHT}mm."
                )
            else:
                height_status = "Check height / dropdown settings."

            recommended_dropdown = int(round(dropdown_h))

        else:
            # Fixed dropdown options (108 / 90 / 50 / 0mm)
            selected_dropdown = TOP_LINER_OPTIONS.get(option, 108)
            dropdown_h = min(selected_dropdown, MAX_DROPDOWN_LIMIT)

            raw_door_height = base_usable_height - dropdown_h
            raw_door_height = max(raw_door_height, 0)  # guard against negative

            # Compute what dropdown would be needed to exactly hit MAX_DOOR_HEIGHT
            dropdown_needed_for_max = base_usable_height - MAX_DOOR_HEIGHT

            if raw_door_height <= MAX_DOOR_HEIGHT:
                final_door_h = raw_door_height
                height_status = "OK"
            else:
                # Door is still taller than allowed
                final_door_h = MAX_DOOR_HEIGHT

                if dropdown_needed_for_max <= MAX_DROPDOWN_LIMIT:
                    height_status = (
                        "Too tall for selected dropdown – "
                        f"need about {int(round(dropdown_needed_for_max))}mm dropdown "
                        f"(includes {TRACKSET_TOLERANCE}mm trackset tolerance)."
                    )
                else:
                    height_status = (
                        f"Too tall even at max {MAX_DROPDOWN_LIMIT}mm dropdown "
                        f"(includes {TRACKSET_TOLERANCE}mm trackset tolerance)."
                    )

            recommended_dropdown = None  # not bespoke

        # Door width including fixed overlap (no explicit gaps):
        # total coverage of doors = net_width + (doors - 1) * overlap
        overlap_mm = CUSTOM_DOOR_OVERLAP_MM
        if doors > 0:
            door_width = (net_width + (doors - 1) * overlap_mm) / doors
        else:
            door_width = 0

        door_span = doors * door_width
        total_overlap = (doors - 1) * overlap_mm  # for the Overlap_Tolerance_mm column

        issue_flag = "✅ OK" if str(height_status).startswith("OK") else "🔴 Check height"

        return pd.Series({
            "Door_Height_mm": int(round(final_door_h)),
            "Door_Width_mm": int(round(door_width)),
            "Doors_Used": int(doors),
            "Dropdown_Height_mm": int(round(dropdown_h)),
            "Recommended_Dropdown_Height_mm": recommended_dropdown,
            "Side_Liner_Thickness_mm": round(side_liner_thk, 1),
            "Required_Buildout_Per_Side_mm": 0.0,  # none, fixed at 18mm
            "Net_Width_mm": int(round(net_width)),
            "Door_Span_mm": int(round(door_span)),
            # Here: total overlap for made-to-measure mode
            "Overlap_Tolerance_mm": int(round(total_overlap)),
            "Span_Diff_mm": 0.0,                # not used in made-to-measure mode
            "Bottom_Liner_Length_mm": int(round(net_width)),
            "Side_Liner_Length_mm": int(round(height)),
            "Dropdown_Length_mm": int(round(net_width)),
            "Trackset_Tolerance_mm": int(TRACKSET_TOLERANCE),
            "Height_Status": height_status,
            "Issue": issue_flag,
        })


# ============================================================
# RESULTS TABLE
# ============================================================
st.subheader("2. Calculated results")

if len(edited_df) > 0:
    calcs = edited_df.apply(calculate_for_row, axis=1)
    results_df = pd.concat([edited_df.reset_index(drop=True), calcs], axis=1)

    st.dataframe(results_df, use_container_width=True)

    if not all(str(s).startswith("OK") for s in results_df["Height_Status"]):
        st.warning(
            "Some openings exceed height limits or need a different / larger dropdown to fit perfectly "
            "(after allowing for bottom liners and 54mm trackset tolerance)."
        )

    # CSV download
    csv = results_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "wardrobe_results.csv", "text/csv")

    # Optional: show only problematic rows below
    problem_rows = results_df[results_df["Issue"] != "✅ OK"]
    if not problem_rows.empty:
        st.markdown("#### Openings to check")
        st.dataframe(problem_rows, use_container_width=True)

    # ============================================================
    # VISUALISATION
    # ============================================================
    st.subheader("3. Visualise an opening")

    options = [
        f"{i}: {row['Job']} – {row['Opening']} ({row['Issue']}, {row['Door_System']})"
        for i, row in results_df.iterrows()
    ]
    selection = st.selectbox("Choose opening", options)
    idx = int(selection.split(":")[0])

    row = results_df.iloc[idx]

    # Build dropdown label for the top of the wardrobe
    dropdown_height_int = int(row["Dropdown_Height_mm"])
    dropdown_label = ""

    if row["Door_System"] == "Made to measure doors":
        if row["Top_Liner_Option"] == BESPOKE_DROPDOWN_LABEL:
            if dropdown_height_int > 0:
                dropdown_label = f"BESPOKE {dropdown_height_int}mm DROPDOWN"
            else:
                dropdown_label = "BESPOKE – NO DROPDOWN"
        else:
            if dropdown_height_int > 0:
                dropdown_label = f"{dropdown_height_int}mm DROPDOWN"
            else:
                dropdown_label = "NO DROPDOWN"
    else:
        # Fixed system – just show the actual dropdown height being used
        if dropdown_height_int > 0:
            dropdown_label = f"{dropdown_height_int}mm DROPDOWN"
        else:
            dropdown_label = "NO DROPDOWN"

    fig = draw_wardrobe_diagram(
        opening_width_mm=row["Width_mm"],
        opening_height_mm=row["Height_mm"],
        bottom_thk_mm=BOTTOM_LINER_THICKNESS,
        side_thk_mm=row["Side_Liner_Thickness_mm"],
        dropdown_height_mm=row["Dropdown_Height_mm"],
        door_height_mm=row["Door_Height_mm"],
        num_doors=row["Doors_Used"],
        door_width_mm=row["Door_Width_mm"],
        dropdown_label=dropdown_label,
    )

    # Diagram + door sizes side-by-side
    col1, col2 = st.columns([2, 1])

    with col1:
        # Main diagram
        st.pyplot(fig)

        # Photo + caption box for fixed-size system
        if row["Door_System"] == "Fixed 2223mm doors":
            # NOTE: update this path to something relative to your app, or remove if not needed.
            st.markdown("**Fixed-size dropdown example**")
            st.image(
                r"C:\Users\woolfendenj\Desktop\Wardrobe Calculator\Fixed Sized Dropdown.JPG",
                use_column_width=True,
            )
            st.markdown(
                """
                <div style="
                    border: 1px solid #ddd;
                    padding: 8px 10px;
                    border-radius: 4px;
                    font-size: 0.9em;
                    background-color: #f9f9f9;
                    margin-top: 4px;
                ">
                    Example photo of a fixed-size door dropdown. Use together with the calculated
                    side liner thickness, build-out per side, dropdown height, and trackset tolerance
                    shown on the right.
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col2:
        st.markdown("#### Door sizes for this opening")
        st.write(f"**Door system:** {row['Door_System']}")
        st.write(f"**Issue:** {row['Issue']}")
        st.write(f"**Height status:** {row['Height_Status']}")
        if row["Door_System"] == "Fixed 2223mm doors":
            st.write(f"**Fixed door width selected:** {int(row['Fixed_Door_Width_mm'])} mm")
        else:
            st.write(f"**Top liner option (input):** {row['Top_Liner_Option']}")
            st.write(f"**Per-meeting overlap (internal):** {CUSTOM_DOOR_OVERLAP_MM} mm")
            if row["Top_Liner_Option"] == BESPOKE_DROPDOWN_LABEL:
                st.write(
                    f"**Bespoke dropdown used in calc:** {int(row['Dropdown_Height_mm'])} mm "
                    "(auto-calculated)"
                )
        st.write("---")
        st.write(f"**Number of doors:** {int(row['Doors_Used'])}")
        st.write(f"**Door height:** {int(row['Door_Height_mm'])} mm")
        st.write(f"**Door width (each):** {int(row['Door_Width_mm'])} mm")
        st.write(f"**Door span (total):** {int(row['Door_Span_mm'])} mm")
        st.write(f"**Net opening width (between liners):** {int(row['Net_Width_mm'])} mm")
        st.write(f"**Side liner thickness (each):** {row['Side_Liner_Thickness_mm']} mm")
        st.write(
            f"**Required liner build-out per side:** "
            f"{row['Required_Buildout_Per_Side_mm']} mm (above 18mm default)"
        )
        st.write(f"**Total overlap / tolerance:** {int(row['Overlap_Tolerance_mm'])} mm")
        if row["Door_System"] == "Fixed 2223mm doors":
            st.write(
                f"**Span difference (door span - (net + tolerance)):** "
                f"{row['Span_Diff_mm']} mm"
            )
        st.write(f"**Trackset tolerance allowed:** {int(row['Trackset_Tolerance_mm'])} mm")
        st.write(
            f"**Height components (effective):** "
            f"{BOTTOM_LINER_THICKNESS}mm bottom liners + "
            f"{int(row['Trackset_Tolerance_mm'])}mm trackset tolerance + "
            f"{int(row['Dropdown_Height_mm'])}mm dropdown + "
            f"{int(row['Door_Height_mm'])}mm door"
        )
        st.write(f"**Dropdown height (used in calc):** {int(row['Dropdown_Height_mm'])} mm")

else:
    st.info("Add at least one opening to calculate sizes and view diagrams.")
