# CSE545_filescanner
Team 2 group project.
##Goal
Scan all files in a given directory to find the plain text flag and return. This tool will handle the following scenarios:
* Plain text (trivial)
* base64 encoded text
* Hexdump of gzip/bzip2/tar (recursively decompress until a data/text file is found)

## how to use
under the directory where interested files are collected, run
```python
python3 scanner.py --dir="dir/where/files/to/be/decoded" --res="res.txt"
```
