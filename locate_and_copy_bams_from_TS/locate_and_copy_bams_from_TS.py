#
# Locate, copy and rename bams inside an Ion Torrent TorrentServer filesystem
# 
########################################################################################
#
# Parse a tab-seperated input file of the format
#
# Sample    Tumor/Normal    Barcode Run
# BC451-T-HP	T	    1	    OX1-317
# BC615-T-HP	T	    2	    OX1-311
#
# then copy and rename all aligned bams to an export folder and
# create an uploading list for the IRUcli
#
########################################################################################
#
# Input arguments:
# 1. The input file (see above)
#
# The name of 2 output files that will store command (to be executed as shell scripts)
# 2. IRUcli commands (will be created for UNALIGNED bams for uploading to Ion Reporter)
# 3. copy commands (will be created for ALIGNED bams for local research use, e.g. coverage analysis)
#
########################################################################################
#
# You might need to modify 2 parts of this script:
# 1. the locations list, which is a list of all TS folder where bams might be kept
# 2. the unifiy_sample_name function, which reformats sample names (specific to the WTCHG Quasar project)
#
########################################################################################


import sys
import os
import subprocess
import pprint

def main():

    locations = ["/well/brc/archivedReports/",
                 "/cluster/pgmarchive/",
                 "/cluster/pgmarchive/archivedReports/",
                "/results/OX1/",
                "/results/OX2/",
                "/cluster/pgmarchive/archivedReports/",
                "/gpfs1/well/brc/archivedReports/",
                 "/results/analysis/output/Home/",
                 "/media/pgmarchive/archivedReports/"
                ]
    
    tumor_normal_file = sys.argv[1]
    irculi_input = sys.argv[2] #  an empty file where the upload commands will be stored
    copy_script = sys.argv[3] # an empty file where the cp commands for the aligned bams will be stored
    
    all_aligned_bams, all_unaligned_bams = fetch_all_bam_locations(locations)
    
    aligned_output = open(copy_script, "w")
    unaligned_output = open(irculi_input, "w")
    
    ########################################################################################
    # parse all samples into a dict
    
    sample_info = {}
      
    with open(tumor_normal_file) as all_files:
        for row in all_files:
            f = row.strip().split("\t")
            if f[0] == "Run": continue #header 
            
            #sample, run, tumour_barcode, normal_barcode = f
            sample, tn, barcode, run = f
            
            if not sample_info.get(sample):
                sample_info[sample] = dict(run = None, tumour_barcode = "XXX", normal_barcode = "XXX", uni_sample = unifiy_sample_name(sample))
            sample_info[sample]["run"] = run
            
            if "T" in tn:
                sample_info[sample]["tumour_barcode"] = barcode
            elif "N" in tn:
                sample_info[sample]["normal_barcode"] = barcode

    
    ########################################################################################
    # try to fetch the locations for all samples        
    
    all_samples = sample_info.keys()
    all_samples.sort()
    
    for sample in all_samples:
        s = sample_info[sample]
        run, tumour_barcode, normal_barcode, uni_sample = s["run"], s["tumour_barcode"], s["normal_barcode"], s["uni_sample"] 
        
        tumor_found, normal_found = search_for_sample_in_all_bams(all_unaligned_bams, sample, run, tumour_barcode, normal_barcode, uni_sample, "unaligned", unaligned_output)            
        if not tumor_found and not normal_found:
            print "Missed unaligned", uni_sample, run, tumour_barcode, normal_barcode, tumor_found, normal_found
            
        tumor_found, normal_found = search_for_sample_in_all_bams(all_aligned_bams, sample, run, tumour_barcode, normal_barcode, uni_sample, "aligned", aligned_output)
        if not tumor_found and not normal_found:
            print "Missed aligned", uni_sample, run, tumour_barcode, normal_barcode, tumor_found, normal_found
 
    aligned_output.close()
    unaligned_output.close()

################################################################################################################################################################################

def search_for_sample_in_all_bams(all_bams, sample, run, tumour_barcode, normal_barcode, uni_sample, bam_type, output):
    """
    Try to locate a Tumor/Normal pair from the list of valid bams   
    """
    
    tumor_found = False
    normal_found = False
    
    #print "running", sample, run, tumour_barcode, normal_barcode, uni_sample, bam_type, output
    
    for bam in all_bams:
        result = None
        
        if "Auto_user_" + run in bam and "IonXpress_" + pad(tumour_barcode) in bam:
            if not tumor_found:
                tumor_found = True

                if bam_type == "unaligned": # for uploading with the IRUcli
                    result = ",".join([uni_sample + "_T", bam,"Unknown"]) 
                elif bam_type == "aligned": # for downstream analysis
                    result = "cp -n %s /results/analysis/output/Home/to_export_quasar_tumor_bams/%s" % (bam, uni_sample + "_T.bam")
            
        elif "Auto_user_" + run in bam and "IonXpress_" + pad(normal_barcode) in bam:
            
            if not normal_found:
                normal_found = True
                if bam_type == "unaligned": # for uploading with the IRUcli
                    result = ",".join([uni_sample + "_N", bam,"Unknown"]) 
                elif bam_type == "aligned": # for downstream analysis
                    result = "cp -n %s /results/analysis/output/Home/to_export_quasar_normal_bams/%s" % (bam, uni_sample + "_N.bam")
        
        if result:
            output.write(result + "\n")
             
        if tumor_found and normal_found:
            break    
    
    #print "running", tumor_found, normal_found, result
    
    return tumor_found, normal_found


def fetch_all_bam_locations(locations):
    """
    Walk through the folders sepcifiec in 'locations' and create a list of all valid bams  
    """
    
    all_aligned_bams, all_unaligned_bams = [], []
    
    for loc in locations:
        if not os.path.exists(loc): 
            print "wrong path",  loc
        
        sample_folders = os.listdir(loc)
        
        for sample_folder in sample_folders:
            
            #####################################################################################
            # add bams from the main folder of the run
            
            link_folder = loc+sample_folder
            if not os.path.isdir(link_folder): continue
            
                
            links_in_download_folder = os.listdir(link_folder)
            aligned_bams_in_download_folder = [link_folder +"/"+ x for x in links_in_download_folder 
                                       if x.endswith(".bam") 
                                       and "Ion" in x 
                                       and "basecaller" not in x]
            
            unaligned_bams_in_download_folder = [link_folder +"/"+ x for x in links_in_download_folder 
                                       if x.endswith(".bam") 
                                       and "Ion" in x 
                                       and "basecaller" in x]
        
            all_aligned_bams.extend(aligned_bams_in_download_folder)
            all_unaligned_bams.extend(unaligned_bams_in_download_folder)

            #####################################################################################
            # add bams from the subfolder download_links
            
            download_link_folder = loc+sample_folder+"/download_links/"
            if not os.path.isdir(download_link_folder): continue
                
            links_in_download_folder = os.listdir(download_link_folder)
            bams_in_download_folder = [download_link_folder + x for x in links_in_download_folder 
                                       if x.endswith(".bam") 
                                       and "Ion" in x 
                                       and "basecaller" not in x]
            
            unaligned_bams_in_download_folder = [download_link_folder + x for x in links_in_download_folder 
                                       if x.endswith(".bam") 
                                       and "Ion" in x 
                                       and "basecaller" in x]
        
            all_aligned_bams.extend(aligned_bams_in_download_folder)
            all_unaligned_bams.extend(unaligned_bams_in_download_folder)
    
    #####################################################################################
    # weed out all bams with a broken symlink from '/download_links' to the actual bam folder
    # this happens when bams get moved to backup but the symlinks don't get repaired
    
    all_aligned_bams_working_links, all_unaligned_bams_working_links = [], []
    
    for bam in all_aligned_bams:
        try:
            os.stat(bam)
            all_aligned_bams_working_links.append(bam)
        except:
            pass

    for bam in all_unaligned_bams:
        try:
            os.stat(bam)
            all_unaligned_bams_working_links.append(bam)
        except:
            pass
        
    return all_aligned_bams_working_links, all_unaligned_bams_working_links

          
def pad(number):
    no = str(number)
    
    if len(no) == 3:
        return no
    elif len(no) == 2:
        return "0" + no
    elif len(no) == 1:
        return "00" + no
    else:
        return no
    
def unifiy_sample_name(sample):
    
    if sample[0] == "Q":
    
        plate_loc = sample.replace("-", "_").split("_")[1]
        
        if "pl2" in sample.lower():
            plate = "PL2"
        elif "pl3" in sample.lower():
            plate = "PL3"
        elif "pl4" in sample.lower():
            plate = "PL4"
        else:
            plate = "PL1"
        
        if plate_loc[1:3].isdigit(): #  e.g. E08, correct order
            plate_loc = plate_loc[:3] #remove trailing letters
            
        else: # wrong order
            if len(plate_loc) == 2: # eg. 8E
                plate_loc = plate_loc[1] + "0" + plate_loc[0]
            elif len(plate_loc) == 3: # eg. 10E
                plate_loc = plate_loc[2] + plate_loc[:2]
        
        new_sample = "_".join(["Q2"+plate, plate_loc])
    
        return new_sample
    
    else:
        return sample
        
#####################################################################################

if __name__ == '__main__':
    main()
