from code.settings import getsettings
from code.main_process import process_files
from code.youtube import get_authenticated_service
from code.youtube import VALID_PRIVACY_STATUSES
from code.youtube import verify_oauth_file
from oauth2client.tools import argparser

if __name__ == '__main__':
	settings = getsettings()
	if len( settings[ 'files_2do' ] ) > 0:
		opt = {
			'keywords'		: settings[ "keywords" ],
			'category'		: settings[ "category" ],
			'privacyStatus'	: settings[ "privacyStatus" ],
			'title'			: "",
			'description'	: "",
			'file'			: "",
			'publishedAt'	: "",
			'channel_id'	: ""
		}
		args = argparser.parse_args()
		verify_oauth_file( settings[ "client_secrets" ] )
		print( "Authenticating" )
		yt = get_authenticated_service( settings[ "client_secrets" ], args )
		process_files( settings[ "csv_dir" ], settings[ 'files_2do' ], settings[ "csv_dir_done" ], settings[ "video_files_dir" ], opt, yt, settings[ 'createAtAsPublishedAt' ] )
	else:
		print( "There are not csv files to process" )