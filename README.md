# Overview

`tree-tracker` creates records of the tree structure (files and metadata) in a given directory, and can create that structure in a given target directory (only empty files ofc).

# Building

## Linux

1. Create .venv `python -m venv .venv`
2. Enter .venv `source .venv/bin/activate`
3. Install dependencies `pip install -r requirements.txt`
4. Run installer `pyinstaller --onefile main.py`
5. Executable will be located in `dist`

## Windows

Same as above, but need to use `.\.venv\Scripts\activate` in step 2
