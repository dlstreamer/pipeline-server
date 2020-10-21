import sys

import logging

from utils.arguments import ArgumentParser, ArgumentsType
from utils.exception_handler import PrintGetExceptionDetails
from media_stream_processor import MediaStreamProcessor

def Main():
    try:
        # Get application arguments
        ap = ArgumentParser(ArgumentsType.CLIENT)

        # Create gRPC stub
        grpcServerAddress = ap.GetGrpcServerAddress()
        logging.info('gRPC server address: {0}'.format(grpcServerAddress))

        # Get sample video frame address
        sampleInFileName = ap.GetSampleMediaAddress()
        logging.info('Sample video frame address: {0}'.format(sampleInFileName))

        # Get loop count
        loopCount = ap.GetLoopCount()
        logging.info('How many times to send sample frame to aix server: {0}'.format(loopCount))

        # Get shared memory flag
        shmFlag = ap.GetSharedMemoryFlag()

        # Run stream processer loop
        msp = MediaStreamProcessor(grpcServerAddress, sampleInFileName, loopCount, shmFlag)
        msp.Start()

    except:
        PrintGetExceptionDetails()
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
    Main()

    logging.info('Client finished execution')

