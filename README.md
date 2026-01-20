# DumpOrganizer

A simple tool to organize photos and videos by date.

## What it does

Sorts your messy folders into `Year/Month/Day` structure. Copies files, doesn't touch originals.

## For Normal Users (Just want to use it)

1. **Download the EXE:**
   - Go to [Releases](https://github.com/Kazutosuna/DumpOrganizer/releases)
   - Download `DumpOrganizer.exe`
   - Put it anywhere (Desktop is fine)

2. **Run it:**
   - Double-click `DumpOrganizer.exe`
   - Windows might say "Unknown publisher" - click "More info" → "Run anyway"

3. **Use it:**
   - Select your messy folder
   - Choose which file types to organize
   - Pick where to put organized files
   - Click "Start Sorting"

## For Developers (Want to modify/run from source)

```bash
# Clone it
git clone https://github.com/Kazutosuna/DumpOrganizer.git
cd DumpOrganizer

# Install Python 3.8+ if you don't have it

# Install requirements
pip install pillow

# Run it
python main.py

# Build EXE (optional)
pip install pyinstaller
python build_exe.py  # EXE goes to dist/ folder
```

## Supported files

- **Photos**: .jpg, .jpeg, .png, .gif, .bmp, .tiff, .webp
- **Videos**: .mp4, .avi, .mov, .wmv, .flv, .mkv, .m4v

## How it works

1. Tries to get date from EXIF data in photos
2. Falls back to file creation date
3. Copies files to organized folders
4. Original files stay where they are

Example output:
```
Organized/
├── 2023/
│   └── 12/
│       └── 25/
│           └── christmas.jpg
└── 2024/
    └── 01/
        └── 15/
            └── birthday.mp4
```

## Notes

- Works offline
- No installation needed (just the EXE)
- Handles duplicate file names
- Shows progress as it works

---

*Made for lazy people xd.*
