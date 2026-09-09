#!/bin/bash
# --- User Input ---
read -p "Enter the destination directory path: " DEST_DIR
read -p "Enter the number of days to look back: " DAYS_BACK

# --- Validation ---
if ! [[ "$DAYS_BACK" =~ ^[0-9]+$ ]]; then
  echo "Error: '$DAYS_BACK' is not a valid number. Exiting."
  exit 1
fi

# Calculate the start date (macOS BSD date syntax)
START_DATE=$(date -v-"${DAYS_BACK}"d +%Y-%m-%d)

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

# Use 'find' with -mtime instead of -newermt
# -mtime -N finds files modified less than N days ago
find . -type f -mtime -"$DAYS_BACK" -print0 | while IFS= read -r -d '' file; do
  # Recreate the parent directory structure manually
  # (macOS cp doesn't support --parents)
  dest_file="$DEST_DIR/$file"
  dest_dir=$(dirname "$dest_file")
  mkdir -p "$dest_dir"
  echo "Copying '$file'..."
  cp "$file" "$dest_file"
done

echo "Operation complete."