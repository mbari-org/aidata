# mbari_aidata, Apache-2.0 license
# Filename: tests/test_cli_performance.py
# Description: Test CLI performance to ensure lazy loading is working

import subprocess
import time


def test_cli_help_performance():
    """Test that CLI help command is reasonably fast due to lazy loading"""
    start = time.time()
    result = subprocess.run(
        ["python", "-m", "mbari_aidata", "--help"],
        capture_output=True,
        text=True,
        timeout=5
    )
    elapsed = time.time() - start
    
    # Should complete successfully
    assert result.returncode == 0
    assert "Load data to tator database" in result.stdout
    
    # Should be much faster than 1 second (was ~4.4s before refactoring)
    assert elapsed < 1.0, f"CLI help took {elapsed:.2f}s, expected < 1.0s"
    

def test_subcommand_help():
    """Test that subcommand help works with lazy loading"""
    result = subprocess.run(
        ["python", "-m", "mbari_aidata", "load", "--help"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    # Should complete successfully
    assert result.returncode == 0
    assert "Load data, such as images, boxes, and exemplars" in result.stdout
    
    # Should list all the lazy-loaded commands
    assert "images" in result.stdout
    assert "boxes" in result.stdout
    assert "tracks" in result.stdout
    

def test_specific_command_help():
    """Test that specific command help works with lazy loading"""
    result = subprocess.run(
        ["python", "-m", "mbari_aidata", "load", "images", "--help"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    # Should complete successfully
    assert result.returncode == 0
    assert "Load images from a directory" in result.stdout
    assert "--input" in result.stdout
    assert "--token" in result.stdout


def test_all_command_groups():
    """Test that all command groups work with lazy loading"""
    command_groups = ["load", "download", "db", "transform"]
    
    for group in command_groups:
        result = subprocess.run(
            ["python", "-m", "mbari_aidata", group, "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 0, f"Command group '{group}' failed"
        assert "--help" in result.stdout
