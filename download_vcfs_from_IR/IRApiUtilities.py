'''
Created Jan 2013

IRAPiUtilities

@author: Joe Wood

'''

import urllib2
import logging
import zipfile
import csv
import re
import os
import json
import pprint
import subprocess

class IRApiUtilities:
    '''
    classdocs
    '''

    def __init__(self,container_id=None,sample_T_id=None,sample_N_id=None):
        '''
        Constructor
        '''
        self.container_id = container_id
        self.sample_T_id = sample_T_id
        self.sample_N_id = sample_N_id
    
    def get_variome(self,analysis_id,token,analysis_base_url,variome_base_url,output_dir):
        
        ################################################################################
        # First, download the json containing the URLs for the actual vcfs
        
        analysis_json = self.get_api_json(analysis_id,token,analysis_base_url,output_dir)
        print analysis_json
        
        if analysis_json:            
            logging.info('Parsing json file %s',analysis_json)
            
            #try:
            with open(analysis_json) as json_file:
                json_data = json.load(json_file)
                self.vcf_location = json_data[0]["data_links"]["unfiltered_variants"]

                try:
                    self.sample_N_id = json_data[0]["samples"]["NORMAL"]
                    self.sample_T_id = json_data[0]["samples"]["TUMOR"]
                    
                    logging.info("Tumour sample id is %s",self.sample_T_id)
                    logging.info("Normal sample_id is %s",self.sample_N_id)
                except:
                    logging.info("No tumor/normal info found in the JSON.")
                   
            #except:
            #    logging.error("Json parsing error %s",analysis_json)
            
            ################################################################################
            # Second, download and extract the zip file containing the vcfs
            
            #get variome zip file
            variome_zipfile = self.get_api_zip(self.vcf_location,token,variome_base_url,output_dir)
                        
            if(variome_zipfile != 0):            
                logging.debug('Extracting zip file %s',variome_zipfile)

                try:
                    #extract files
                    unzip_cmd = "unzip output.zip" 
                    subprocess.call(unzip_cmd, shell=True)
                    
                    unzip_cmd = "unzip -B %s" % (variome_zipfile)
                    subprocess.call(unzip_cmd, shell=True)
                
                except zipfile.BadZipfile:
                    logging.error("Zip file error")
            
                logging.debug('Extraction complete')
            
                #rename files with sample ids
                
                filename_extension = ""

                if (os.path.exists(output_dir+'Sample 1.vcf')):
                    os.rename(output_dir+'Sample 1.vcf', output_dir+self.sample_T_id+filename_extension+'.vcf')
                if (os.path.exists(output_dir+'Sample 1.tsv')):
                    os.rename(output_dir+'Sample 1.tsv', output_dir+self.sample_T_id+filename_extension+'.tsv')
                if (os.path.exists(output_dir+'Sample 2.vcf')):
                    os.rename(output_dir+'Sample 2.vcf', output_dir+self.sample_N_id+filename_extension+'.vcf')
                if (os.path.exists(output_dir+'Sample 2.tsv')):
                    os.rename(output_dir+'Sample 2.tsv', output_dir+self.sample_N_id+filename_extension+'.tsv')
                     
                #reset class variables        
                self.container_id = None
                self.sample_T_id = None
                self.sample_N_id = None    
                return 1
            else:
                #reset class variables        
                self.container_id = None
                self.sample_T_id = None
                self.sample_N_id = None 
                return 0
        else:
            #reset class variables     
            self.container_id = None
            self.sample_T_id = None
            self.sample_N_id = None 
            return 0  
    
    def get_api_json(self,analysis_id,token,base_url,output_dir):
        
        req = urllib2.Request(base_url+analysis_id)
        req.add_header("Authorization",token)
        
        json_filename = output_dir+analysis_id+".json"
        
        f = urllib2.urlopen(req)
        
        logging.debug('Requesting json from URL %s',req.get_full_url())
        
        try:
            f = urllib2.urlopen(req)
            
            logging.debug('Starting file download %s',json_filename)
            
            # Open local file for writing
            with open(json_filename, "wb") as local_file:
                local_file.write(f.read())
                
            logging.debug('Completed file download %s',json_filename)
                        
            return json_filename
            
        except urllib2.HTTPError, e:
            logging.error('HTTP error: %d',e.code)
            return 0;
        except urllib2.URLError, e:
            logging.error('Network error: %s',e.reason.args[0]+" "+e.reason.args[1])
            return 0;
        
    
    def get_api_zip(self,vcf_location,token,base_url,output_dir):              
        
        #send request with authentication token (as used in IonReporterUploader plugin)

        req = urllib2.Request(vcf_location)
        req.add_header("Authorization",token)
        
        zip_filename = vcf_location.split("/")[-1]
        
        logging.debug('Requesting URL %s',req.get_full_url())
        
        f = urllib2.urlopen(req)
        
        try:
            curl_cmd = """curl -k -H "Authorization:%s" "%s" -o output.zip""" % (token, vcf_location)
            subprocess.call(curl_cmd, shell=True)
            
            return zip_filename
            
        except urllib2.HTTPError, e:
            logging.error('HTTP error: %d',e.code)
            return 0;
        except urllib2.URLError, e:
            logging.error('Network error: %s',e.reason.args[0]+" "+e.reason.args[1])
            return 0;