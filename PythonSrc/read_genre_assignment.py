import csv

genreDict = {}
with open('msd-topMAGD-genreAssignment.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            print("Column names are {0}".format(", ".join(row)))
            line_count += 1
        elif line_count == 20:
            break
        else:
            track_id = str(row[1]).strip()
            genre    = str(row[2]).strip()
            genreDict[track_id] = genre
            print("\tTrack id={0} and Genre={1}".format(track_id, genre))
            line_count += 1
print("Done going through contents of the file")
print("The genre for track id=TRAAAGW12903CC1049 is {0}".format(genreDict["TRAAAGW12903CC1049"]))
if "TRAAAGW12903CC104X" not in genreDict:
    print "Key not present"
else:
    print "Key present"
