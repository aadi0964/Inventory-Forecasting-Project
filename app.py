import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Set wide layout to reduce scrolling and utilize space
st.set_page_config(layout="wide", page_title="Inventory Optimization Dashboard")

# Title at top with no extra space (tight margin)
st.markdown(
    """
    <div style='display: flex; justify-content: flex-start; align-items: center; margin-bottom: 0.5rem;'>
        <h1 style='margin-bottom: 0; font-size: 1.5rem;'>Inventory Optimization Dashboard</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

# Load main data quietly
file_path = r"C:\Users\aadit\OneDrive\Desktop\project files\updated_inventory_results.xlsx"
try:
    df = pd.read_excel(file_path)
except Exception as e:
    st.error(f"Error loading file: {e}")
    st.stop()

# Load consumption data for dynamic location chart
consumption_path = r"C:\Users\aadit\OneDrive\Desktop\project files\new Consumption Data for Trainee Ver1.XLSX"
try:
    consumption_df = pd.read_excel(consumption_path)
except Exception as e:
    st.warning(f"Could not load consumption data for location chart: {e}")
    consumption_df = pd.DataFrame()

# Layout: Input box | Top 5 Materials Chart | Top 10 Locations Chart
input_col, material_chart_col, location_chart_col = st.columns([1, 2, 2], gap="small")

with input_col:
    pasted_ids = st.text_area("Enter Material ID(s) (comma/newline separated)", "", height=50, label_visibility="collapsed")
    ids = []
    if pasted_ids:
        ids = [float(x.strip()) for x in pasted_ids.replace(",", "\n").split("\n") if x.strip()]
    filtered = df[df["Material"].isin(ids)] if ids else pd.DataFrame()

with material_chart_col:
    if not filtered.empty:
        def parse_qty_with_unit(qty_str):
            if not isinstance(qty_str, str):
                return 0.0, "Unknown"
            try:
                parts = qty_str.split(" ", 1)
                val = float(parts[0])
                unit = parts[1] if len(parts) > 1 else "Unknown"
                return val, unit
            except:
                return 0.0, "Unknown"

        parsed = filtered["Forecasted Usage (6 Months)"].apply(parse_qty_with_unit)
        filtered["usage_val"] = [p[0] for p in parsed]
        filtered["usage_unit"] = [p[1] for p in parsed]

        chart_data = filtered.sort_values("usage_val", ascending=False).head(5)
        top_n = len(chart_data)

        fig, ax = plt.subplots(figsize=(4, 3))
        ax.bar(chart_data["Material"].astype(str), chart_data["usage_val"], color="skyblue")
        unit_label = chart_data["usage_unit"].mode()[0] if not chart_data["usage_unit"].empty else "Unknown"
        ax.set_ylabel(f"Forecasted Usage (6 Months)")
        ax.set_xlabel("Material ID")
        ax.set_title(f"Top {top_n} Materials by Usage")
        plt.xticks(rotation=45, ha="right", fontsize=7)
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.info("Enter IDs to see material chart.")

with location_chart_col:
    if not filtered.empty and not consumption_df.empty:
        filter_consumption = consumption_df[consumption_df["Material"].isin(ids)]
        location_usage = filter_consumption.groupby('Storage location')['Qty in unit of entry'].sum().abs().nlargest(10)

        if not location_usage.empty:
            fig2, ax2 = plt.subplots(figsize=(4, 3))
            location_usage.plot(kind='bar', ax=ax2, color="lightgreen")
            ax2.set_ylabel("Total Usage (Units)")
            ax2.set_xlabel("Storage Location")
            ax2.set_title("Top 10 Locations by Usage")
            plt.xticks(rotation=45, ha="right", fontsize=7)
            plt.tight_layout()
            st.pyplot(fig2)
        else:
            st.info("No location data for entered materials.")
    else:
        st.info("Enter IDs to see location chart.")

# Display results table without usage_val and usage_unit
if not filtered.empty:
    display_df = filtered.drop(columns=["usage_val", "usage_unit"], errors="ignore")
    st.markdown(f"<h6 style='margin-bottom: 0.2rem; margin-top: 0.5rem;'>Results for {len(display_df)} Materials</h6>", unsafe_allow_html=True)
    st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.info("No matching materials found or no IDs provided yet.")
