#! /usr/bin/python3

import argparse
import logging
import os
from re import S, sub
import subprocess
from tkinter import W
import tarfile

def decode_file(filename, scanres, path):
    '''
    If file is plain text, return text. 
    If file is encoded, try decoding using base64
    If file is compressed, try decompress using various tools
    '''
    if (scanres == filename):
        return
    logging.info("scanning filename=%s", filename)
    result = subprocess.run(["file", "--mime", filename], stdout=subprocess.PIPE)
    logging.debug("file --mime %s", result.stdout.decode(encoding="utf-8"))
    if (b"text/plain" in result.stdout):
        logging.info("byte string")

        with open(filename, 'r') as srcfile, open(scanres, 'a') as destfile:
            if not path:
                destfile.write(filename + "(raw)\n")
            else:
                destfile.write(path+filename + "(raw)\n")
            lineno = 0
            for line in srcfile:
                if lineno > 0:
                    logging.warning("multiple lines detected, only sampling first line")
                    break
                lineno += 1
                destfile.write(line + "\n")

        logging.debug("Checking whether the file is base64 encoded")
        base64_result = subprocess.run(["base64", "--decode", filename], stdout=subprocess.PIPE)
        if base64_result.stdout: 
            with open(scanres, 'ab') as destfile:
                destfile.write(bytes(path + " -> " if path else "" + filename + " base64 encoded\n", encoding='utf-8'))
                destfile.write(base64_result.stdout)
        else:
            logging.debug("not base64")

        logging.debug("Try hexdump -r")
        tmpfilename = filename + "_tmp"
        with open(tmpfilename, 'wb') as tmphexdump:
            hexres = subprocess.run(["xxd", "-r", filename], stdout=subprocess.PIPE)
            tmphexdump.write(hexres.stdout)
        decode_file(tmpfilename, scanres, path + tmpfilename+ "(hexdump) -> ")
        subprocess.run(["rm", tmpfilename], stdout=subprocess.PIPE)

    elif b"gzip" in result.stdout:
        logging.info("gzip file")
        newfilename = filename + "_tmp"
        subprocess.run(["mv", filename, newfilename + ".gz"], stdout=subprocess.PIPE)
        res = subprocess.run(["gzip", "-d", newfilename+".gz"], stdout=subprocess.PIPE)
        decode_file(newfilename, scanres, path + newfilename + "(gzip) -> ")
        logging.debug("removing tmp file %s", newfilename)
        subprocess.run(["rm", newfilename], stdout=subprocess.PIPE)
    
    elif b"bzip" in result.stdout:
        logging.info("bzip file")
        res = subprocess.run(["bzip2", "-d", filename], stdout=subprocess.PIPE)
        decode_file(filename+".out", scanres, path+filename+".out" + "(bzip) -> ")
        logging.debug("removing tmp file %s", filename+".out")
        subprocess.run(["rm", filename + ".out"], stdout=subprocess.PIPE)

    elif b"tar" in result.stdout:
        logging.info("tar ball")
        with tarfile.open(filename) as tar:
            for name in tar.getnames():
                logging.debug("extracting %s", name)
                tar.extract(name)
                decode_file(name, scanres, path+name+"(tar) -> ")

            for name in tar.getnames():
                subprocess.run(["rm", name], stdout=subprocess.PIPE)


    else:
        logging.debug("unrecognized file format " + filename)


        
def scan_dir(dir, res):
    '''
    scanning all files in given directory
    '''
    objs = os.scandir(dir)
    logging.info("Start scanning: dir=%s", dir)

    for obj in objs:
        logging.debug("obj=%s", obj.name)
        if obj.is_dir():
            logging.debug("Sub dir found: name=%s", obj.name)
            scan_dir(obj.path)
        elif obj.is_file():
            logging.debug("File object found: name=%s", obj.name)
            decode_file(obj.path, res, "")
        else:
            logging.warning("Unrecogonized file object: name=%s", obj.path)
            pass

    objs.close()

def start():
    '''
    Start scanning the given directory and find any plain text string to return in a list
    '''
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d:%H:%M:%S')
    parser = argparse.ArgumentParser(description="input args")
    parser.add_argument("--dir", 
                        metavar="directory",
                        required=False, 
                        default="./",
                        help = "directory to scan (default='./')")

    parser.add_argument("--res", 
                        metavar="result filename",
                        required=False, 
                        default="./scan_result.txt",
                        help = "scanning result")
    args = parser.parse_args()

    logging.info("Scanner started in dir=%s", args.dir)
    scan_dir(args.dir, args.res)



if __name__=="__main__":
    start()