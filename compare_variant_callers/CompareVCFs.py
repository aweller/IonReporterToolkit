#
# CompareVCFs
#
# Find differences between the output of 2 variant callers on the same sample.
#
##########################################################################################################################
#
# expects a folder of vcf files (+ their annotation tsvs) downloaded from IonReporter with the following filename format:
#
# G153317Q_v2_IR16.vcf (+ G153317Q_v2_IR16.tsv)
# G153317Q_v2_IR40.vcf (+ G153317Q_v2_IR40.tsv)
#
# pairwise compares the vcfs that differ only in the IR16/IR40 and creates several output files:
# - all positions
# - all variants (no ref positions)
# - actionable variants (only variants with protein impact)
#
# usually the actionable variants are then combined into one file ("cat *action* > all_Samples.tsv"),
# loaded into Excel and analysed by hand to explain the differences
#
##########################################################################################################################
#
# Disclaimer:
# This script is highly optimized for comparison on IR14 vs IR16 vs IR40.
# New versions of IR will very likely break something due to new vcf fields, different annotation file layouts or similar.
# Proceed with caution!
#
##########################################################################################################################

import sys
import variant_class as vc
import parser_functions as parser
import os
   
def run_all_similar_files_in_folder(foldername, output_dir):                
    """
    Find all pairs of files in a folder (if they have the same sample name)
    """
    
    all_files = [x for x in os.listdir(foldername) if x.endswith(".vcf")]
    pairs = []
    
    for first in all_files:
        run = first.split("_")[0] +"_"+first.split("_")[1]
        
        pair = [x for x in all_files if run in x]
        
        if len(pair) == 1:
            pair = [pair[0], pair[0]]
        
        pair.sort()
        
        if pair not in pairs and pair[0] != pair[1]:
            pairs.append(pair)
    
    #############################################################
    
    for pair in pairs:
        print "-" * 100
        print pair
        run_vcf_comparison(foldername, pair[0], pair[1], output_dir)  
       
    
def run_vcf_comparison(foldername, oldfile, newfile, output_dir):
    """
    Compare 2 vcfs with each other and print the results to different output files depending on variant status.
    """
    
    variants = {}
    comp_name = "".join([oldfile.split(".")[0], "_vs_", newfile.split(".")[0]])
    
    ####################################
    # collect data

    with open(foldername+oldfile) as old:
        
        annotation_file = oldfile.split(".")[0] + ".tsv"
        datasets = parser.parse_datafiles(foldername+annotation_file) 
        
        for row in old:
            if row[0] == "#" or "IMPRECISE" in row: continue
            var = vc.VCFrow(row, datasets, oldfile.split(".")[0])
            
            #cutoffs = [["DP", ">", 10], ["DP", "<", 15]]
            #print var.passes_qc(cutoffs), row,
            
            variants[var.chrompos] = vc.VariantComparison()
            variants[var.chrompos].add_old(var)
    
    with open(foldername+newfile) as new:
        
        annotation_file = newfile.split(".")[0] + ".tsv"
        datasets = parser.parse_datafiles(foldername+annotation_file) 
        
        for row in new:
            if row[0] == "#" or "IMPRECISE" in row: continue
            var = vc.VCFrow(row, datasets, newfile.split(".")[0])
            var.chrompos
    
            if not variants.get(var.chrompos):
                variants[var.chrompos] = vc.VariantComparison()
                variants[var.chrompos].add_new(var)
                
            else:
                variants[var.chrompos].add_new(var)
    
    print "parsed variants for %i locations" % (len(variants))
    
    ####################################
    # print 
    
    dataset = vc.ComparisonDataset(variants.values())
    dataset.print_to_file(comp_name, "comparison", "all_positions", output_dir)
    dataset.print_to_file(comp_name, "comparison", "actionable_variants", output_dir)
    dataset.print_to_file(comp_name, "comparison", "all_variants", output_dir)

def main():
    foldername = sys.argv[1]
    output_dir = sys.argv[2]

    run_all_similar_files_in_folder(foldername, output_dir)

##########################################################################################################################
##########################################################################################################################


if __name__ == '__main__':
    main()

