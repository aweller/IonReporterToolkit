# accepts as input a file of the format
# 
# samplename /path/to/sample.bam
# 
# will then fetch and unpack all of them, retrying any failed downloads if they should happen 
# Parallel processing can be turned on by setting "parallel" to True

import subprocess
from subprocess import Popen, PIPE
import multiprocessing as mp
import os
import pdb
import sys

def run(cmd):
    p = Popen(cmd, stderr=PIPE, stdout=PIPE, shell=True)
    output, errors = p.communicate()
    return errors.split("\r")[-1]  

def fetch_bam(sample, bam_location):
    
    downloaded = False
    tries = 0
    max_tries = 10
                 
    test_sample_name = "TestSample_v2_"
    test_bam_location = "/shared/grdata/Oxford_Cancer_and_Haematology_Centre/data/2013-10-29_12_25_45/v2/G125149H_v1/IonXpress_003_rawlib.basecaller.bam"
    
    token = "Uhi5vNyadzCbnU9eSiLhDyBqDGLAwye7RES6QzqLDR2HXWbMKc5Q+UcZGb7X+MamkemomG892FcXfp8HnQkH2g=="
    out_dir = "/home/ionadmin/andreas/projects/ionoxford/TSB_Tools/fetch_bams/data/" 
    out_file = "%s.zip" % sample
    out = out_dir + out_file
    
    curl_cmd = """curl --request POST -d "name=%s" --header "Authorization:%s" https://ir16-retired.ionreporter.iontorrent.com/rest/api/download?name -o %s""" % (bam_location, token, out)
    
    if os.path.exists(out) and False:
        print "Already present:", out
    
    else:
        while not downloaded:
            tries += 1        

            try:
                os.chdir(out_dir)
                if tries == 1:
                    print '-'*40
                    print curl_cmd
        
                print "Try %i for %s starting..." % (tries, sample)
                error = run(curl_cmd)
                
                print "Out for try %i for %s:" % (tries, sample)
                print error
                
                if "remaining" in error:
                    print "Try Nr. %i failed" % (tries)
                    
                else:
                    unzip_cmd = "unzip -o %s" % (out)
                    subprocess.call(unzip_cmd, shell=True)
                    
                    unzipped_name = bam_location.split("/")[-1]               
                    os.rename(out_dir + unzipped_name, out_dir + sample + "_" + unzipped_name)
                    
                    print "Try Nr. %i successfull!" % (tries)
                    downloaded = True
                    
            except:
                print "Try Nr. %i failed" % (tries)
            
            if tries > max_tries:
                print "Maximum tries reached for %s, aborting" % (sample)
                break
    
    return True
    
#################################################################################################

if __name__ == '__main__':


    parallel = False
    
    if parallel: pool = mp.Pool(processes = 4)
    
    with open(sys.argv[1]) as to_fetch:
        for row in to_fetch:
            f = row.strip("\n").split("\t")
            
            if len(f) == 1:
                f = row.strip("\n").split(",")
            if len(f) == 1:
                f = row.strip("\n").split(" ")
            
            sample, bam_location = f
            
            if parallel:
                pool.apply_async(fetch_bam, args = [sample, bam_location])
                
            else:
                fetch_bam(sample, bam_location)
                
            
    if parallel: pool.close()        
    if parallel: pool.join()        
