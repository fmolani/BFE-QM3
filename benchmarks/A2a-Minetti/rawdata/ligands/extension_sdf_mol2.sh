#!/bin/bash

# Change directory to the one containing the files
cd ./

# Loop through all files with .sdf extension in the directory
for file in *.sdf; do
    # Get the file name without extension
    filename=$(basename "$file" .sdf)
    # Rename the file with the new .mol2 extension
    mv "$filename.sdf" "$filename.mol"
done
