# bitburnerSaveEditor

Save game editor for the excellent game https://danielyxie.github.io/bitburner/

Save games are base64 encoded json files. So this application just base64 decodes the content, parses the json, edits the relevant fields, and saves off the resulting data, and base64 encodes it again so it can be imported.
The game is fun and the challenge is automating various actions. 

I wrote this because I got frustrated on BitNode3. I finished BN1 and BN2 once each, and on BN3 worked up to getting to the point of installing the red pill and realizing that getting the necessary hack level with the existing augmentations and maxed out servers was going to take way too long. 

To export your save game, in the game, click "Options->Export Game", and then use the "Import Game" to import the modified save file.

There are currently just a couple of command line arguments: 
```bash
usage: bitburner_save_editor.py [-h] [-s SAVE | -d DIRECTORY] [--manual] [-v]
                                [-m]

Edit BitBurner Save game files

optional arguments:
  -h, --help            show this help message and exit
  -s SAVE, --save SAVE  Save game file
  -d DIRECTORY, --directory DIRECTORY
                        Save game directory (find latest version)
  --manual              Edit file contents manually
  -v, --verbose         Verbose prints
```

You can either specify the specific file to edit, or specify a directory that contains multiple saves. 
The `-d` option will find the latest save and use that.
By default, a cli menu will pop up and you can select the modifications you want to make.
EG:
```bash
> [ ] Max home pc resources                                                                                                                                                                                                                                                                                             
  [ ] Join all factions                                                                                                                                                                                                                                                                                                 
  [ ] Give player lots of money                                                                                                                                                                                                                                                                                          
  [ ] Change save game time                                                                                                                                                                                                                                                                                             
  [ ] Add stanek gift augmentations                                                                                                                                                                                                                                                                                     
  [ ] Set karma to -60000                                                                                                                                                                                                                                                                                               
  [ ] Enable stock market access                                                                                                                                                                                                                                                                                        
  [ ] Increase all experience stats                                                                                                                                                                                                                                                                                     
Press <space>, <tab> for multi-selection and <enter> to select and accept   
```

If you specify `--manual` the conversion to json is done and an `intermediate` file is written out that you can manually edit. Once you are done the program will re-encode the contents.

## Warning
Obviously use with caution, no guarantee that it will not corrupt your save game data. 
Additionally, the game maintainers are awesome and are constantly making changes, so this may not work in the future iterations of the game. I will probably only maintain this for as long as it keeps my attention, which will probably not be very long.


