#!/bin/bash
# --- Configuration ---
# (Moved date calculation after user input)

# --- User Input ---
# Prompt the user for the destination directory.
read -p "Enter the destination directory path: " DEST_DIR

# Prompt the user for the number of days to look back.
read -p "Enter the number of days to look back: " DAYS_BACK

# --- Validation ---
# Validate that DAYS_BACK is a positive integer.
if ! [[ "$DAYS_BACK" =~ ^[0-9]+$ ]]; then
  echo "Error: '$DAYS_BACK' is not a valid number. Exiting."
  exit 1
fi

# Calculate the start date based on user input.
START_DATE=$(date -d "$DAYS_BACK days ago 00:00:00" +%Y-%m-%d)

# Check if the destination directory exists. If not, create it.
if [ ! -d "$DEST_DIR" ]; then
  echo "Destination directory does not exist. Creating it..."
  mkdir -p "$DEST_DIR"
  if [ $? -ne 0 ]; then
    echo "Error: Failed to create directory '$DEST_DIR'. Exiting."
    exit 1
  fi
fi

# --- Search and Copy ---
echo "Searching for files modified within the last $DAYS_BACK day(s) (since $START_DATE) and copying to '$DEST_DIR'..."

# Use 'find' to search recursively.
# -type f: Only find files (not directories).
# -newermt "$START_DATE": Find files newer than the calculated start date.
# The 'while read' loop handles filenames with spaces or special characters correctly.
find . -type f -newermt "$START_DATE" -print0 | while IFS= read -r -d $'\0' file; do
  echo "Copying '$file'..."
  cp --parents "$file" "$DEST_DIR"
done

echo "Operation complete."
