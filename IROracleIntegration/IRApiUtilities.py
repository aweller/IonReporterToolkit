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
import Model.Analysis as Analysis
import Model.IRSample as IRSample
import pprint

class IRApiUtilities:
    '''
    classdocs
    '''

    def __init__(self,container_id=None,sample_T_id=None,sample_N_id=None):
        '''
        Constructor
        '''
        
    def get_samples(self,version,config):    
    
        '''
        test curl command:
        curl -o testsamples.zip -H "Authorization:Uhi5vNyadzCbnU9eSiLhDyBqDGLAwye7RES6QzqLDR2HXWbMKc5Q+UcZGb7X+MamkemomG892FcXfp8HnQkH2g==" https://ir16.ionreporter.lifetechnologies.com/ir14/rest/sample/metadata?sampleName=G125149H_v1
        '''
        #List for analysis objects
        samples = []
        
        #get zip file all samples
        samples_file = self.get_api_zip("",
                                        ('all_samples_%s' % version),
                                    config['token'],config[('all_samples_%s_base_url' % version)],
                                    config['output_path'])    
        
        samples_zip = zipfile.ZipFile(samples_file.name)
            
        logging.info('Extracting zip file %s',samples_file.name)
        
        try:
            
            container_file = samples_zip.extract(samples_zip.namelist()[0],config['output_path'])
            
            try:
                
                #read in sample info file
                container_reader = csv.reader(open(container_file, 'rb'), delimiter='\t')
                
                #rows = list(container_reader)
                
                for row in container_reader:
                #logging.debug(', '.join(row))
                    regex = re.compile("Sample Name:")
                    runid_regex = re.compile("OX[1|2]-[1-9][0-9][0-9]*")
                    print row,
                    if row:
                        if regex.match(row[0]):
                            sample_name_row = re.split(": ", row[0])
                            #logging.debug(analysis_name_row[1])
                                                      
                            #create IRSample object
                            sample = IRSample.IRSample()
                            
                            sample.sample_id = sample_name_row[1]
                            
                            #error here
                            
                            #get sample info row
                            sample_info_row = container_reader.next()
                            print "\t".join(sample_info_row)
                            sample_info_dict = {}
                            
                            for sample_info in sample_info_row:
                                #logging.info(sample_info.strip())
                                #sample_info.strip()
                                
                                if ("=" in sample_info):
                                    sample_info_item = re.split('=', sample_info.strip())
                                    sample_info_dict[sample_info_item[0]]=sample_info_item[1]
                            
                            if runid_regex.search("".join(row)):
                                sample_info_dict['Run ID'] = runid_regex.search("".join(row)).group()
                                
                            logging.debug(sample_info_dict)
                            
                            #set sample attributes
                            sample.run_id = sample_info_dict['Run ID'] if ('Run ID' in sample_info_dict) else None  
                            sample.sample_filepath = sample_info_dict['File Path'] if ('File Path' in sample_info_dict) else None
                            sample.chip_id = sample_info_dict['chipId'] if ('chipId' in sample_info_dict) else None
                            sample.chip_type = sample_info_dict['chipType'] if ('chipType' in sample_info_dict) else None
                            sample.device_id = sample_info_dict['deviceId'] if ('deviceId' in sample_info_dict) else None
                            sample.qc_file_path = sample_info_dict['qcFilePath'] if ('qcFilePath' in sample_info_dict) else None
                            sample.lib_prep = sample_info_dict['libraryPreprationMethod'] if ('libraryPreprationMethod' in sample_info_dict) else None
                            sample.promo = sample_info_dict['promo'] if ('promo' in sample_info_dict) else None
                            sample.status = sample_info_dict['status'] if ('status' in sample_info_dict) else None
                            sample.org = sample_info_dict['Organization Name'] if ('Organization Name' in sample_info_dict) else None
                            sample.imported_by = sample_info_dict['Imported By'] if ('Imported By' in sample_info_dict) else None
                            sample.pathology = sample_info_dict['Pathology'] if ('Pathology' in sample_info_dict) else None
                            sample.pathology_summary = sample_info_dict['Pathology_summary'] if ('Pathology_summary' in sample_info_dict) else None
                            sample.gender = sample_info_dict['Gender'] if ('Gender' in sample_info_dict) else None
                            sample.barcode = sample_info_dict['Barcode'] if ('Barcode' in sample_info_dict) else None
                            

                            logging.debug(sample.sample_filepath)
                            #set sample file type                
                            if sample.sample_filepath:
                                if re.search("sff",sample.sample_filepath,re.IGNORECASE):
                                    sample.file_type = "sff"
                                elif re.search("vcf",sample.sample_filepath,re.IGNORECASE):
                                    sample.file_type = "vcf"
                                else:
                                    sample.file_type = "bam"                    
                            
                            print pprint.pprint(sample.__dict__)
                            
                            #add sample to samples list
                            samples.append(sample)

            except IOError:
                print "Error: can\'t find file or read data"
    
        except zipfile.BadZipfile:
                logging.error("Zip file error")
        
        samples_zip.close()
        
        return samples
    
    def get_analyses(self,version,config):
        #List for analysis objects
        analyses = []
        
        #get zip file all analyses
        analyses_file = self.get_api_zip("",('all_analyses_%s' % version),
                                    config['token'],config[('all_analysis_%s_base_url' % version)],
                                    config['output_path'])    
 
        analyses_zip = zipfile.ZipFile(analyses_file.name)
            
        logging.info('Extracting zip file %s',analyses_file.name)
        
        try:
            
            container_file = analyses_zip.extract(analyses_zip.namelist()[0],config['output_path'])
            
            try:
                
                #read in analysis info file
                container_reader = csv.reader(open(container_file, 'rb'), delimiter='\t')
                
                #rows = list(container_reader)
                
                for row in container_reader:
                #logging.debug(', '.join(row))
                    regex = re.compile("Analysis Name:")
                    if row:
                        if regex.match(row[0]):
                            analysis_name_row = re.split(": ", row[0])
                            #logging.debug(analysis_name_row[1])
                            
                            #get analysis info row
                            info_row = container_reader.next()
                            
                            #create Analysis object
                            analysis = Analysis.Analysis()

                            #get sample ids for current analysis
                            self.set_sample_ids(info_row[12],analysis)
                                
                            analysis.ir_version = version
                            analysis.analysis_name = analysis_name_row[1]
                            analysis.workflow = info_row[4]
                            analysis.status = info_row[1]
                            analysis.user = info_row[9]
                            analysis.analysis_date = info_row[10]
                            #add analysis to analyses list
                            analyses.append(analysis)

            except IOError:
                print "Error: can\'t find file or read data"
    
        except zipfile.BadZipfile:
                logging.error("Zip file error")
        
        analyses_zip.close()
        
        return analyses
    
    
        
    def get_api_zip(self,analysis_id,file_name,token,base_url,output_dir):              
        
        #send request with authentication token (as used in IonReporterUploader plugin)
        req = urllib2.Request(base_url+analysis_id)
        req.add_header("Authorization",token)
        
        zip_filename = output_dir+file_name+".zip"
         
        try:
            f = urllib2.urlopen(req)
            
            logging.debug('Starting file download %s',zip_filename)
            
            # Open local file for writing
            with open(zip_filename, "wb") as local_file:
                local_file.write(f.read())
                
            logging.debug('Completed file download %s',zip_filename)
            
            return local_file
            
        except urllib2.HTTPError, e:
            logging.error('HTTP error: %d',e.code)
            return 0;
        except urllib2.URLError, e:
            logging.error('Network error: %s',e.reason.args[0]+" "+e.reason.args[1])
            return 0;

    def set_sample_ids(self,sample_string,analysis):
        
        #logging.debug(sample_string)
        #split out samples
        samples = sample_string.split(';')
        
        #Note order samples returned in can vary eg. T/N or N/T
        for sample in samples:
            sample_info = sample.split('=')
            match = re.search(r'Normal|Self|Tumor', sample_info[0])
            if ((match != None) and (match.group() == 'Normal')):
                analysis.n_sample = sample_info[1]
            elif((match != None) and ((match.group() == 'Tumor') or (match.group() == 'Self'))):
                analysis.t_sample = sample_info[1]
            else:
                logging.error("No sample id")      
                         
