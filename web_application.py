# streamlit_app.py
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
import pandas as pd
from typing import List
from datetime import timedelta
from lastganganalyse.data_loader import DataLoader
from lastganganalyse.statistics import MonthlyStatistics
from lastganganalyse.data_plot import plot_monthly_bar, plot_yearly


def process_files(
    uploaded_files: List[UploadedFile],
    year: int,
    time_delta: timedelta,
    threshold: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    dfs: List[pd.DataFrame] = []
    for uploaded_file in uploaded_files:
        # Use DataLoader to load each file, initializing it with the specified time delta
        data_loader = DataLoader(uploaded_file, time_delta)
        data_loader.load_excel()
        dfs.append(data_loader.df)

    if dfs:
        # Process the loaded DataFrames with MonthlyStatistics
        monthly_stats = MonthlyStatistics(dfs, year)
        monthly_stats.calculate_monthly_sum()
        monthly_stats.calculate_monthly_max()
        monthly_stats.count_values_above_threshold(
            threshold
        )  # Use the user-specified threshold
        monthly_stats.count_values_below_threshold(threshold)
        monthly_stats.calculate_percentage()
        monthly_stats.calculate_ratio_of_sum_to_max()
        return monthly_stats.get_stats_df(), monthly_stats.get_raw_df()
    else:
        return (
            pd.DataFrame(),
            pd.DataFrame(),
        )  # Return an empty DataFrame if no files were processed


def main():
    st.set_page_config(
        page_title="Lastganganalyse",
        layout="wide",
        page_icon=":chart_with_downwards_trend:",
    )
    st.title("EMV-Lastganganalyse")

    # File uploader
    uploaded_files: List[UploadedFile] = st.file_uploader(
        "Excel Rohdaten Upload", accept_multiple_files=True, type=["xlsx"]
    )

    # User inputs for year, threshold, and time delta
    year: int = st.number_input(
        "Jahr des Lastgangs", min_value=1900, max_value=2100, value=2022
    )
    threshold: float = st.number_input(
        "Lastspitzengrenzwert [kW]", value=501, min_value=0
    )

    # Time delta input
    time_delta_minutes: int = st.number_input(
        "Zeitdifferenz der Messwerte [min]", min_value=1, value=15
    )
    time_delta: timedelta = timedelta(minutes=time_delta_minutes)

    if st.button("Berechnen"):
        if uploaded_files and year and time_delta:
            result_df, raw_df = process_files(
                uploaded_files, year, time_delta, threshold
            )
            if not result_df.empty:
                st.write("Analysis Result:")
                st.dataframe(result_df)
                st.plotly_chart(plot_yearly(raw_df))
                st.plotly_chart(plot_monthly_bar(result_df))
            else:
                st.write("No data to display. Please upload valid Excel files.")
        else:
            st.write(
                "Please upload at least one Excel file, enter the year of the dataset, and specify the time delta."
            )


if __name__ == "__main__":
    main()
