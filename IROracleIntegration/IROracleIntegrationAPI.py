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
import IRApiUtilities

def main():
  
    #configure logging 
    #logging.basicConfig(level=logging.DEBUG,
    logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%d-%m-%y %H:%M',
                    filename=config['log_file'],
                    filemode='w') 
    
    myIRApiUtilities = IRApiUtilities.IRApiUtilities()
    
    #get file contents
    #IR files can be generated via API on the fly
    input_sample_list = open(config['lab_sample_list']).readlines()
    
    logging.info('starting api calls')
    
    #ir_sample_list = open(config['ir_sample_list']).readlines()
    #ir_14_analyses = open(config['ir14_analysis_file'], 'rb').readlines()
    #ir_16_analyses = open(config['ir16_analysis_file'], 'rb').readlines()
    
    ir_sample_list = myIRApiUtilities.get_samples("1x",config)
    
    ir_14_analyses = myIRApiUtilities.get_analyses("14",config)
    logging.info('1.4 analyses done')
    
    ir_16_analyses = myIRApiUtilities.get_analyses("16",config)
    logging.info('1.6 analyses done')
    
    #ir_40_analyses = myIRApiUtilities.get_analyses("40",config)
    
    #join lists
    ir_analyses = ir_14_analyses + ir_16_analyses
    
    logging.info('input files read and analyses object lists created')
        
    #Analysis_Name will be used to extract vcf via API
    
    #List for sample objects
    input_samples = []
        
    #loop input sample names
    for input_sample in input_sample_list:

        sample_info = input_sample.split(',')
        sample_id = sample_info[0].rstrip()
        
        try:
            sample_run_id = sample_info[1].rstrip()
        except:
            sample_run_id = None

        
        #create sample object
        sample = Sample.Sample(sample_id,None)        
        
        #list of ir_samples found
        ir_samples = []
        
        #loop ir sample names to find match        
        for ir_sample in ir_sample_list:
           #print sample_info, ir_sample.sample_id, ir_sample.run_id

           samplename_match = (sample_id in ir_sample.sample_id) or (sample_run_id == ir_sample.run_id) or (fix_quasar_names(sample_id, tumor_normal = "?") in fix_quasar_names(ir_sample.sample_id, tumor_normal = "?"))
           #if sample matches an ir_sample
           if (samplename_match):
                              
               #create analysis list
               sample_ir_analyses=[]
               
               #check for analyses for current ir sample
               
               for analysis in ir_analyses:
                   if ir_sample.sample_id in (analysis.t_sample,analysis.n_sample):
                       
                       #check if analysis already in sample_ir_analyses
                       #as t or n sample may have been matched already
                       
                       seen = 0
                       
                       for sample_ir_analysis in sample_ir_analyses:
                           if sample_ir_analysis.analysis_name == analysis.analysis_name:
                                seen = 1
                       
                       if seen == 0:
                           #add analysis object to sample_analyses
                           sample_ir_analyses.append(analysis)
                       
                             
               #set analysis list of ir_sample
               ir_sample.ir_analyses = sample_ir_analyses
               
               #add irsample to ir sample list in Sample               
               ir_samples.append(ir_sample) 
               
           #set ir_samples
           sample.ir_samples = ir_samples                   
                       
        #add sample to input_samples list
        input_samples.append(sample)  
    
    #print out info
    print_sample_info(input_samples,config['output_file'])
                
    logging.info('finished')

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
                        sample_info_file.write(ir_analysis.print_analysis_info()+"\n")
                elif (len(ir_sample.ir_analyses)==0):
                    #write sample id
                    sample_info_file.write(sample.print_sample_info()+",")
                    #write ir_sample_id
                    sample_info_file.write(ir_sample.print_sample_info()+"\n")
                    
        elif (len(sample.ir_samples)==0):
            #write sample id only
            sample_info_file.write(sample.print_sample_info()+"\n")
    
    sample_info_file.close()

def fix_quasar_names(sample, tumor_normal = None):
    
    if sample.startswith("Q"):            
        ##############################################
        if "pl2" in sample.lower() or "p2" in sample.lower():
            plate = "PL2"
        elif "pl3" in sample.lower() or "p3" in sample.lower():
            plate = "PL3"
        else:
            plate = "PL1"
        ##############################################
        plate_loc = sample.replace("-", "_").split("_")[1]
        
        if plate_loc[1:3].isdigit(): #  e.g. E08, correct order
            plate_loc = plate_loc[:3] #remove trailing letters
            
        else: # wrong order
            if len(plate_loc) == 2: # eg. 8E
                plate_loc = plate_loc[1] + "0" + plate_loc[0]
            elif len(plate_loc) == 3: # eg. 10E
                plate_loc = plate_loc[2] + plate_loc[:2]
        ##############################################
        match = re.search('v[0-9]', sample)
        if match:
            version = match.group(0)
        else:
            version = "v1"
        ##############################################
        if not tumor_normal: 
            tumor_normal = "?"
            if "T" in sample:
                tumor_normal = "T"
            elif "N" in sample:
                tumor_normal = "N"
        ##############################################
        new_sample = "_".join(["Q2"+plate, plate_loc, version, tumor_normal ])
        return new_sample
    
    else:
        return sample

if __name__ == '__main__':
    main()
  