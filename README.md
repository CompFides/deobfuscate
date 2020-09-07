# deobfuscate
Converts files obfuscated with multiple layers of encodings, to ascii<br>
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
-i --input path to source files(s)<br>
-o --output path to output directory