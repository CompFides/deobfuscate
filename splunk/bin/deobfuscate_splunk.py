#!/usr/bin/python
# deobfuscate custom search app for splunk v1.2
# Copyright 2020 by CompFides
# MIT License
# deobfuscate splunk custom search app

from deobfuscate import Obfuscated
import sys
from splunklib.searchcommands import dispatch, StreamingCommand, Configuration

@Configuration()

class deobfuscate(StreamingCommand):
    # searches _raw for regex patterns and replaces matches with ascii

    def stream(self, events):
        source = Obfuscated()
        lowercase = True
        plus = True
        for event in events:
            event['_raw'] = source.deobfuscate(event['_raw'], lowercase, plus)
            yield event

if __name__ == "__main__":
    dispatch(deobfuscate, sys.argv, sys.stdin, sys.stdout, __name__)