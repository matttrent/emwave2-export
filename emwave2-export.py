#!/usr/bin/env python
# encoding: utf-8
"""
emwave2-export.py

Created by Matthew Trentacoste on 2011-06-30.
Copyright (c) 2011 matttrent.com. All rights reserved.
"""

import os
import sys
import optparse
import json
import sqlite3
import struct

from sqlalchemy.ext.sqlsoup import SqlSoup

# ----------------------------------------------------------------------------

DB_VERSION = 9

MODES = ( 'user', 'session', 'version' )

usage = '''%prog [options] <embd file>'''

# ----------------------------------------------------------------------------

def session_set( session_str ):
    
    sessions = session_str.split(',')
    sessions2 = []
    
    for sess in sessions:
        parts = sess.split('-')
        if len( parts ) is 1:
            print parts
            sessions2 += [ int( parts[0] ) ]
        elif len( parts ) is 2:
            sessions2 += [ int( p ) for p in range( parts[0], parts[1]+1 ) ]
            
    sessions2 = set( sessions2 )
    return sessions2
    

def connect_db( filename ):
    
    db = SqlSoup( 'sqlite:///%s' % filename )
    
    return db

# ----------------------------------------------------------------------------

def read_user( db ):
    
    entries = []
    
    users = db.Client.all()
    for user in users:
        
        d = {}
        d['ClientRecID'] = user.ClientRecID
        d['FirstName']   = user.FirstName
        d['LastName']    = user.LastName
        d['DOB']         = user.DOB
        d['Sex']         = user.Sex
        d['Settings']    = user.Settings
        d['DateCreated'] = user.DateCreated
        d['DateUpdated'] = user.DateUpdated
        d['DefaultChallengeLevel'] = user.DefaultChallengeLevel
        d['Email']       = user.Email
        d['Password']    = user.Password
        d['ClientGroupId']  = user.ClientGroupId
        d['TimeCorrection'] = user.TimeCorrection
        d['BRecent']     = user.BRecent
        
        entries += [ d ]
        
    return entries
    
    
def read_session( db, sesslist=None ):
    
    entries = []
    
    sessions = db.PrimaryData.order_by( db.PrimaryData.DateCreated ).all()
    if sesslist is None:
        sesslist = range( len( sessions) )
        
    for i, sess in enumerate( sessions ):
        
        if i not in sesslist:
            continue
        
        d = {}
        d['TestRecID']      = sess.TestRecID
        d['ClientRecID']    = sess.ClientRecID
        d['DateCreated']    = sess.DateCreated
        d['LastModified']   = sess.LastModified
        d['Title']          = sess.Title
        d['Comment']        = sess.Comment
        d['CoreModuleVersion']  = sess.CoreModuleVersion
        d['SensorVersion']  = sess.SensorVersion
        d['ChallengeLevel'] = sess.ChallengeLevel
        d['PulseStartTime'] = sess.PulseStartTime
        d['PulseEndTime']   = sess.PulseEndTime
        d['IBIStartTime']   = sess.IBIStartTime
        d['IBIEndTime']     = sess.IBIEndTime
        d['ZoneEPStartTime']    = sess.ZoneEPStartTime
        d['ZoneEPEndTime']  = sess.ZoneEPEndTime
        d['PulseIntervalTime']  = sess.PulseIntervalTime
        d['IBIIntervalTime']    = sess.IBIIntervalTime
        d['EntrainmentIntervalTime']    = sess.EntrainmentIntervalTime
        d['PctMedium']      = sess.PctMedium
        d['PctHigh']        = sess.PctHigh
        
        if sess.Pulse:
            flen        = 2
            ftype       = 'H'
            nfields     = int( len( sess.Pulse ) / flen )
            if nfields is not 0:
                d['Pulse']  = struct.unpack( ftype * nfields, sess.Pulse )
        
        if sess.LiveIBI:
            flen            = 4
            ftype           = 'i'
            nfields         = int( len( sess.LiveIBI) / flen )
            if nfields is not 0:
                d['LiveIBI']    = struct.unpack( ftype * nfields, sess.LiveIBI )

        if sess.SampledIBI:
            flen            = 4
            ftype           = 'i'
            nfields         = int( len( sess.SampledIBI) / flen )
            if nfields is not 0:
                d['SampledIBI'] = struct.unpack( ftype * nfields, sess.SampledIBI )

        if sess.ArtifactFlag:
            flen                = 4
            ftype               = 'i'
            nfields             = int( len( sess.ArtifactFlag) / flen )
            if nfields is not 0:
                d['ArtifactFlag']   = struct.unpack( ftype * nfields, sess.ArtifactFlag )

        if sess.AccumZoneScore:
            flen                = 4
            ftype               = 'i'
            nfields             = int( len( sess.AccumZoneScore) / flen )
            if nfields is not 0:
                d['AccumZoneScore'] = struct.unpack( ftype * nfields, sess.AccumZoneScore )

        if sess.ZoneScore:
            flen            = 4
            ftype           = 'i'
            nfields         = int( len( sess.ZoneScore) / flen )
            if nfields is not 0:
                d['ZoneScore']  = struct.unpack( ftype * nfields, sess.ZoneScore )

        if sess.Free2:
            flen        = 4
            ftype       = 'i'
            nfields     = int( len( sess.Free2) / flen )
            if nfields is not 0:
                d['Free2']  = struct.unpack( ftype * nfields, sess.Free2 )

        if sess.Free3:
            flen        = 4
            ftype       = 'i'
            nfields     = int( len( sess.Free3) / flen )
            if nfields is not 0:
                d['Free3']  = struct.unpack( ftype * nfields, sess.Free3 )

        if sess.EntrainmentParameter:
            flen        = 4
            ftype       = 'i'
            nfields     = int( len( sess.EntrainmentParameter) / flen )
            if nfields is not 0:
                EP          = struct.unpack( ftype * nfields, sess.EntrainmentParameter )
                d['EntrainmentParameter'] = [ ep / 100. for ep in EP ]
        
        entries += [ d ]
        
    return entries
    
    
def read_version( filename ):
    
    db = sqlite3.connect( filename )
    query = db.execute( 'select Version from VersionTable' )
    for q in query:
        return q[0]

# ----------------------------------------------------------------------------

def main():

    parser = optparse.OptionParser( usage=usage )
    parser.add_option( '-v', dest='verbose', action='store_true', default=False, help='verbose output' )
    parser.add_option( '-m', dest='mode', default='session', help='mode: session, user or version [default: %default]' )
    parser.add_option( '-o', dest='output',  action='store', help='output file' )
    parser.add_option( '-s', dest='session', action='store', help='session indices in format A,B,C-D,E,...' )

    ( options, args ) = parser.parse_args()
    
    if len( args ) is not 1:
        parser.error( 'require only 1 argument of emdatabase file' )
        
    if options.mode not in MODES:
        parser.error( '-m argument must be one of %s' % str( MODES ) )
        
    output = options.output
    if not output:
        output = '%s.json' % options.mode 
    
    filename    = args[0]
    version     = read_version( filename )
    
    if version is not DB_VERSION:
        parser.error( 'emdb version %d. script only supports version 9' % version )

    if options.mode == 'version':
        print 'Version: %i' % version
        return

    db = connect_db( filename )

    if options.mode == 'user':
        entries = read_user( db )
    elif options.mode == 'session':
        sesslist    = None
        if options.session:
            sesslist = session_set( options.session )
        print sesslist
        entries     = read_session( db, sesslist )
            
    of = open( output, 'wb' )
    json.dump( entries, of, sort_keys=True, indent=2 )


if __name__ == "__main__":
    sys.exit( main() )
