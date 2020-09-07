# deobfuscate
Converts files obfuscated with multiple layers of encodings, to ascii<br>

##supported encodings:
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


## options
-l --lowercase convert output to lowercase<br>
-p --plus remove plus signs from output<br>
-i --input path to source files(s)<br>
-o --output path to output directory

### examples
capture stdin and output to stdout<br>
    cat apache.log | deobfuscate.py<br>
<br>
process an entire directory of files with the extensiton .log and output to local directory dbfcctd<br>
  note: filenames with be appended with '_dbfsctd' but will retain their original extensions<br>     
    deobfuscate -i ./path/to/files/*.log -o ./dbfctd/ 

