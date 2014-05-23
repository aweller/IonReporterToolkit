'''
Created on 28 Jan 2014

@author: wooda1

'''
from config import config
import csv
import re
import logging
import Model.Sample as Sample
import Model.IRSample as IRSample
import Model.Analysis as Analysis


def main():
  
    #configure logging 
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%d-%m-%y %H:%M',
                    filename=config['log_file'],
                    filemode='w') 
    
    #get file contents
    #IR files can be generated via API on the fly
    input_sample_list = open(config['lab_sample_list']).readlines()
    ir_sample_list = open(config['ir_sample_list']).readlines()
    ir_14_analyses = open(config['ir14_analysis_file'], 'rb').readlines()
    ir_16_analyses = open(config['ir16_analysis_file'], 'rb').readlines()
    
    logging.info('input files read')
        
    #Analysis_Name will be used to extract vcf via API
    
    #List for sample objects
    input_samples = []
        
    #loop input sample names
    for input_sample in input_sample_list:

        sample_info = input_sample.split(',')
        
        sample_id = sample_info[0].rstrip()
        
        #create sample object
        sample = Sample.Sample(sample_id,None)        
        
        #list of ir_samples found
        ir_samples = []
        
        #loop ir sample names to find match        
        for ir_sample_line in ir_sample_list:
           
           ir_sample_info = ir_sample_line.split(',')
           ir_sample_id = ir_sample_info[0]
           
           samplename_match = sample_id in ir_sample_id
           
           #if sample matches an ir_sample
           if (samplename_match):
               
               #create IRSample instance
               irsample = IRSample.IRSample(ir_sample_id,None,None,None)   
               
               #set file path of irsample
               irsample.sample_filepath = ir_sample_info[2]
               
               #set sample file type                
               if re.search("sff",irsample.sample_filepath,re.IGNORECASE):
                    irsample.file_type = "sff"
               elif re.search("vcf",irsample.sample_filepath,re.IGNORECASE):
                    irsample.file_type = "vcf"
               else:
                    irsample.file_type = "bam"
               
               #logging.debug("%s:%s:%s:%s",sample.sample_id,irsample.sample_id
               #              ,irsample.file_type,irsample.sample_filepath)
                              
               #create analysis list
               ir_analyses=[]
                              
               #find analyses with ir_sample_id
               #IR 1.4
               ir_14_analysis_list = get_ir_analyses(ir_sample_id,ir_14_analyses)
               #IR 1.6
               ir_16_analysis_list = get_ir_analyses(ir_sample_id,ir_16_analyses)
                
               if not ((len(ir_14_analysis_list)==0) and (len(ir_16_analysis_list)==0)):
                      
                    #add analysis info to sample object
                    for ir_14_analysis in ir_14_analysis_list:
                    
                        iranalysis = Analysis.Analysis()
                        set_analysis_info(iranalysis,ir_14_analysis)
                        ir_analyses.append(iranalysis)
                        
                    for ir_16_analysis in ir_16_analysis_list:
                        
                        iranalysis = Analysis.Analysis()
                        set_analysis_info(iranalysis,ir_16_analysis)                   
                        ir_analyses.append(iranalysis)
                
               #set analysis list of irsample
               irsample.ir_analyses = ir_analyses
               
               #add irsample to ir sample list in Sample               
               ir_samples.append(irsample) 
               
           #set ir_samples
           sample.ir_samples = ir_samples                   
                       
        #add sample to input_samples list
        input_samples.append(sample)  
    
    #print out info
    print_sample_info(input_samples,config['output_file'])
                
    logging.info('finished')

def get_ir_analyses(sample_id,analyses):

    sample_analyses = []
    
    for analysis in analyses:
        analysis_info = analysis.split(',')
        if sample_id in (analysis_info[1],analysis_info[2]):
            #add line to sample_analyses
            sample_analyses.append(analysis)
    
    return sample_analyses

def set_analysis_info(irsample,ir_analysis):
    
    ir_analysis.rstrip()
    
    analysis_info = ir_analysis.split(',')

    irsample.ir_version = analysis_info[0]
    irsample.t_sample = analysis_info[1]
    irsample.n_sample = analysis_info[2]
    irsample.analysis_name = analysis_info[3]
    irsample.workflow = analysis_info[4]
    irsample.status = analysis_info[5]
    irsample.user = analysis_info[6]
    irsample.analysis_date = analysis_info[7]

def print_sample_info(samples,outputfilename):
    '''
    for sample in samples:
        logging.debug('sample %s,ir_samples %s',sample.sample_id,str(len(sample.ir_samples)))
        logging.debug(",".join([str(irsample.sample_id) for irsample in sample.ir_samples]))
    '''
    #open output file
    sample_info_file = file(outputfilename, 'wb') 

    #set heading
    sample_info_file.write(("Input_Sample,IR_sample,IR_filetype,File_Path,"
                            +"IR_Version,Tumour_Sample,Normal_Sample,"
                            +"Analysis_Name,Workflow,Status,User,Date\n"))
    for sample in samples:
        logging.debug("%s:%s",sample.sample_id,str(len(sample.ir_samples)))
        for ir_sample in sample.ir_samples:
             logging.debug("%s:%s",ir_sample.sample_id,str(len(ir_sample.ir_analyses)))
             
    for sample in samples:
        logging.debug("%s:%s",sample.sample_id,str(len(ir_sample.ir_analyses)))
        if (len(sample.ir_samples)>0):
            for ir_sample in sample.ir_samples:
                
                if (len(ir_sample.ir_analyses)>0):
                    #write analysis info
                    for ir_analysis in ir_sample.ir_analyses:
                        #write sample id
                        sample_info_file.write(sample.print_sample_info()+",")
                        #write ir_sample_id
                        sample_info_file.write(ir_sample.print_sample_info()+",")
                        sample_info_file.write(ir_analysis.print_analysis_info())
                elif (len(ir_sample.ir_analyses)==0):
                    #write sample id
                    sample_info_file.write(sample.print_sample_info()+",")
                    #write ir_sample_id
                    sample_info_file.write(ir_sample.print_sample_info()+"\n")
                    
        elif (len(sample.ir_samples)==0):
            #write sample id only
            sample_info_file.write(sample.print_sample_info()+"\n")
    
    sample_info_file.close()
    
if __name__ == '__main__':
    main()
  