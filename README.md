# CSE545_filescanner
Team 2 group project.
##Goal
Scan all files in a given directory to find the plain text flag and return. This tool will handle the following scenarios:
* data file - try decoding with base64
* ASCII text file - return back the string
* Compressed file - recursively decompress until a data/text file is found.
