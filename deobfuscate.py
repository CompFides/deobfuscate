#!/usr/bin/python
# deobfuscate v1.0
# Copyright 2020 by CompFides
# MIT License
# Converts stdin or files, obfuscated with multiple layers of encodings, to ascii

import argparse
from glob import glob
import os
import re
import sys

APPEND = '_dbfsctd'

# configure argument parser
parser = argparse.ArgumentParser()
parser.add_argument('-l', '--lowercase', action='store_true', help='converts output to all lowercase')
parser.add_argument('-p', '--plus', action='store_true', help='removes plus signs from output')
parser.add_argument('-i', '--input', nargs='*', type=str, default=sys.stdin, help='path to files(s) to be deobfuscated')
parser.add_argument('-o', '--output', nargs='?', type=str, help='path to output directory')
args = parser.parse_args()

def urlhex2ascii(matchobj):  # %XX or &#xXX;
    return chr(int(matchobj.group(1),16))

def urldec2ascii(matchobj):  # &#XX
    return chr(int(matchobj.group(1)))

def char0xXX2ascii(matchobj):  # char(0xXX)
    return chr(int(matchobj.group(1)))

def char2ascii(matchobj):  # chr(XX), char(XXX), char(XXX,XXX,...)
    ascii = ''
    # check to for single code or list
    if not((matchobj.group(1)).find(',')):
        ascii = chr(int(matchobj.group(1)))
    else:
        # extract list of codes
        thelist = matchobj.group(2).split(",")
        # loop list and convert
        for theitem in thelist:
            ascii += chr(int(theitem))
    return ascii

def octal2ascii(matchobj):  # \\XXX...
    return ''.join(chr(int(matchobj.group(2)[i:i+2], 8)) for i in range(0, len(matchobj.group(2)), 2))

def hex2ascii(matchobj):  # 0xXX, \xXX
    return ''.join(chr(int(matchobj.group(2)[i:i+2], 16)) for i in range(0, len(matchobj.group(2)), 2))

def deobfuscate(the_line):
    # searches line for regex patterns and replaces matches with ascii
    # the_line - the line of text being processed

    # declare variables for regex searches
    urlhex = re.compile(r'%([a-f0-9]{2,2})', flags=re.I) # %XX
    urlhex2 = re.compile(r'&#x([a-f0-9]{2,2})(;)', flags=re.I) # &#xXX;
    hexstr = re.compile(r'([0|\\]x)([a-f0-9]+)', flags=re.I)  # 0xXX..., \xXX...
    urldec = re.compile(r'&#([0-9]{2,3})', flags=re.I) # &#XX
    char0xXX = re.compile(r'\bchar\(0x([a-f0-9]{2,3})\)', flags=re.I) # char(0xXX)
    charXXX = re.compile(r'\b(cha?r)\(([0-9]{2,3})(,\s*\d+)*\)', flags=re.I) # chr(XX), char(XXX), char(XX,XXX,...)
    octal = re.compile(r'\\\\([0-7]+)', flags=re.I) # \\XXX...

    obfuscated = True
    while obfuscated:
        if urlhex.search(the_line):
            the_line = urlhex.sub(urlhex2ascii, the_line)
        elif urlhex2.search(the_line):
            the_line = urlhex2.sub(urlhex2ascii, the_line)
        elif hexstr.search(the_line):
            the_line = hexstr.sub(hex2ascii, the_line)
        elif urldec.search(the_line):
            the_line = urldec.sub(urldec2ascii, the_line)
        elif char0xXX.search(the_line):
            the_line = char0xXX.sub(char0xXX2ascii, the_line)
        elif charXXX.search(the_line):
            the_line = charXXX.sub(char2ascii, the_line)
        elif octal.search(the_line):
            the_line = octal.sub(octal2ascii, the_line)
        else:
            obfuscated = False
        # remove plus signs
        if args.plus:
            the_line = re.sub(r'\+', '', the_line)
        # convert to lower case
        if args.lowercase:
            the_line = the_line.lower()
    return(the_line)

def main():

    # test for sys.stdin
    if not sys.stdin.isatty():
        input_line = str(sys.stdin.readlines())[2:-4]
        output_line = deobfuscate(input_line)
        sys.stdout.write(output_line)

    # file(s) | directory | wildcard
    elif args.input:
        input_file_names = []
        for arg in args.input:
            # test if arg is a directory
            if os.path.isdir(arg):
                arg = os.path.join(os.path.dirname(os.path.realpath(__file__)), arg, '*')
            input_file_names += glob(arg)
        # iterate file names
        for input_file_name in input_file_names:
            input_file = open(input_file_name,"r")
            # construct output file name
            if args.output:
                f_name, f_ext = os.path.splitext(input_file_name)
                output_file_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), args.output, f_name + APPEND + f_ext)
                # test if directory exists
                if not os.path.exists(os.path.dirname(output_file_name)):
                    # create directory
                    os.makedirs(os.path.dirname(output_file_name))
                output_file = open(output_file_name, "w")
            # iterate file lines
            for input_line in input_file:
                output_line = deobfuscate(input_line)
                # output to destination
                if args.output:
                    output_file.write(output_line)
                else:
                    sys.stdout.write(output_line)
            # close files
            input_file.close()
            if args.output:
                output_file.close()
    else:
        print("something went wrong!  no input detected")

if __name__ == '__main__':
     main()
