# mbari_aidata, Apache-2.0 license
# Filename: commands/load_clusters.py
# Description: Load clusters from a directory with SDCAT formatted CSV files
import click
import pandas as pd
import tator

from mbari_aidata import common_args
from pathlib import Path
from mbari_aidata.logger import create_logger_file, info, err, debug
from mbari_aidata.plugins.extractors.tap_sdcat_csv import extract_sdcat_csv
from mbari_aidata.plugins.loaders.tator.common import init_yaml_config, find_box_type, find_media_type, init_api_project, get_version_id

@click.command("clusters", help="Load cluster from a SDCAT formatted CSV files")
@common_args.token
@common_args.yaml_config
@common_args.dry_run
@common_args.version
@click.option("--input", type=Path, required=True, help=" VOC xml or SDCAT formatted CSV files")
@click.option("--max-num", type=int, help="Maximum number of cluster assignments to load")
@click.option("--update", is_flag=True, default=False, help="Update localization instead of creating new ones")
def load_clusters(token: str, config: str, version: str, input: Path, dry_run: bool, max_num: int, update: bool) -> int:
    """Load clusters from a directory SDCAT formatted CSV files. Returns the number of clusters loaded.
    Assumes that the data is already loaded into Tator and rows reference the database ids."""

    try:
        create_logger_file("load_clusters")

        # Load the configuration file
        config_dict = init_yaml_config(config)
        project = config_dict["tator"]["project"]
        host = config_dict["tator"]["host"]

        # Initialize the Tator API
        api, tator_project = init_api_project(host, token, project)
        box_type = find_box_type(api, tator_project.id, "Box")
        version_id = get_version_id(api, tator_project, version)
        assert box_type is not None, f"No box type found in project {project}"
        assert version_id is not None, f"No version found in project {project}"

        info(f"Loading clusters from directory {input}")
        valid_extensions = [".csv"]
        df = pd.DataFrame()
        if input.is_dir():
            # Search for files with valid extensions
            files = list(input.rglob("*"))
            info(f"Found {len(files)} files in {input}")
            valid_files = [f for f in files if f.suffix in valid_extensions]
            if len(valid_files) == 0:
                err(f"No valid files found in {input}")
                return 0
            # Use the first valid file and its extension to determine the extractor
            first_file = valid_files[0]
            if first_file.suffix in valid_extensions:
                extractor = extract_sdcat_csv[first_file.suffix[1:]]
                df = extractor(input)
        else:
            # Use the extension of the file to determine the extractor
            info(f"Reading file {input}")
            if not input.exists():
                err(f"File {input} does not exist")
                return 0
            df = extract_sdcat_csv(input)

        if len(df) == 0:
            info(f"No data found in {input}")
            return 0

        if dry_run:
            info(f"Dry run - not loading {len(df)} cluster entries into Tator")
            return 0

        # Check if the dataframe has the required column image_path
        if "image_path" not in df.columns:
            err(f"No image_path column found in {input}")
            return 0

        if "id" not in df.columns:
            def get_index_from_fname(row):
                stem = Path(row.image_path).stem # Get the stem of the image path which is the media id, e.g. 390088.jpg
                # Error if the index is not a number
                try:
                    id = int(stem)
                except ValueError:
                    err(f"Index {stem} is not a number. Please check the image_path column in {input}. Should be the media id followed by the image extension, e.g. 35661.jpg.")
                    return None
                return id

            # Make a new column with the database id
            df["id"] = df.apply(get_index_from_fname, axis=1)

        # Drop rows with missing id
        df = df.dropna(subset=["id"])
        if len(df) == 0:
            info(f"No data found in {input} after dropping rows with missing id")
            return 0

        # Rename the class_s column to Label if it exists since that is a reserved name
        if "class" in df.columns:
            df = df.rename(columns={"class": "label"})

        max_load = -1 if max_num is None else max_num

        # Truncate the boxes if the max number of boxes to load is set
        if 0 < max_load <= len(df):
            df = df[:max_load]

        if dry_run:
            info(f"Dry run - not loading {len(df)} cluster entries into Tator")
            return 0


        # Helper to split a DataFrame into batches of N rows
        def batch_group(my_df, batch_size=5):
            return [my_df.iloc[i:i + batch_size] for i in range(0, len(my_df), batch_size)]

        # Iterate over each group, then each chunk in the group
        for group_name, group_df in df.groupby("cluster"):
            chunks = batch_group(group_df, 100)

            if update:
                cluster_name = f'Unknown C{group_name}'
                params = {"type": box_type.id}
                for i, chunk in enumerate(chunks):
                    info(f"cluster: {group_name}, chunk: {i + 1}")
                    id_bulk_patch = {
                        "attributes": {"cluster": cluster_name},
                        "ids": chunk.id.values.tolist(),
                        "in_place": 1,
                    }
                    try:
                        info(id_bulk_patch)
                        response = api.update_localization_list(project=tator_project.id, **params,
                                                                localization_bulk_update=id_bulk_patch)
                        debug(response)
                    except Exception as e:
                        err(f"Failed to update localizations to {cluster_name}. Error: {e}")
                        return 1

                    info(f"Updated {len(chunk)} localizations to {cluster_name} in version {version_id}")
            else:
                cluster_name = f'Unknown C{group_name}'

                for i, chunk in enumerate(chunks):
                    info(f"cluster: {group_name}, chunk: {i + 1}")
                    specs = []
                    for _, row in chunk.iterrows():
                        spec = tator.models.LocalizationSpec(
                            type=box_type.id,
                            media_id=row.id,
                            version=version_id,
                            x=row.x if "x" in row else 0.0,
                            y=row.y if "y" in row else 0.0,
                            width=row.width if "width" in row else 1.0,
                            height=row.height if "height" in row else 1.0,
                            frame=row.frame if "frame" in row else 0,
                            attributes={
                                "Label": row.label if "label" in row else cluster_name,
                                "label_s": row.class_s if "class_s" in row else cluster_name,
                                "score": row.score if "score" in row else 1.0,
                                "score_s": str(row.score_s) if "score_s" in row else "1.0",
                                "cluster": cluster_name
                            },
                        )
                        specs.append(spec)

                    try:
                        response = api.create_localization_list(project=tator_project.id, body=specs)
                        info(f"Created {len(chunk)} localizations for {cluster_name} in version {version_id}")
                        debug(response)
                    except Exception as e:
                        err(f"Failed to create localizations for {cluster_name}. Error: {e}")
                        return 1


    except Exception as e:
        err(f"Error loading clusters: {e}")
        return 1

    info(f"Done. Loaded {len(df)} cluster entries into Tator")
