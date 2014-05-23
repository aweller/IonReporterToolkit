##########################################################################################
#
# This script downloads vcfs from IonReporter
#
# Written by Joe Wood (joe.wood@lifetech.com) and Andreas Weller (andreas.m.weller@gmail.com)
#
# Requirements:
#    - an input file of analysis names (provided as the first commandline argument)
#    - the Python script IRApiUtilities.py which contains class definitions
#    - the Python script config.py which contains the token to access Ion Reporter as well as URLs
#
# This script contains a lot of disabled "try:, except:" constructs to catch errors
# I have disabled them to allow better bug fixing, if you wan't a smoother output just reenable them
#
##########################################################################################

import logging
from config import api_config
import IRApiUtilities
import csv
import sys
import os

def main():
    
    ##########################################################################################
    # Setup variables
    
    # configure logging
    # if you want to redirect to a file, replace 'stream=sys.stdout' 
    # with filename='log.txt' and filemode='w'
    
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%d-%m-%y %H:%M',
                    stream=sys.stdout,
                    filemode='w') 
       
    myIRApiUtilities = IRApiUtilities.IRApiUtilities()
    
    # read analysis file
    # this is a list of analysis names (e.g. simply copied from the IR analysis overview page)
    
    analysis_file = sys.argv[1]
    
    try:
        analysisReader = csv.reader(open(analysis_file, 'rb'), delimiter=',')
    except IOError:
        print "Error: can\'t find file or read data"
        logging.error("Error: can\'t find file or read data") 
    logging.debug('analysis_file %s read',api_config['analysis_file']) 
    
    # setup output directory
    output_path = api_config['output_path']
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    
    ##########################################################################################
    # Download the vcfs
    
    for analysis in analysisReader:
        
        #try:
        analysis_id = analysis[0].strip().replace(" ", "") # to get rid of sample names with spaces which break the downloader        
        get_variome = False

        #try:     
        get_variome = myIRApiUtilities.get_variome(analysis_id,
                                                   api_config['token'],
                                                   api_config['analysis_base_url'],
                                                   api_config['variome_base_url'],
                                                   output_path)
        #except:
            #logging.error('Variome fetching failed for analysis %s',analysis_id)
        
        if get_variome:
            logging.info('Variome exported for analysis %s',analysis_id)
        else:
            logging.error('Variome export failed for analysis %s',analysis_id)
        #except:
        #    logging.error('Error in fetching %s',analysis[0])
     
    logging.info("Finished")    

if __name__ == '__main__':
    main()