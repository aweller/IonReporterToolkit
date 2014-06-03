# these functions parse various input files that might be needed for CompareVCFs.py

import json
import re
import os

script_folder = os.path.dirname(os.path.realpath(__file__)) + "/"

def parse_json_cutoffs():
    """
    Parse a json of quality cutoffs that the Torrent Variant Caller uses (to be able to emulate it's filtering).
    """
    
    filename = script_folder + "chp2_somatic_lowstringency.json"
    
    return  json.load(open(filename))
    
def parse_hotspot_bed():
    """
    Parse a bedfile of hotspots, so each variant can be marked as in or out of the hotspot. 
    """
    
    filename = script_folder + "CHP1.HSMv12.1_reqions_NO_JAK2_NODUP.bed"
    
    hotspots = {}
    
    with open(filename) as bed:
        for row in bed:
            if row[0] != "c": continue
            fields = row[:-1].split("\t")
                        
            chrom = fields[0]
            start = int(fields[1])
            stop = int(fields[2])
#             exon = fields[3]
#             gene = fields[5].split("=")[1]
            
            if not hotspots.get(chrom):
                hotspots[chrom] = []
            
            hotspots[chrom].append([start, stop])
            
    return hotspots
            

def parse_blacklist():
    """
    Parse a blacklist of variants that shouldn't be considered. 
    """
    
    filename = script_folder + "blacklist.txt"
    blacklist_chromposes = []
    
    with open(filename) as blacklist:
        for row in blacklist:
            chrompos = row.split()[:2] 
            blacklist_chromposes.append("\t".join(chrompos))
            
    return blacklist_chromposes

def parse_annotation(annotation_file):
    """
    Parse a list of annotated variants, trying to determine the correct layout.
    This might break for IR versions higher than 4.0, so a need parser is needed (see below for 1.4, 1.6 and 4.0).
    """
        
    filename = annotation_file
    annotations = {}
    
    with open(filename) as annotation_file:
        for row in annotation_file:
            if len(row) < 2 or row[0] == "#": continue
            
            if row[0] == "c": # version 14
                fields = row.split()
                chrom = fields[0].split(":")[0]
                posfield = fields[0].split(":")[1]
                pos_regex = re.search("(\d+)", posfield)
                
                pos = "?"
                if pos_regex != None:
                    pos = pos_regex.groups()[0]
                chrompos = chrom +"\t"+ pos
                
                for field in fields[2:]:
                    if not "=" in field: continue
                    
                    key = field.split("=")[0]
                    value = field.split("=")[1]
                    
                    if key in ["func", "cds", "loc", "Minor_Allele_Frequency", "gid"]:                    
                        if not annotations.get(chrompos):
                            annotations[chrompos] = {}
                            
                        annotations[chrompos][key] = value
            
            elif row.split()[2] in ["INDEL", "NOCALL", "REF", "SNV", "type"]: # version 40 full
                fields = row.split()
                chrom = "chr" + fields[0]
                pos = fields[1]
                chrompos = chrom +"\t"+ pos
                
                if not annotations.get(chrompos):
                    annotations[chrompos] = {}

                annotations[chrompos]["ref"] = fields[3]
                annotations[chrompos]["alt"] = fields[5]
                                
                try:
                    annotations[chrompos]["gid"] = fields[6].split(":")[0]
                    annotations[chrompos]["loc"] = fields[8]
                    annotations[chrompos]["func"] = fields[9].split(":")[0].strip("[]")
                    infofield = fields[11]    
                except:
                    pass                                       
                    
                        
            else: # version 16
                fields = row.split()
                chrom = "chr" + fields[0]
                pos = fields[1]
                chrompos = chrom +"\t"+ pos
                
                if not annotations.get(chrompos):
                    annotations[chrompos] = {}
                
                annotations[chrompos]["ref"] = fields[2]
                annotations[chrompos]["alt"] = fields[3]
                
                try:
                    annotations[chrompos]["gid"] = fields[4]
                    annotations[chrompos]["loc"] = fields[6]
                    annotations[chrompos]["func"] = fields[7]
                    infofield = fields[11]    
                except:
                    pass           
        
        return annotations

def parse_poly_database():
    """
    Parse a list of common polymorphisms, i.e. how often a variant appears in all samples 
    """
    
    poly_covered = {} # proper variant with a NHS QC coverage
    
    with open(script_folder + "all_covered_variants_stats.tsv") as polyfile:
        for row in polyfile:
            f = row.split("\t")
            chrompos = f[0] +"\t"+ f[1]
            total_count = f[2]
            
            poly_covered[chrompos] = total_count
    
    poly_variant = {} # any variant that shows an alt allele
    
    with open(script_folder + "all_variants_stats.tsv") as polyfile:
        for row in polyfile:
            f = row.split("\t")
            chrompos = f[0] +"\t"+ f[1]
            total_count = f[2]
            
            poly_variant[chrompos] = total_count
    
    return poly_covered, poly_variant

#############################################################################            

#poly_covered, poly_variant = parse_poly_database()
#json_cutoff = parse_json_cutoffs()

hotspot_bed = parse_hotspot_bed()
blacklist = parse_blacklist()
poly_covered, poly_variant = None, None

def parse_datafiles(annotation_file):
    datasets = {}
    datasets["annotations"] = parse_annotation(annotation_file)
    
    return datasets
    
    
