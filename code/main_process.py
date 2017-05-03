import csv, operator
import os
from shutil import copyfile
from code.youtube import initialize_upload
from code.settings import get_channel_id

def substring( cad, start, len ):
	return cad[ start : start + len ]

def get_reg_as_dict( reg ):
	if len( reg ) == 8:
		return {
			"site_name" 	: reg[ 0 ],
			"uid"			: reg[ 1 ],
			"text"			: reg[ 2 ],
			"created_at"	: reg[ 3 ],
			"format"		: reg[ 4 ],
			"file_name"		: reg[ 5 ],
			"url_bc"		: reg[ 6 ],
			"in_bc"			: reg[ 7 ]
		}
	else:
		return {}

def process_file( base_path, tmp_file, done_path, video_files_dir, options, yt, createAtAsPublishedAt ):
	file = "%s/%s" % ( base_path, tmp_file )
	file_out = "%s/%s" % ( done_path, tmp_file ) 
	video_files_dir += "/%s" % tmp_file.replace( " ", "_" ).replace( ".csv", "")
	print( "Processing %s with channel id %s" % ( file, options[ "channel_id"] ) )
	if not os.access( video_files_dir, os.R_OK ):
		exit( "Unable to access to %s (main_process.process_file)" % video_files_dir )
	copyfile( file, file + ".bkp" )
	csv_file = open( file )
	csv_file_out = open( file_out, "w", newline = '' )
	regs = csv.reader( csv_file )
	csv_out_stream = csv.writer( csv_file_out, quoting = csv.QUOTE_MINIMAL )
	first_line = True
	for reg in regs:
		if first_line:
			first_line = not first_line
			reg.append( "status" )
			reg.append( "comments" )
			reg.append( "YT id" )
			csv_out_stream.writerow( reg )
		else:
			reg_dict = get_reg_as_dict( reg )
			status = ""
			comments = ""
			yt_id = ""
			if not os.access( "%s/%s" % (video_files_dir, reg_dict["file_name"] ), os.R_OK ):
				status = "Not Found"
				comments = "File %s/%s not found" % ( video_files_dir, reg_dict["file_name"] )
			else:
				options[ "title" ] = substring( reg_dict[ "text" ].strip(), 0, 100 )
				options[ "description" ] = "%s\n\nUID: %s\nCreated At: %s" % ( reg_dict[ "text" ], reg_dict[ "uid" ], reg_dict[ "created_at" ] )
				options[ "file" ] = "%s/%s" % ( video_files_dir, reg_dict[ "file_name" ] )
				if createAtAsPublishedAt:
					options[ "publishedAt" ] = substring( reg_dict[ "created_at" ], 0, 19 ) + ".0Z"
				result = initialize_upload( yt, options )
				if result[ 0 ] == "Ok":
					status = "Uploaded"
					yt_id = result[ 1 ]
				elif result[ 0 ] == "Failed":
					status = "Failed"
					comments = result[ 1 ]
			reg.append( status )
			reg.append( comments )
			reg.append( yt_id )
			csv_out_stream.writerow( reg )
	del( reg )
	del( regs )
	csv_file.close()
	del( csv_file )
	csv_file_out.close()
	del( csv_file_out )

def process_files( base_path, files, done_path, video_files_dir, options, yt, createAtAsPublishedAt ):
	if not createAtAsPublishedAt:
		del( options[ "publishedAt" ] )
	for file in files:
		if not os.access( base_path + "/" + file, os.R_OK ):
			exit( "Unable to access to %s/%s" % ( base_path, file ) )
		channel_id = get_channel_id( file )
		if channel_id == None:
			print( "There is no channel id for %s" % file )
		else:
			options[ "channel_id" ] = channel_id;
			process_file( base_path, file, done_path, video_files_dir, options, yt, createAtAsPublishedAt )
