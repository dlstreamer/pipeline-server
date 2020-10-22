import sys

import logging
import os
from media_stream_processor import MediaStreamProcessor
from arguments import parse_args
from samples.lva_ai_extension.common.exception_handler import log_exception

def _log_options(args):
    heading = "Options for {}".format(os.path.basename(__file__))
    banner = "="*len(heading)
    logging.info(banner)
    logging.info(heading)
    logging.info(banner)
    for arg in vars(args):
        logging.info("{} == {}".format(arg, getattr(args, arg)))
        logging.info(banner)
            

def main():
    try:
        # Get application arguments
        args = parse_args()

        _log_options(args)
        
        # Run stream processer loop
        msp = MediaStreamProcessor(args.grpc_server_address,
                                   args.sample_file,
                                   args.loop_count,
                                   args.use_shared_memory)
        msp.start()

    except:
        log_exception()
        exit(-1)

if __name__ == "__main__": 
    # Set logging parameters
    logging.basicConfig(
        level=logging.INFO,
        format='[AIXC] [%(asctime)-15s] [%(threadName)-12.12s] [%(levelname)s]: %(message)s',
        handlers=[
            #logging.FileHandler(LOG_FILE_NAME),     # write in a log file
            logging.StreamHandler(sys.stdout)       # write in stdout
        ]
    )

    # Call Main logic
    main()

    logging.info('Client finished execution')

