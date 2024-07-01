import pandas as pd
from pandas import DataFrame, Timedelta
from pathlib import Path
from datetime import datetime
from streamlit.runtime.uploaded_file_manager import UploadedFile
from datetime import timedelta


class DataLoader:
    def __init__(self, file_obj: UploadedFile, time_delta: timedelta) -> None:
        self.file_obj: UploadedFile = file_obj
        self.time_delta: Timedelta = pd.to_timedelta(time_delta)
        self.df: DataFrame = pd.DataFrame()

    def validate_path(self, file_path: UploadedFile) -> Path:
        """Validate the given file path."""
        path: Path = Path(str(file_path))
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(
                f"The file {file_path} does not exist or is not a file."
            )
        return path

    def load_excel(self) -> None:
        """Load data from an Excel file."""
        self.df: DataFrame = pd.read_excel(self.file_obj, skiprows=1)
        self.df.iloc[:, 0] = pd.to_datetime(self.df.iloc[:, 0])

    def fill_missing_times(self) -> None:
        """Fill missing time entries in the loaded DataFrame."""
        if self.df.empty:
            raise ValueError("DataFrame is empty. Please load the data first.")

        i: int = 1
        while i < len(self.df):
            time_diff: Timedelta = self.df.iloc[i, 0] - self.df.iloc[i - 1, 0]  # type: ignore
            if time_diff > self.time_delta:
                num_entries_to_add: int = int(time_diff / self.time_delta) - 1
                entries_to_append: list = []
                for j in range(1, num_entries_to_add + 1):
                    new_time: datetime = self.df.iloc[i - 1, 0] + j * self.time_delta  # type: ignore
                    entries_to_append.append(
                        {self.df.columns[0]: new_time, self.df.columns[1]: 0}
                    )

                # Append in bulk to improve performance
                self.df = pd.concat(
                    [self.df, pd.DataFrame(entries_to_append)], ignore_index=True
                )
                i += num_entries_to_add  # Adjust index to skip newly added rows

            i += 1

        self.df = self.df.sort_values(by=self.df.columns[0]).reset_index(drop=True)
