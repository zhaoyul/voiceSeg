# bintail.py -- reads a binary file, writes initial contents to stdout,
# and writes new data to stdout as it is appended to the file.

import time
import sys
import os

# Time to sleep between file polling (seconds)
sleep_int = 1

def main():
    # File is the first argument given to the script (bintail.py file)
    binfile = sys.argv[1]

    # Get the initial size of file
    fsize = os.stat(binfile).st_size

    # Read entire binary file
    h_file = open(binfile, 'rb')
    h_bytes = h_file.read(128)
    while h_bytes:
        sys.stdout.write(h_bytes)
        h_bytes = h_file.read(128)
    h_file.close()


    # Loop forever, checking for new content and writing new content to stdout
    while 1:
        current_fsize = os.stat(binfile).st_size
        if current_fsize > fsize:
            h_file = open(binfile, 'rb')
            h_file.seek(fsize)
            h_bytes = h_file.read(128)
            while h_bytes:
                sys.stdout.write(h_bytes)
                h_bytes = h_file.read(128)
            h_file.close()
            fsize = current_fsize
        time.sleep(sleep_int)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main()
    else:
        sys.stdout.write("No file specified.")

