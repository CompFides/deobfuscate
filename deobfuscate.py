#!/usr/bin/python

# deobfuscate v1.2
# Copyright 2020 by CompFides
# MIT License
# Decodes stdin or file(s) obfuscated with multiple layers of encodings

# Change Log v1.2
# Now with OBJECTS!

import argparse
from collections import OrderedDict
from glob import glob
import os
import re
import sys

APPEND = '_dbfsctd'


# Obfuscated object class
class Obfuscated:
    def config_regexes(self):
        # define dictionary of regexes, flags, and docoders
        # ("<regex>",  ('<re.compile flags=>' , '<decoder>')), ...
        # FYI:  4 escapes = 1 escape
        regexes = OrderedDict([ \
            ("r'%([A-F0-9]{2})'", ('0', 'self.hex2ascii')), \
            ("r'&#x([A-F0-9]{2})(;)'", ('0', 'self.hex2ascii')), \
            # keep char(0xXX) before 0xXX, \xXX
            ("r'char\(0x([A-F0-9]{2,3})\)'", ('re.I', 'self.hex2ascii')), \
            ("r'[0|\\\\]x([A-F0-9]{2})'", ('re.I', 'self.hex2ascii')), \
            ("r'&#([0-9]{2,3})(;)'", ('re.I', 'self.dec2ascii')), \
            ("r'cha?r\(([0-9]{2,3})\)'", ('re.I', 'self.dec2ascii')), \
            ("r'cha?r\(((\d{2,3}),\s(\d{2,3},?\s?)+)\)'", ('re.I', 'self.dec2ascii')), \
            ("r'\\\\\\\\([0-7]+)'", ('re.I', 'self.octal2ascii')) \
            ])
        return regexes

    # decoders
    def hex2ascii(self, matchobj):
        ascii = chr(int(matchobj.group(1), 16))
        return ascii

    def dec2ascii(self, matchobj):
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

    def octal2ascii(self, matchobj):
        ascii = ''.join(chr(int(matchobj.group(1)[i:i + 2], 8)) for i in range(0, len(matchobj.group(1)), 2))
        return ascii

    # dispatcher
    def dispatcher(self, line, regexes, lower, plus):
        # searches line for regex patterns and sends matches to appropriate decoder function
        # line - the line being processed
        # regexes - dictionary of search and substitution regexes

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
        if lower:
            line = line.lower()
        if plus:
            line = re.sub(r'\+', ' ', line)
        return (line)

    def deobfuscate(self, line, lower, plus):
        regexes = self.config_regexes()
        return self.dispatcher(line, regexes, lower, plus)

# configure argparser
def load_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help='enable debugging')
    parser.add_argument('-l', '--lowercase', action='store_true', default='False', help='converts output to lowercase')
    parser.add_argument('-p', '--plus', action='store_true', default='False', help='removes + from output')
    parser.add_argument('-i', '--input', nargs='*', type=str, default=sys.stdin, help='file or path to files(s)')
    parser.add_argument('-o', '--output', nargs='?', type=str, help='path to output directory')
    return parser.parse_args()

def handle_stdin(args):
    source = Obfuscated()
    input_line = str(sys.stdin.readlines())[2:-4]
    output_line = source.deobfuscate(input_line, args.lowercase, args.plus)
    sys.stdout.write(output_line)

def handle_files(args):
    source = Obfuscated()
    input_file_names = []
    for arg in args.input:
        # test for directory
        if os.path.isdir(arg):
            arg = os.path.join(os.path.dirname(os.path.realpath(__file__)), arg, '*')
        input_file_names += glob(arg)
    # iterate file names
    for input_file_name in input_file_names:
        input_file = open(input_file_name, "r")
        # construct path and output file name
        if args.output:
            f_name, f_ext = os.path.splitext(input_file_name)
            output_file_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), args.output, f_name + APPEND + f_ext)
            if not os.path.exists(os.path.dirname(output_file_name)):
                os.makedirs(os.path.dirname(output_file_name))
            output_file = open(output_file_name, "w")
        # iterate file lines
        for input_line in input_file:
            output_line = source.deobfuscate(input_line, args.lowercase, args.plus)
            # output to destination
            if args.output:
                output_file.write(output_line)
            else:
                sys.stdout.write(output_line)
        # close files
        input_file.close()
        if args.output:
            output_file.close()

def main():
    args = load_arguments()

    # sys.stdin
    if not sys.stdin.isatty():
        handle_stdin(args)
    # file(s) or wildcards
    elif args.input:
        handle_files(args)
    else:
        print("something went wrong!  no input detected")

if __name__ == '__main__':
     main()
