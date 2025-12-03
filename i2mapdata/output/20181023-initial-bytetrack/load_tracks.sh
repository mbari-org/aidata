# !/bin/bash

TATOR_TOKEN="ae84628927851c1a545c375ea8e4c3da2a022400"
# Find all .tracks.tar.gz files in the current directory and its subdirectories
find . -type f -name "*-tracks.tar.gz" | while read -r file; do
    aidata load tracks --input $file --token $TATOR_TOKEN --version i2map-rfdetr-large-728x728-pseudo --config https://docs.mbari.org/internal/ai/projects/config/config_i2map.yml
done