from typing import List
from pandas import DataFrame, Series
import pandas as pd


class MonthlyStatistics:
    def __init__(self, dfs: List[DataFrame], year: int) -> None:
        self.combined_df: DataFrame = self.combine_dataframes(dfs)
        self.year: int = year
        self.stats_df: DataFrame = self.initialize_stats_df()
        self.threshold: float = 0.0  # Default threshold value

    def combine_dataframes(self, dfs: List[DataFrame]) -> DataFrame:
        # when more than one df is given: power values are added for same time
        # """Combine the list of DataFrames into a single DataFrame."""
        # combined_df: DataFrame = pd.concat(dfs, ignore_index=True)
        """Combine the list of DataFrames into a single DataFrame by summing their second columns."""
        combined_df = pd.concat(dfs).groupby(dfs[0].columns[0], as_index=False).sum()
        return combined_df

    def initialize_stats_df(self) -> DataFrame:
        """Initialize the statistics DataFrame with all months of the year."""
        start_date: str = f"{self.year}-01-01"
        months: DataFrame = pd.DataFrame(
            {"Month": pd.date_range(start=start_date, periods=12, freq="MS")}
        )
        months["Month"] = months["Month"].dt.to_period("M")
        return months

    def calculate_monthly_sum(self) -> None:
        """Calculate the sum of values for each month."""
        self.combined_df["Month"] = self.combined_df.iloc[:, 0].dt.to_period("M")
        # dividing by 4 comes from the interval 15min, so this must be turned into a variable
        # here calculating from kW to kWh?
        monthly_sum: Series = (
            self.combined_df.groupby("Month")[self.combined_df.columns[1]].sum() / 4
        )
        self.stats_df = self.stats_df.merge(
            monthly_sum, how="left", left_on="Month", right_index=True
        )
        self.stats_df.rename(
            columns={self.stats_df.columns[1]: "Verbrauch pro Monat"}, inplace=True
        )
        self.stats_df["Verbrauch pro Monat"] = self.stats_df[
            "Verbrauch pro Monat"
        ].round(0)

    def calculate_monthly_max(self) -> None:
        """Calculate the maximum value for each month."""
        monthly_max: Series = self.combined_df.groupby("Month").max().iloc[:, 1]
        self.stats_df = self.stats_df.merge(
            monthly_max, how="left", left_on="Month", right_index=True
        )
        self.stats_df.rename(
            columns={self.stats_df.columns[2]: "Höchster Wert pro Monat"}, inplace=True
        )

    def count_values_above_threshold(self, threshold: float) -> None:
        """Count how often values per month are above a given threshold."""
        self.threshold = threshold
        counts_above_threshold: Series = (
            self.combined_df[self.combined_df.iloc[:, 1] > self.threshold]
            .groupby("Month")
            .count()
            .iloc[:, 0]
        )
        self.stats_df = self.stats_df.merge(
            counts_above_threshold, how="left", left_on="Month", right_index=True
        ).fillna(0)
        self.stats_df.rename(
            columns={self.stats_df.columns[3]: f"Ereignisse über {self.threshold} kW"},
            inplace=True,
        )

    def count_values_below_threshold(self, threshold: float) -> None:
        """Count how often values per month are below a given threshold."""
        self.threshold = threshold
        counts_above_threshold: Series = (
            self.combined_df[self.combined_df.iloc[:, 1] <= self.threshold]
            .groupby("Month")
            .count()
            .iloc[:, 0]
        )
        self.stats_df = self.stats_df.merge(
            counts_above_threshold, how="left", left_on="Month", right_index=True
        ).fillna(0)
        self.stats_df.rename(
            columns={self.stats_df.columns[4]: f"Ereignisse unter {self.threshold} kW"},
            inplace=True,
        )

    def calculate_percentage(self) -> None:
        """Calculate the percetage between the number of events below threshold"""
        self.stats_df["in %"] = (
            self.stats_df.iloc[:, 3]
            / (self.stats_df.iloc[:, 3] + self.stats_df.iloc[:, 4])
            * 100
        )
        self.stats_df["in %"] = self.stats_df["in %"].round(2)

    def calculate_ratio_of_sum_to_max(self) -> None:
        """Create a new column in stats_df that is the ratio of the 'Sum' column to the 'Max' column, handling division by 0."""
        # Use a lambda function to safely handle division, replacing division by 0 with None (or another chosen value)
        self.stats_df["VBH"] = self.stats_df.apply(
            lambda row: (
                row[self.stats_df.columns[1]] / row[self.stats_df.columns[2]]
                if row[self.stats_df.columns[2]] != 0
                else None
            ),
            axis=1,
        )
        self.stats_df["VBH"] = self.stats_df["VBH"].round(0)

    def get_stats_df(self) -> DataFrame:
        """Return the statistics DataFrame."""
        return self.stats_df

    def get_raw_df(self) -> DataFrame:
        """Return the raw data as one DataFrame"""
        return self.combined_df
