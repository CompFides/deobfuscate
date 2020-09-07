# deobfuscate
Converts input obfuscated with multiple layers of encodings, to ascii<br>
Handles stdin, file and directory names 

### supported encodings
%XX - base16<br>
&#xXX - base16<br>
0xXX - base16<br>
\\xXX - base16<br>
&#XX - base10<br>
char(0xXX) - base10<br>
chr(XX) - base10<br>
char(XXX) - base10<br>
char(XXX,XXX,...) - base10<br>
\\\\XXX... - base8<br>

### options
-l --lowercase convert output to lowercase<br>
-p --plus remove plus signs from output<br>
-i --input input path<br>
-o --output output path<br>

### examples
send contents of log.file via stdin and output to results.txt<br>
>cat log.file | deobfuscate.py >> results.txt<br>

process ./logs/*.log files and output to ./dbfctd/<br>
>deobfuscate.py -i ./logs/*.log -o ./dbfctd/<br>
