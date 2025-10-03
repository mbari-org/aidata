# mbari_aidata, Apache-2.0 license
# Filename: commands/split.py
# Description: Split data into train/val/test sets

import os
import random
import shutil
import tarfile
import tempfile
from pathlib import Path

import click
from tqdm import tqdm

from mbari_aidata.logger import create_logger_file, debug, err, info


def split(input_path: Path, output_path: Path):
    """
    Split data into train/val/test sets randomly per the following percentages 85%/10%/5%
    
    Args:
        input_path: Path to the root folder with images and labels organized into labels/ and images/ folders
        output_path: Path to the root folder to save the split, compressed files
    """
    #########################################
    # Credit to http://github.com/ultralytics/yolov5 code for this snippet
    #########################################
    def autosplit(path: Path, weights: tuple, annotated_only: bool):
        files = sorted(x for x in path.rglob('*.*') if
                       x.suffix[1:].lower() in ['bmp', 'dng', 'jpeg', 'jpg', 'mpo', 'png', 'tif', 'tiff',
                                                'webp'])  # image files only
        n = len(files)
        random.seed(0)  # for reproducibility
        indices = random.choices([0, 1, 2], weights=weights, k=n)  # assign each image to a split
        txt = ['autosplit_train.txt', 'autosplit_val.txt', 'autosplit_test.txt']
        # remove existing
        for x in txt:
            if (path.parent / x).exists():
                (path.parent / x).unlink()
        info(f'Autosplitting images from {path}' + ', using *.txt labeled images only' * annotated_only)

        def img2label_paths(img_paths):
            # Define label paths as a function of image paths
            sa, sb = f'{os.sep}images{os.sep}', f'{os.sep}labels{os.sep}'  # /images/, /labels/ substrings
            return [sb.join(x.rsplit(sa, 1)).rsplit('.', 1)[0] + '.txt' for x in img_paths]

        for i, img in tqdm(zip(indices, files), total=n, desc="Autosplitting"):
            if not annotated_only or Path(img2label_paths([str(img)])[0]).exists():  # check label
                with open(path.parent / txt[i], 'a') as f:
                    f.write('./' + img.relative_to(path.parent).as_posix() + '\n')  # add image to txt file

    #########################################

    # do the work in a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        autosplit(path=input_path / 'images', weights=(0.85, 0.10, 0.05), annotated_only=False)

        for v in ['train', 'val', 'test']:
            image_path = temp_path / 'images' / v
            label_path = temp_path / 'labels' / v
            image_path.mkdir(parents=True)
            label_path.mkdir(parents=True)
            split_path = (input_path / f'autosplit_{v}.txt')
            
            if not split_path.exists():
                debug(f'Skipping {v} - no files assigned to this split')
                continue
                
            debug(f'Splitting {split_path}')
            with (split_path).open('r+t') as f:
                lines = f.readlines()
            for line in tqdm(lines, desc=f"Copying {v} files"):
                filename = Path(line.strip())
                shutil.copy2((input_path / 'labels' / f'{filename.stem}.txt').as_posix(),
                             (label_path / f'{filename.stem}.txt').as_posix())
                shutil.copy2((input_path / filename).as_posix(),
                             (image_path / filename.name).as_posix())

        info(f"Creating {(output_path / 'labels.tar.gz').as_posix()}...")
        with tarfile.open((output_path / 'labels.tar.gz').as_posix(), 'w:gz') as t:
            t.add((temp_path / 'labels').as_posix(), arcname='labels')

        info(f"Creating {(output_path / 'images.tar.gz').as_posix()}...")
        with tarfile.open((output_path / 'images.tar.gz').as_posix(), 'w:gz') as t:
            t.add((temp_path / 'images').as_posix(), arcname='images')

        info('Done')


@click.command(name="split")
@click.option('-i', '--input', type=str, required=True,
              help='Path to the root folder with images and labels, organized into labels/ and images/ folders files to split')
@click.option('-o', '--output', type=str, required=True,
              help='Path to the root folder to save the split, compressed files. If it does not exist, it will be created.')
def split_command(input: str, output: str):
    """
    Split data into train/val/test sets randomly per the following percentages 85%/10%/5%
    """
    create_logger_file("split")
    
    input_path = Path(input)
    output_path = Path(output)

    if not output_path.exists():
        output_path.mkdir(parents=True)

    paths = [input_path / 'labels', input_path / 'images']

    exists = [not p.exists() for p in paths]
    if any(exists):
        err(f'Error: one or more {paths} missing')
        return

    split(Path(input), Path(output))
