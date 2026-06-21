import streamlit as st
import pandas as pd
import os
import zipfile
from pdf_generator import generate_pdf

st.title("Physician Income Generator")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:

    # ✅ Read Excel
    df = pd.read_excel(uploaded_file, engine="openpyxl")

    # ✅ Show count
    st.success(f"{len(df)} physicians found")
    st.dataframe(df.head())

    if st.button("Generate PDFs"):

        output_folder = "output"

        # ✅ Prepare output folder
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        else:
            for f in os.listdir(output_folder):
                os.remove(os.path.join(output_folder, f))

        total_rows = len(df)
        progress = st.progress(0)

        # ✅ Loop through rows
        for i, (_, row) in enumerate(df.iterrows()):

            # ✅ Normalize column names
            row_dict = {
                k.strip().lower().replace(" ", "_"): v
                for k, v in row.to_dict().items()
            }

            # ✅ Extract fields
            sap = row_dict.get("sap", "NA")
            month = row_dict.get("month", "NA")
            year = row_dict.get("year", "NA")

            # ✅ Clean name for filename
            name_safe = str(row_dict.get("name", "unknown"))
            name_safe = name_safe.replace(" ", "_")

            # ✅ Optional: shorten (remove this line if you want full name)
            name_safe = name_safe[:30]

            # ✅ Final filename WITH NAME ✅
            filename = f"{sap}_{name_safe}_{month}_{year}.pdf"

            # ✅ Generate PDF
            generate_pdf(row_dict, filename)

            # ✅ Update progress
            progress.progress((i + 1) / total_rows)

        # ✅ Create ZIP
        zip_path = "physician_reports.zip"

        with zipfile.ZipFile(zip_path, "w") as z:
            for f in os.listdir(output_folder):
                z.write(os.path.join(output_folder, f), f)

        # ✅ Download button
        with open(zip_path, "rb") as f:
            st.download_button(
                "Download All PDFs",
                f,
                file_name="physician_reports.zip"
            )