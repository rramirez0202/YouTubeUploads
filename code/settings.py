import os
import json
import csv, operator

channel_id = {}

def getsetting( jsonObject, setting, mandatory = True ):
	val = ""
	try:
		val = jsonObject[ setting ]
	except KeyError:
		if mandatory:
			exit( setting + " key not found in settings" )
	return val

def getsettings():
	settings_path = ""
	settings_file = None
	settings_json = None
	csv_dir_path = ""
	csv_dir_done_path = ""
	csv_files_2do = []
	client_secrets_path = ""
	video_files_dir = ""
	keywords = ""
	category = ""
	privacyStatus = ""
	settings_path = os.getcwd() + "/settings.json"
	if not os.access( settings_path, os.R_OK ):
		exit( "Unable to access to %s" % settings_path )
	settings_file = open( settings_path, "r" )
	settings_json = json.loads( settings_file.read() );
	settings_file.close()
	del( settings_file )
	csv_dir_path = "%s/%s" % ( os.getcwd(), getsetting( settings_json, "csv_dir" ) )
	if not os.access( csv_dir_path, os.R_OK ):
		exit( "Unable to access to %s" % csv_dir_path )
	else:
		csv_dir_done_path = csv_dir_path + '/done'
		if not os.access( csv_dir_done_path, os.F_OK ):
			os.mkdir( csv_dir_done_path )
		if not os.access( csv_dir_done_path, os.R_OK ):
			exit( "Unable to access to %s" % csv_dir_done_path )
		aux_files = os.scandir( csv_dir_path )
		for file in aux_files:
			if file.is_file() and file.name.lower().endswith( 'csv' ):
				csv_files_2do.append( file.name )
	video_files_dir = getsetting( settings_json, "video_files_dir" )
	if not os.access( video_files_dir, os.R_OK ):
		exit( "Unable to access to " +  video_files_dir )
	client_secrets_path = os.getcwd() + "/" + getsetting( settings_json, "client_secrets_file" )
	if not os.access( client_secrets_path, os.R_OK ):
		exit( "Unable to access to " +  client_secrets_path )
	keywords = getsetting( settings_json, "keywords" )
	category = getsetting( settings_json, "category" )
	privacyStatus = getsetting( settings_json, "privacyStatus" )
	createAtAsPublishedAt = getsetting( settings_json, "createAt_as_publishedAt" )
	channelIdFile = getsetting( settings_json, "channelIdFile" )
	populate_channel_id( channelIdFile )
	return {
		'csv_dir'		 		: csv_dir_path,
		'csv_dir_done' 			: csv_dir_done_path,
		'files_2do'				: csv_files_2do,
		'client_secrets'		: client_secrets_path,
		'video_files_dir'		: video_files_dir,
		'keywords'				: keywords,
		'category'				: category,
		'privacyStatus'			: privacyStatus,
		'createAtAsPublishedAt'	: createAtAsPublishedAt,
		'channelIdFile'			: channelIdFile
	}
	
def populate_channel_id( channel_id_file ):
	if not os.access( channel_id_file, os.R_OK ):
		exit( "Unable to access to %s" % channel_id_file )
	csv_file = open( channel_id_file, "r" )
	regs = csv.reader( csv_file )
	first_line = True
	for reg in regs:
		if first_line:
			first_line = not first_line
		else:
			channel_id[ reg[ 0 ] ] = reg[ 1 ]
			
def get_channel_id( csv_file ):
	try:
		return channel_id[ csv_file ]
	except KeyError:
		return None