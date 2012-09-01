# ISBN Android Cataloguing

This is a SL4A (Scripting Layer for Android) script that I used for cataloguing
my personal book library.

It scans a barcode, looks it up with the http://xisbn.worldcat.org/xisbnadmin/doc/api.htm api, and stores the information in a text file.

## Installation

+ Move the isbn.py and lookup.py scripts to the SL4A folder on your phone (mine
  is /sdcard/sl4a/scripts/

## Usage

+ Execute isbn.py

+ Print out the exit_code.png image. You scan that to exit the script.

+ The results of the catalog are stored in the same folder as isbn.py, and the
  file is called books.txt

## Known Issues

+ If the metadata of a book contains non-ascii characters, the script breaks
  when it tries to write to the catalog (fh.write()). The solution, I think, is
  to encode everything in unicode. I'm not sure what type of encoding the API
  is using. The error that is being raised is "UnicodeEncodeError".

+ I've had issues with certain books in the past. I don't remember which
  barcode format it was, but certain older formats are not scanned correctly by
  my phone's scanner, which causes the API query to fail. Maybe this is a
  result of my ignorance on barcode types. I left a "convert" function, that
  currently just returns the barcode that it is passed. It also takes a barcode
  format argument, which is coming from the phone's barcode scanner. This could
  be used to make the necessary conversions so that the API query won't fail.

+ Occasionally, when trying to scan the exit_code.png barcode, my phone picks
  up an EAN_8 barcode with some strange number.
