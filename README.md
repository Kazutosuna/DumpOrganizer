# DumpOrganizer

A simple tool to organize photos and videos by date.

## What it does

Sorts your messy folders into `Year/Month/Day` structure. Copies files, doesn't touch originals.

## How to use

1. Run `DumpOrganizer.exe`
2. Pick a messy folder to scan
3. Choose which file types to organize
4. Pick where to put organized files
5. Click "Start Sorting"

## Supported files

- **Photos**: .jpg, .jpeg, .png, .gif, .bmp, .tiff, .webp
- **Videos**: .mp4, .avi, .mov, .wmv, .flv, .mkv, .m4v

## Run from source

```bash
pip install pillow
python main.py
```

## Folder structure

```
Organized/
├── 2023/
│   └── 12/
│       └── 25/
│           ├── photo1.jpg
│           └── video1.mp4
├── 2024/
│   ├── 01/
│   │   └── 15/
│   └── 06/
│       └── 30/
```

## Notes

- Works offline
- Original files stay where they are
- Handles duplicate names
- Shows progress as it works

---

*Made to clean up mess.*
