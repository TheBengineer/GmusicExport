# GmusicExport
This program sorts music uploaded to Google Play Music, and exported from YouTube Music, using Takeout.
It uses the metadata from the csv file to sort the music into folders by Artist/Album on a best-guess basis.

## Steps:
1. Request your data from Google Takeout here:
   1. https://takeout.google.com/settings/takeout?pli=1
   2. Export from YouTube Music
      ![export1.PNG](images%2Fexport1.PNG)
   3. Select only music related exports
      ![export2.PNG](images%2Fexport2.PNG)
      ![export3.PNG](images%2Fexport 3.PNG)

2. Download your music from Google Takeout
3. Install Python 3.8+ (Tested with 3.8, 3.9.5, 3.11.0, 3.12.0)
4. Run `main.py` at least twice. Each run through will catch more files. 
   1. Between runs, you can add mp3 tags to the remaining files to help the program identify them. 
   2. You may also want to clean up the artists and albums in your `music-uploads-metadata.csv` file.
5. Enjoy your sorted music!
