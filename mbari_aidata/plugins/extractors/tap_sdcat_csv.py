# mbari_aidata, Apache-2.0 license
# Filename: plugins/extractors/tap_sdcat_csv.py
# Description: Extracts data from a SDCAT generated csv files and prepares it for loading into Tator

from pathlib import Path
import pandas as pd
import tqdm

def extract_sdcat_csv(csv_path: Path) -> pd.DataFrame:
    """Extracts data from a SDCAT generated csv files."""
    dfs = []

    if csv_path.is_dir():
        for det_csv_path in tqdm.tqdm(list(csv_path.rglob("*.csv")), desc="Reading SDCAT CSVs"):
            try:
                df = pd.read_csv(det_csv_path.as_posix())
                dfs.append(df)
            except Exception as e:
                print(f"Error reading {det_csv_path}: {e}")
                continue
            dfs.append(df)
        if len(dfs) == 0:
            return pd.DataFrame()
        combined_df = pd.concat(dfs, ignore_index=True)
    else:
        combined_df = pd.read_csv(csv_path)

    if len(combined_df) == 0:
        return combined_df

    combined_df = combined_df.sort_values(by="image_path")

    # If x, y, xx, xy columns are not present, return the dataframe as is
    if not all(col in combined_df.columns for col in ["x", "y", "xx", "xy"]):
        return combined_df

    # Remove any duplicate rows; duplicates have the same .x, .y, .xx, .xy, and image_path
    combined_df = combined_df.drop_duplicates(subset=["x", "y", "xx", "xy", "image_path"])

    if "class" in combined_df.columns:
        combined_df["label"] = combined_df["class"]

    # Replace /home/ubuntu with /Volumes/tatordata
    combined_df["image_path"] = combined_df["image_path"].str.replace("/home/ubuntu", "/Volumes/tatordata")

    # If image paths look like <prefix><frame>.<ext>, add a frame column with the frame number
    image_names = combined_df["image_path"].astype(str).str.replace("\\", "/", regex=False).str.rsplit("/", n=1).str[-1]
    frame_match = image_names.str.extract(r"^(?P<prefix>.*?)(?P<frame>\d+)\.(?P<ext>[^.]+)$")
    if frame_match["frame"].notna().any():
        frame_series = pd.to_numeric(frame_match["frame"], errors="coerce")
        if "frame" in combined_df.columns:
            combined_df["frame"] = combined_df["frame"].fillna(frame_series)
        else:
            combined_df["frame"] = frame_series
        combined_df["frame"] = combined_df["frame"].astype(int)

    return combined_df
