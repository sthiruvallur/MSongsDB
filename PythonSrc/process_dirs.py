import os
import fnmatch

for root, dir, files in os.walk("."):
    print "Processing directory {0}".format(root)
    print ""
    for items in fnmatch.filter(files, "*"):
        print "processing song {0}".format(items)
    print ""
