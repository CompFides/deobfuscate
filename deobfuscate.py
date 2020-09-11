#!/usr/bin/python
# deobfuscate v1.1
# Copyright 2020 by CompFides
# MIT License
# Decodes stdin or file(s) obfuscated with multiple layers of encodings

# Change Log v1.1
# Changed to iterating a dictionary of regexes for searches and substitutions

import argparse
from collections import OrderedDict
from glob import glob
import os
import re
import sys

APPEND = '_dbfsctd'

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--lowercase', action='store_true', help='converts output to all lowercase')
parser.add_argument('-p', '--plus', action='store_true', help='removes plus signs from output')
parser.add_argument('-i', '--input', nargs='*', type=str, default=sys.stdin, help='path to files(s) to be converted')
parser.add_argument('-o', '--output', nargs='?', type=str, help='path to output directory')
args = parser.parse_args()

def config_regexes():
    # define dictionary for regex searches

    # regexes = OrderedDict([("<regex>",  ('<re.compile flags>' , '<decoder>')), ...])
    # FYI:  4 escapes = 1 escape

    regexes = OrderedDict([\
        ("r'%([A-F0-9]{2})'", ('0', 'hex2ascii')), \
        ("r'&#x([A-F0-9]{2})(;)'", ('0', 'hex2ascii')), \
        # keep char(0xXX) before 0xXX, \xXX
        ("r'char\(0x([A-F0-9]{2,3})\)'", ('re.I', 'hex2ascii')), \
        ("r'[0|\\\\]x([A-F0-9]{2})'", ('re.I', 'hex2ascii')), \
        ("r'&#([0-9]{2,3})(;)'", ('re.I', 'dec2ascii')), \
        ("r'cha?r\(([0-9]{2,3})\)'", ('re.I', 'dec2ascii')), \
        ("r'cha?r\(((\d{2,3}),\s(\d{2,3},?\s?)+)\)'", ('re.I', 'dec2ascii')), \
        ("r'\\\\\\\\([0-7]+)'", ('re.I', 'octal2ascii')) \
        ])

    return regexes
# decoders
def hex2ascii(matchobj):
    ascii = chr(int(matchobj.group(1),16))
    return ascii

def dec2ascii(matchobj):
    ascii = ''
    # check for single code or list
    if ((matchobj.group(1)).find(',')):
        # extract list of codes
        list = matchobj.group(1).split(",")
        # loop list and convert
        for item in list:
            ascii += chr(int(item))
    else:
        ascii = chr(int(matchobj.group(1)))
    return ascii

def octal2ascii(matchobj):
    ascii = ''.join(chr(int(matchobj.group(1)[i:i+2], 8)) for i in range(0, len(matchobj.group(1)), 2))
    return ascii

def dispatch_decoder(line, regexes):
    # searches line for regex patterns and sends matches to appropriate decoder function
    # line - the line being processed

    obfuscated = True
    not_found = 0
    while obfuscated:
        for regex, config in regexes.items():
            if re.compile(eval(regex), flags=eval(config[0])).search(line):
                line = re.compile(eval(regex), flags=eval(config[0])).sub(eval(config[1]), line)
            else:
                not_found += 1
        # check whether to exit
        if not_found == len(regexes.keys()):
            obfuscated = False
        # reset not_found
        else:
            not_found = 0
    # remove plus signs
    if args.plus:
        line = re.sub(r'\+', ' ', line)
    # convert to lower case
    if args.lowercase:
        line = line.lower()
    return(line)

def main():

    # create dictionary of regexes
    regexes = config_regexes()

    # sys.stdin
    if not sys.stdin.isatty():
        input_line = str(sys.stdin.readlines())[2:-4]
        output_line = dispatch_decoder(input_line, regexes)
        sys.stdout.write(output_line)

    # file(s) or wildcards
    elif args.input:
        input_file_names = []
        for arg in args.input:
            # test for directory
            if os.path.isdir(arg):
                arg = os.path.join(os.path.dirname(os.path.realpath(__file__)), arg, '*')
            input_file_names += glob(arg)
        # iterate file names
        for input_file_name in input_file_names:
            input_file = open(input_file_name,"r")
            # construct path and output file name
            if args.output:
                f_name, f_ext = os.path.splitext(input_file_name)
                output_file_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), args.output, f_name + APPEND + f_ext)
                if not os.path.exists(os.path.dirname(output_file_name)):
                    os.makedirs(os.path.dirname(output_file_name))
                output_file = open(output_file_name, "w")
            # iterate file lines
            for input_line in input_file:
                output_line = dispatch_decoder(input_line, regexes)
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
