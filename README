emwave2-export
==============

This python script dumps the contents of the HeartMath emWave2 database file into a JSON blob for each entry.  The script supports dumping of the user and sessions databases and performs all the necessary format conversions for BLOB fields into typed arrays.

The end goal is to support exporting of emWave2 heartrate variability (HRV) data to the host of other applications that can analyze it, including KubiosHRV.

Usage
-----

    emwave2-export.py [options] <embd file>

    Options:
      -h, --help  show this help message and exit
      -v          verbose output
      -m MODE     mode: session, user or version [default: session]
      -o OUTPUT   output file
      -s SESSION  session indices in format A,B,C-D,E,...