#!/usr/bin/python
# deobfuscate custom search app for splunk v1.1
# Copyright 2020 by CompFides
# MIT License
# deobfuscate splunk custom search app

from collections import OrderedDict
import sys
import re
from splunklib.searchcommands import dispatch, StreamingCommand, Configuration

@Configuration()

class deobfuscate(StreamingCommand):
    # searches _raw for regex patterns and replaces matches with ascii

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

    def stream(self, events):

        # searches line for regex patterns and replaces matches with ascii
        # events - the events being processed

        # declare variables for regex searches
        # regexes = OrderedDict([("<regex>", ('<re.compile flags>' , '<decoder>')), ...])

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

        for event in events:
            obfuscated = True
            not_found = 0
            while obfuscated:
                for regex, config in regexes.items():
                    if re.compile(eval(regex), flags=eval(config[0])).search(event['_raw']):
                        event['_raw'] = re.compile(eval(regex), flags=eval(config[0])).sub(eval(config[1]), event['_raw'])
                    else:
                        not_found += 1
                # check whether to exit
                if not_found == len(regexes.keys()):
                    obfuscated = False
                # reset not_found
                else:
                    not_found = 0
            # remove plus signs
            event['_raw'] = re.sub(r'\+', ' ', event['_raw'])
            # convert to lower case
            event['_raw'] = event['_raw'].lower()
            yield event


if __name__ == "__main__":
    dispatch(deobfuscate, sys.argv, sys.stdin, sys.stdout, __name__)