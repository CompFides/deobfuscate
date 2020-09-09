#!/usr/bin/python
# deobfuscate custom search app for splunk v1.0
# Copyright 2020 by CompFides
# MIT License
# deobfuscate splunk custom search app

import sys
import re
from splunklib.searchcommands import dispatch, StreamingCommand, Configuration

@Configuration()

class deobfuscate(StreamingCommand):
    # searches _raw for regex patterns and replaces matches with ascii

    def urlhex2ascii(self, matchobj): # %XX or &#xXX;
        return chr(int(matchobj.group(1), 16))

    def urldec2ascii(self, matchobj): # &#XX
        return chr(int(matchobj.group(1)))

    def char0xXX2ascii(self, matchobj): # char(0xXX)
        return chr(int(matchobj.group(1)))

    def char2ascii(self, matchobj): # chr(XX) char(XXX) char(XXX,XXX,...)
        ascii = ''
        # check to for single code or list
        if not ((matchobj.group(1)).find(',')):
            ascii = chr(int(matchobj.group(1)))
        else:
            # extract list of codes
            thelist = matchobj.group(2).split(",")
            # loop list and convert
            for theitem in thelist:
                ascii += chr(int(theitem))
        return ascii

    def octal2ascii(self, matchobj): # \\XXX...
        return ''.join(chr(int(matchobj.group(2)[i:i + 2], 8)) for i in range(0, len(matchobj.group(2)), 2))

    def hex2ascii(self, matchobj): # 0xXX \xXX
        return ''.join(chr(int(matchobj.group(2)[i:i + 2], 16)) for i in range(0, len(matchobj.group(2)), 2))

    def stream(self, events):

        # declare variables for regex searches
        urlhex = re.compile(r'%([a-f0-9]{2,2})', flags=re.I) # %XX
        urlhex2 = re.compile(r'&#x([a-f0-9]{2,2})(;)', flags=re.I) # &#xXX;
        hexstr = re.compile(r'([0|\\]x)([a-f0-9]+)', flags=re.I)  # 0xXX..., \xXX...
        urldec = re.compile(r'&#([0-9]{2,3})', flags=re.I) # &#XX
        char0xXX = re.compile(r'\bchar\(0x([a-f0-9]{2,3})\)', flags=re.I) # char(0xXX)
        charXXX = re.compile(r'\b(cha?r)\(([0-9]{2,3})(,\s*\d+)*\)', flags=re.I) # chr(XX), char(XXX), char(XX,XXX,...)
        octal = re.compile(r'\\\\([0-7]+)', flags=re.I) # \\XXX...

        for event in events:
            obfuscated = True
            while obfuscated:
                if urlhex.search(event['_raw']):
                    event['_raw'] = urlhex.sub(self.urlhex2ascii, event['_raw'])
                elif urlhex2.search(event['_raw']):
                    event['_raw'] = urlhex2.sub(self.urlhex2ascii, event['_raw'])
                elif hexstr.search(event['_raw']):
                    event['_raw'] = hexstr.sub(self.hex2ascii, event['_raw'])
                elif urldec.search(event['_raw']):
                    event['_raw'] = urldec.sub(self.urldec2ascii, event['_raw'])
                elif char0xXX.search(event['_raw']):
                    event['_raw'] = char0xXX.sub(self.char0xXX2ascii, event['_raw'])
                elif charXXX.search(event['_raw']):
                    event['_raw'] = charXXX.sub(self.char2ascii, event['_raw'])
                elif octal.search(event['_raw']):
                    event['_raw'] = octal.sub(self.octal2ascii, event['_raw'])
                else:
                    obfuscated = False
                # remove plus signs
                event['_raw'] = re.sub(r'\+', '', event['_raw'])
                # convert to lower case
                event['_raw'] = event['_raw'].lower()
            yield event

if __name__ == "__main__":
    dispatch(deobfuscate, sys.argv, sys.stdin, sys.stdout, __name__)