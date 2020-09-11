# deobfuscate
Decodes stdin or file(s) obfuscated with multiple layers of encodings to ascii.<br>
Output file names are appended with '_dbfsctd' to prevent overwriting originals.<br>
Project has also been ported to a Splunk custom search app.<br>

#### supported encodings

encoding | regex
-------- | ------
%XX | %([A-F0-9]{2})
&#xXX | &#x([A-F0-9]{2})(;)
0xXX | [0&#124;\\\\]x([A-F0-9]{2})
\\xXX | [0&#124;\\\\]x([A-F0-9]{2}
&#XX; | &#([0-9]{2,3})(;)
char(0xXX) | char\(0x([A-F0-9]{2,3})\)
chr(XXX) | cha?r\(([0-9]{2,3})\)
char(XXX) | cha?r\(([0-9]{2,3})\)
char(XXX,XXX,...) | cha?r\(((\d{2,3}),\s(\d{2,3},?\s?)+)\)
\\\\XXX... | \\\\\\\\([0-7]+)


#### options
-l --lowercase convert output to lowercase<br>
-p --plus remove plus signs from output<br>
-i --input path <br>
-o --output path<br>
#### examples
capture stdin and output to stdout<br>
> cat log.txt | deobfuscate.py

process file.ext and output to stdout<br>
> deobfuscate.py -i file.ext

process all *.ext files in ./file/location/ and output to ./output/<br>
> deobfuscate.py -i ./file/location/*.ext -o ./output/<br>

## Splunk Custom Search Command
### Installation
#### Create an App via the Splunk Web Interface
Click **Apps** > **Manage Apps**<br>
Click **Create app**<br>

#### Configure app
**Name:** deobfuscate<br>
**Folder name:** deobfuscate<br>
**Visible:** **No**<br>
**Template:** barebones<br>
Click **Save**<br>

#### Configure app permissions
Click **Permissions** link for the deobfuscate app <br>
Check to ensure **Everyone** role has **"Read"** permissions<br>
**Apply selected role permissions to:** select **All apps (system)**<br>
Click **"Save"**<br>

#### Copy deobfuscate_splunk.py
>cp ./deobfuscate/splunk/bin/deobfuscate_splunk.py $SPLUNK_HOME/etc/apps/deobfuscate/bin/<br>

#### Copy commands.conf 
>cp ./deobfuscate/splunk/default/commands.conf $SPLUNK_HOME/etc/apps/deobfuscate/default/<br>

#### Move to deobfuscate bin directory
>cd $SPLUNK_HOME/etc/apps/deobfuscate/bin/<br>

#### Install splunk-sdk to bin directory
>pip3 install -t . splunk-sdk

#### Restart Splunk
Click **Settings** > **Server controls**<br>
Click **Restart Splunk**<br>

### Usage
Pipe a search to deobfuscate
>index = "main" sourcetype = "access_combined" (select OR insert OR cast) | deobfuscate

