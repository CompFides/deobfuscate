# deobfuscate
Converts files obfuscated with multiple layers of encodings, to ascii<br>
Also Contains a custom Splunk searchcommand that deobfuscates event streams.<br>

#### supported encodings:
%XX<br>
&#xXX<br>
0xXX<br>
\\xXX<br>
&#XX<br>
char(0xXX)<br>
chr(XX)<br>
char(XXX)<br>
char(XXX,XXX,...)<br>
\\\\XXX...<br>


#### options
-l --lowercase convert output to lowercase<br>
-p --plus remove plus signs from output<br>
-i --input path <br>
-o --output path<br>

## Custom Splunk Search Command
###Installation
##### Create an App in the Splunk Web Interface
Click on "Apps" > "Manage Apps"<br>
Click on "Create app"<br>

##### Fill in the following
Name: deobfuscate<br>
Folder name: deobfuscate<br>
Click on "Save"<br>

##### Copy deobfuscate.py
> cp ./bin/deobfuscate.py $SPLUNK_HOME/etc/apps/deobfuscate/bin/<br>

##### Copy commands.conf 
>cp ./default/commands.conf $SPLUNK_HOME/etc/apps/deobfuscate/default/<br>

#### Install splunk-sdk
##### Move to deobfuscate bin directory
>cd $SPLUNK_HOME/etc/apps/deobfuscate/bin/<br>

##### Install splunk-sdk 
>pip3 install -t . splunk-sdk

#### Restart Splunk
Click on "Settings" > "Server controls"<br>
Click on "Restart Splunk"<br>

### Usage
Pipe a search to deobfuscate
>index = "main" sourcetype = "access_combined" (select OR insert OR cast) | deobfuscate

