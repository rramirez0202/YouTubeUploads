import http.client
import httplib2
import os
import random
import sys
import time
import json

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload

from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

httplib = http.client

httplib2.RETRIES = 1
MAX_RETRIES = 10
RETRIABLE_EXECEPTIONS = ( 
	httplib2.HttpLib2Error, 
	IOError, 
	httplib.NotConnected, 
	httplib.IncompleteRead, 
	httplib.ImproperConnectionState, 
	httplib.CannotSendRequest,
	httplib.CannotSendHeader,
	httplib.ResponseNotReady,
	httplib.BadStatusLine
	)	
RETRIABLE_STATUS_CODES = [ 500, 502, 503, 504 ]
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
MISSING_CLIENT_SECRETS_MESSAGE = "OAuth should be configured, you need to populate client_secrets.json with info from DevConsole https://console.developers.google.com - https://developers.google.com/api-client-library/python/guide/aaa_client_secrets"
VALID_PRIVACY_STATUSES = ( "public", "private", "unlisted" );

def verify_oauth_file( client_secret_file ):
	oauth2_file = "%s-oauth2.json" % sys.argv[ 0 ]
	if os.access( oauth2_file, os.R_OK ):
		oauth2_stream = open( oauth2_file, "r" )
		oauth2_json = json.loads( oauth2_stream.read() );
		oauth2_stream.close()
		del( oauth2_stream )
		csf_stream = open( client_secret_file, "r" )
		csf_json = json.loads( csf_stream.read() )
		csf_stream.close()
		del( csf_stream )
		for mode in csf_json:
			if oauth2_json[ "client_secret" ] != csf_json[ mode ][ "client_secret" ]:
				os.remove( oauth2_file )

def get_authenticated_service( client_secrets_file, args ):
	flow = flow_from_clientsecrets( client_secrets_file, scope = YOUTUBE_UPLOAD_SCOPE, message = MISSING_CLIENT_SECRETS_MESSAGE )
	storage = Storage( "%s-oauth2.json" % sys.argv[ 0 ] )
	credentials = storage.get()
	if credentials is None or credentials.invalid:
		credentials = run_flow( flow, storage, args )
	return build( YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http = credentials.authorize( httplib2.Http() ) )
	
def initialize_upload( youtube, options ):
	try:
		tags = None
		if options[ "keywords" ]:
			tags = options[ "keywords" ].split( "," )
		snippet_d = dict(
				title = options[ "title" ],
				description = options[ "description" ],
				tags = tags,
				categoryId = options[ "category" ],
				channelId =  options[ "channel_id" ], # "UCg9IT0PBQjq7H_3ki1o0sbA"
			)
		# print( snippet_d )
		try:
			snippet_d[ "publishedAt" ] = options[ "publishedAt" ]
		except KeyError:
			pass
		body = dict(
			snippet = snippet_d,
			status = dict(
				privacyStatus = options[ "privacyStatus" ]
			)
		)
		insert_request = youtube.videos().insert(
			part = ",".join( body.keys() ),
			body = body,
			media_body = MediaFileUpload( options[ "file" ], chunksize = -1, resumable = True )
			#, onBehalfOfContentOwner = "83275071332-pi683rocmu8v7vqgto9frji1sp1dt1rg.apps.googleusercontent.com"
		)
		return resumable_upload( insert_request, youtube );
	except HttpError as e:
		return [ "Failed", "HTTP error %d ocurred: %s" % ( e.resp.status, e.content ) ]
	
def resumable_upload( insert_request, youtube ):
	response = None
	error = None
	retry = 0
	errors = ""
	while response is None:
		try:
			status, response = insert_request.next_chunk()
			if 'id' in response:
				return [ "Ok", response[ 'id' ] ]
			else:
				return [ "Failed", "Upload failed with '%s'" % response ]
		except HttpError as e:
			if e.resp.status in RETRIABLE_STATUS_CODES:
				error = "A retriable HTTP error %d ocurred: %s" % ( e.resp.status, e.content )
			else:
				raise
		except RETRIABLE_EXECEPTIONS as e:
			error = "A retriable error ocurred: %s" % e
		if error is not None:
			errors += error + " && "
			retry += 1
			if retry > MAX_RETRIES:
				return [ "Failed", "No longer attemping to retry. Errors: " + errors ]
			max_sleep = 2 ** retry
			sleep_seconds = random.random() * max_sleep
			print( "Sleeping %f seconds and retrying..." % sleep_seconds )
			time.sleep( sleep_seconds )
