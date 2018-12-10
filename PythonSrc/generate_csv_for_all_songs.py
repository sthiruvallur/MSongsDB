"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

Code to quickly see the content of an HDF5 file.

This is part of the Million Song Dataset project from
LabROSA (Columbia University) and The Echo Nest.


Copyright 2010, Thierry Bertin-Mahieux

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
import hdf5_getters
import numpy as np
import pdb
import csv
import uuid
import fnmatch


def die_with_usage():
    """ HELP MENU """
    print 'display_song.py'
    print 'T. Bertin-Mahieux (2010) tb2332@columbia.edu'
    print 'to quickly display all we know about a song'
    print 'usage:'
    print '   python display_song.py [FLAGS] <HDF5 file> <OPT: song idx> <OPT: getter>'
    print 'example:'
    print '   python display_song.py mysong.h5 0 danceability'
    print 'INPUTS'
    print '   <HDF5 file>  - any song / aggregate /summary file'
    print '   <song idx>   - if file contains many songs, specify one'
    print '                  starting at 0 (OPTIONAL)'
    print '   <getter>     - if you want only one field, you can specify it'
    print '                  e.g. "get_artist_name" or "artist_name" (OPTIONAL)'
    print 'FLAGS'
    print '   -summary     - if you use a file that does not have all fields,'
    print '                  use this flag. If not, you might get an error!'
    print '                  Specifically desgin to display summary files'
    sys.exit(0)

def get_data_row(h5, getters, song_idx):
   data_row=[]
   header_row=[]
   for getter in getters:
      try:
         #if getter == "get_artist_mbtags" or getter == "get_artist_mbtags_count" :
         if getter == "get_artist_mbtags":
            continue   
         res = hdf5_getters.__getattribute__(getter)(h5,song_idx)
      except AttributeError, e:
         if summary:
            continue
         else:
            print e
            print 'forgot -summary flag? specified wrong getter?'
      if res.__class__.__name__ == 'ndarray':
         #print getter[4:]+": shape =",res.shape
         rows = res.shape[0]
         #cols = 0
         #if len(res.shape) != 1:
         #   cols = res.shape[1]
         #data_row += "ndarray rows=" + str(rows) + " cols=" + str(cols) + ","
      else:
         data_row.append( str(res) )
         header_row.append( getter[4:] )
         #data_row += str(res) + ","
         #header_row += getter[4:] + ","
   
   # done
   #data_row = data_row[:-1] + "\n"
   #header_row = header_row[:-1] + "\n"
   return (header_row, data_row)

def process_song(onegetter, song_file, csv_writer,genre):
    h5 = hdf5_getters.open_h5_file_read(song_file)
    numSongs = hdf5_getters.get_num_songs(h5)
    
    getters = filter(lambda x: x[:4] == 'get_', hdf5_getters.__dict__.keys())
    getters.remove("get_num_songs") # special case
    if onegetter == 'num_songs' or onegetter == 'get_num_songs':
        getters = []
    elif onegetter != '':
        if onegetter[:4] != 'get_':
            onegetter = 'get_' + onegetter
        try:
            getters.index(onegetter)
        except ValueError:
            print 'ERROR: getter requested:',onegetter,'does not exist.'
            h5.close()
            sys.exit(0)
        getters = [onegetter]
    getters = np.sort(getters)

    for song_idx in range(numSongs):
       header_row, data_row = get_data_row(h5, getters, song_idx)
       data_row.append(genre)
       #if(song_idx == 0 ):
          #csv_writer.writerow(header_row)
       csv_writer.writerow(data_row)
    h5.close()

def process_files(genreDict, onegetter, csv_writer):
    for root, dir, files in os.walk("."):
        print "Processing directory {0}".format(root)
        #print ""
        for song_file in fnmatch.filter(files, "*"):
            if "_summary" in song_file or "song.csv" in song_file:
                print("Skipping file {0}".format(song_file))
                continue
            song_basename = os.path.splitext(song_file)[0]
            song_basename_trim = song_basename.strip()
            if song_basename_trim not in genreDict:
                continue
                #print ("Skipping file {0} since it is not present in genreDict".format(song_basename_trim))
            genre = str(genreDict[song_basename_trim])
            song_file_path = str(root) + "/" +  str(song_file)
            #print "processing song {0}".format(song_file_path)
            process_song(onegetter, song_file_path, csv_writer, genre)
        #print ""

def construct_genre_dict(filename):
    genreDict = {}
    with open(filename) as csv_file:
       csv_reader = csv.reader(csv_file, delimiter=',')
       line_count = 0
       for row in csv_reader:
          if line_count == 0:
             #print("Column names are {0}".format(", ".join(row)))
             line_count += 1
          else:
             track_id = str(row[1]).strip()
             genre    = str(row[2]).strip()
             genreDict[track_id] = genre
             #print("\tTrack id={0} and Genre={1}".format(track_id, genre))
             line_count += 1
    print("Done going through contents of the file")
    return genreDict


if __name__ == '__main__':
    """ MAIN """

    # help menu
    if len(sys.argv) < 2:
        die_with_usage()

    # flags
    summary = False
    while True:
        if sys.argv[1] == '-summary':
            summary = True
        else:
            break
        sys.argv.pop(1)

    # get params
    hdf5path = sys.argv[1]
    songidx = 0
    if len(sys.argv) > 2:
        songidx = int(sys.argv[2])
    onegetter = ''
    if len(sys.argv) > 3:
        onegetter = sys.argv[3]

    genreDict = construct_genre_dict("msd-topMAGD-genreAssignment.csv")
    print("Number of keys = {0}".format(len(genreDict)))
   
    # sanity check
    #if not os.path.isfile(hdf5path):
    #    print 'ERROR: file',hdf5path,'does not exist.'
    #    sys.exit(0)
    #h5 = hdf5_getters.open_h5_file_read(hdf5path)
    #numSongs = hdf5_getters.get_num_songs(h5)
    #if songidx >= numSongs:
    #    print 'ERROR: file contains only',numSongs
    #    h5.close()
    #    sys.exit(0)

    #pdb.set_trace()
    # get all getters
    #getters = filter(lambda x: x[:4] == 'get_', hdf5_getters.__dict__.keys())
    #getters.remove("get_num_songs") # special case
    #if onegetter == 'num_songs' or onegetter == 'get_num_songs':
    #    getters = []
    #elif onegetter != '':
    #    if onegetter[:4] != 'get_':
    #        onegetter = 'get_' + onegetter
    #    try:
    #        getters.index(onegetter)
    #    except ValueError:
    #        print 'ERROR: getter requested:',onegetter,'does not exist.'
    #        h5.close()
    #        sys.exit(0)
    #    getters = [onegetter]
    #getters = np.sort(getters)

    # print them
    unique_id = str(uuid.uuid4())
    filename = "song.csv" + unique_id
    csv_file = open(filename, "a")
    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    
    print("Starting to populate the CSV for {0} songs in this file".format(filename))
    #pdb.set_trace()
    process_files(genreDict, onegetter, csv_writer)
    
    #for song_idx in range(numSongs):
       #header_row, data_row = get_data_row(getters, song_idx)
       #if(song_idx == 0 ):
       #   csv_writer.writerow(header_row)
       #csv_writer.writerow(data_row)
       #break

    # done
    csv_file.close()
    #h5.close()
    
