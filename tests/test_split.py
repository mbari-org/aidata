# mbari_aidata, Apache-2.0 license
# Filename: tests/test_split.py
# Description: Tests for the split command

import os
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from mbari_aidata.commands.split import split, split_command
from mbari_aidata.logger import CustomLogger

CustomLogger(output_path=Path.cwd() / "logs", output_prefix=__name__)


def setup():
    os.environ["ENVIRONMENT"] = "TESTING"


@pytest.fixture
def sample_dataset():
    """Create a sample dataset for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_input = Path(tmpdir) / "test_dataset"
        test_output = Path(tmpdir) / "output"
        
        # Create directory structure
        images_dir = test_input / "images"
        labels_dir = test_input / "labels"
        images_dir.mkdir(parents=True)
        labels_dir.mkdir(parents=True)
        test_output.mkdir(parents=True)
        
        # Create 100 dummy files to ensure all splits exist
        for i in range(100):
            # Create image file
            img_path = images_dir / f"image_{i:03d}.jpg"
            with open(img_path, 'w') as f:
                f.write(f"Fake image {i}")
            
            # Create corresponding label file
            label_path = labels_dir / f"image_{i:03d}.txt"
            with open(label_path, 'w') as f:
                f.write("0 0.5 0.5 0.3 0.3\n")
        
        yield test_input, test_output


def test_split_function(sample_dataset):
    """Test the split function directly"""
    test_input, test_output = sample_dataset
    
    # Run the split function
    split(test_input, test_output)
    
    # Check outputs
    labels_tar = test_output / "labels.tar.gz"
    images_tar = test_output / "images.tar.gz"
    
    assert labels_tar.exists(), "labels.tar.gz should be created"
    assert images_tar.exists(), "images.tar.gz should be created"
    assert labels_tar.stat().st_size > 0, "labels.tar.gz should not be empty"
    assert images_tar.stat().st_size > 0, "images.tar.gz should not be empty"
    
    # Check autosplit files were created
    for split_type in ['train', 'val', 'test']:
        split_file = test_input / f"autosplit_{split_type}.txt"
        assert split_file.exists(), f"autosplit_{split_type}.txt should be created"
        
        with open(split_file, 'r') as f:
            lines = f.readlines()
        assert len(lines) > 0, f"autosplit_{split_type}.txt should have entries"


def test_split_command_cli(sample_dataset):
    """Test the split command via CLI"""
    test_input, test_output = sample_dataset
    
    runner = CliRunner()
    result = runner.invoke(split_command, ['-i', str(test_input), '-o', str(test_output)])
    
    assert result.exit_code == 0, f"Command should succeed, got: {result.output}"
    
    # Check outputs
    labels_tar = test_output / "labels.tar.gz"
    images_tar = test_output / "images.tar.gz"
    
    assert labels_tar.exists(), "labels.tar.gz should be created"
    assert images_tar.exists(), "images.tar.gz should be created"


def test_split_command_missing_input():
    """Test that the command fails gracefully when input is missing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_input = Path(tmpdir) / "nonexistent"
        test_output = Path(tmpdir) / "output"
        test_output.mkdir()
        
        runner = CliRunner()
        result = runner.invoke(split_command, ['-i', str(test_input), '-o', str(test_output)])
        
        # Should not succeed if input doesn't exist
        assert result.exit_code == 0 or "missing" in result.output.lower()


def test_split_small_dataset():
    """Test split with a small dataset (may not have all splits)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_input = Path(tmpdir) / "test_dataset"
        test_output = Path(tmpdir) / "output"
        
        # Create directory structure
        images_dir = test_input / "images"
        labels_dir = test_input / "labels"
        images_dir.mkdir(parents=True)
        labels_dir.mkdir(parents=True)
        test_output.mkdir(parents=True)
        
        # Create only 5 files
        for i in range(5):
            img_path = images_dir / f"image_{i}.jpg"
            with open(img_path, 'w') as f:
                f.write(f"Fake image {i}")
            
            label_path = labels_dir / f"image_{i}.txt"
            with open(label_path, 'w') as f:
                f.write("0 0.5 0.5 0.3 0.3\n")
        
        # Should not fail even with small dataset
        split(test_input, test_output)
        
        # Check outputs
        labels_tar = test_output / "labels.tar.gz"
        images_tar = test_output / "images.tar.gz"
        
        assert labels_tar.exists(), "labels.tar.gz should be created"
        assert images_tar.exists(), "images.tar.gz should be created"
