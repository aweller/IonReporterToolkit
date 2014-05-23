import pexpect
import subprocess
from subprocess import Popen, PIPE
import multiprocessing as mp
import os
import pdb
import sys
import time
import datetime
import zipfile

def run(cmd):
    p = Popen(cmd, stderr=PIPE, stdout=PIPE, shell=True)
    output, errors = p.communicate()
    return errors.split("\r")[-1]  

def download_bam_from_IR16(sample, cloud_bam_location):
    
    
    downloaded = False
    tries = 0
    max_tries = 10
    log = True
          
    token = "Uhi5vNyadzCbnU9eSiLhDyBqDGLAwye7RES6QzqLDR2HXWbMKc5Q+UcZGb7X+MamkemomG892FcXfp8HnQkH2g=="
    out_dir = "/home/ionadmin/andreas/projects/ionoxford/TSB_Tools/DataManagement/IR16toIR40migration/bams/" 
    out_file = "%s.zip" % sample
    unzipped_name = cloud_bam_location.split("/")[-1]
    out = out_dir + out_file
    
    curl_cmd = """curl --request POST -d "name=%s" --header "Authorization:%s" https://ir16-retired.ionreporter.iontorrent.com/rest/api/download?name -o %s""" % (cloud_bam_location, token, out)
    
    os.chdir(out_dir)
    
    if os.path.exists(out_dir+unzipped_name):
        print "Already present:", out
    
    else:
        while not downloaded:
            
            tries += 1       
            pexpect.run(curl_cmd)
            
            if zipfile.is_zipfile(out_file):
                unzip_cmd = "unzip -o %s" % (out_file)
                subprocess.call(unzip_cmd, shell=True)
                
                os.rename(out_dir + unzipped_name, out_dir + sample + "_" + unzipped_name)
                
                if log: print "Try Nr. %i successfull!" % (tries)
                downloaded = True
            
            else:
                pass
                if log: print "%i" % (tries),
            
#             try:
#                 os.chdir(out_dir)
#                 if tries == 1 and log:
#                     print '-'*40
#                     print curl_cmd
#                     print 
#          
#                 if log: print "Try %i for %s starting..." % (tries, sample)
#                 error = pexpect.run(curl_cmd)
#                 
#                 if log: print "Out for try %i for %s:" % (tries, sample)
#                 if log: print error
#                 
#                 if "remaining" in error:
#                     if log: print "Try Nr. %i failed with remaining bytes to read." % (tries)
#                     
#                 else:
#                     unzip_cmd = "unzip -o %s" % (out_file)
#                     subprocess.call(unzip_cmd, shell=True)
#                     
#                     unzipped_name = cloud_bam_location.split("/")[-1]               
#                     os.rename(out_dir + unzipped_name, out_dir + sample + "_" + unzipped_name)
#                     
#                     if log: print "Try Nr. %i successfull!" % (tries)
#                     downloaded = True
#                     
#             except:
#                 pass
#                 if log: print "Try Nr. %i failed" % (tries)
            
            if tries > max_tries:
                print "Maximum tries reached for %s, aborting" % (sample)
                break
    
    if downloaded:
        return out_dir + sample + "_" + unzipped_name
    else:
        return False

def upload_bam_to_IR16(sample_name, sample_path):
    
    mypassword = "y71ys71\n"
    config_file = "wtc_config.txt"
    
    irucli_cmd = "/home/ionadmin/IonReporterUploader-cli/bin/irucli.sh -c /home/ionadmin/IonReporterUploader-cli/%s -sn %s -sp %s -sg Unknown" % (config_file, sample_name, sample_path) 
    
    #print irucli_cmd
    print pexpect.run(irucli_cmd, events={'lifetech.com :': mypassword}) 
    
    ######################################################################################
    # update list of finished uploads
    
    uploaded_bam_file = "/home/ionadmin/andreas/projects/ionoxford/TSB_Tools/DataManagement/IR16toIR40migration/finished_uploads.txt"
    uploaded_bams = [x.split("\t")[2] for x in open(uploaded_bam_file).readlines()]
    
    logfile = "/home/ionadmin/andreas/projects/ionoxford/TSB_Tools/DataManagement/IR16toIR40migration/log.txt"
    logrows = [row for row in open(logfile).readlines() if "uploaded file" in row and "bam" in row]
    
    with open(uploaded_bam_file, "a") as bamfile:
        for row in logrows:
            datestamp = str(datetime.datetime.now())
            new_uploaded_bam = row.split(" uploaded file ")[1]
            
            if new_uploaded_bam not in uploaded_bams:
                new_row = [datestamp, sample_name, new_uploaded_bam]
                bamfile.write("\t".join(new_row))
                
##################################################################################################################################################################

if __name__ == '__main__':
    
    input_list = "head_quasar_to_migrate.txt"
    
    input_rows = [x.strip().split("\t") for x in open(input_list).readlines()]

    for sample_name, cloud_bam_location in input_rows:
        print '-'*40
        print "Starting", sample_name
        downloaded_file = download_bam_from_IR16(sample_name, cloud_bam_location)
        
#         if downloaded_file:
#             print "Download ok:", sample_name, downloaded_file
#             upload_bam_to_IR16(sample_name, downloaded_file)