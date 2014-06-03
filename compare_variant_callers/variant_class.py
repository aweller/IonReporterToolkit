# this file contains 3 classes needed for CompareVCFs.py
#
# the classes are nested into each other:
#    a VCFrow instance contains information on a single row and it's fields
#    a VariantComparison instance contains 2 VCFrows and compares them
#    a ComparisonDataset instance contains all VariantComparison for a sample
#    
#########################################################################################################

import sys
import re
import parser_functions as parser
import operator
import scipy.stats

class BasicRowParser:

    """
    Baseclass to access Contig, position and reference
    """

    def __init__(self, row, startpos=None):

        """
        The optional startpos argument is used to get rid of any extra fields before the actual vcf part of the rows
        """

        row = row.rstrip("\n")

        self.row = row
        self.fields = row.split("\t")

        if startpos is not None:

            self.fields = self.fields[startpos:]

        if row[0] != "#":

            self.valid_row = True

            self.chrom = self.fields[0]
            self.pos = int(self.fields[1])
            self.ref = self.fields[3]

            self.chrompos = self.chrom +"\t"+ str(self.pos)
        else:
            self.valid_row = False


        ##########################################################
        # type questions
    
        def is_valid_row(self):
            """ test if the row contains all fields """
            return self.valid_row
    
        def is_ref_known(self):
            """ test if the ref is actually a base and not just "N" """
    
            if "N" in self.ref:
                return False
            else:
                return True
    
        def get_conpos(self):
    
            return self.conpos
    
        def get_con(self):
            return self.con
    
        def get_pos(self):
            return self.pos
    
        def get_alt(self):
            return self.alt
    
        def get_ref(self):
            return self.ref
    
        def cutoff_test(self, tested_trait, direction, cutoff):
            """
            Tests if the tested trait is [above/below] the cutoff
            """
    
            if direction == "max":
                if tested_trait <= cutoff:
                    return True
    
            elif direction == "min":
                if tested_trait >= cutoff:
                    return True
            else:
                return False


##############################################################################################################################################################################
##############################################################################################################################################################################
##############################################################################################################################################################################

class VCFrow(BasicRowParser):

    """
    Each instance corresponds to one variant site (= one row in a .vcf file)
    chr2    141771058    .    T    A    204.56    PASS    AO=95;DP=228;FAO=95;FRO=228;FR=.;FRO=133;FSAF=50;FSAR=45;FSRF=73;FSRR=60;FWDB=0.0166299;HRUN=4;LEN=1;MLLD=364.269;RBI=0.0288687;REFB=0;REVB=0.0235977;RO=133;SAF=50;SAR=45;SRF=71;SRR=62;SSEN=0;SSEP=0;STB=0.513213;SXB=0.0524288;TYPE=snp;VARB=0.0180844;OID=.;OPOS=141771058;OREF=T;OALT=A;OMAPALT=A    GT:GQ:DP:FRO:RO:FRO:AO:FAO:SAR:SAF:SRF:SRR:FSAR:FSAF:FSRF:FSRR    0/1:99:228:228:133:133:95:95:45:50:71:62:45:50:73:60
    'chr1\t115256528\t.\tT\t.\t100.0\tPASS\tHS;genes=NRAS;omim=164790;cosmic=585, 586, 587;dbsnp=rs121913255\tGT:GQ:GL:DP:FRO:AD:APSD:AST:ABQV\t0/0:90.22:-0.0,-999.0,-999.0:1437:1365:1363:726:34:27
    """

    def __init__(self, row, datasets=None, filename=None, startpos=None):
        
        BasicRowParser.__init__(self, row, startpos)
        
        self.filename = filename
        self.samplename = filename.split("_")[0]
        if filename[0] == "F": # the special case of the F3_24023_v1_CHP1_IR14 files
            self.samplename = "_".join(filename.split("_")[:2])
        
        if datasets == None:
            # create fake datasets which the class expects 
            datasets = {}
            datasets["annotations"] = {}
        self.datasets = datasets

        # the following need to exist in all instances because they are queried in the cutoffs
        self.type = "None"
        self.func = "None"
        self.DP = 0
        self.FAO = 0
        self.FRO = 0
        self.FR = "."
        
        if "FR=" not in row and "FreqN" not in row: 
            self.ir_version = "14"
        else:
            self.ir_version = "16"
            
        self.alt = self.fields[4]

        try: self.qual = float(self.fields[5])
        except: self.qual = 0.0
        
        self.called = self.fields[6]
    
        # info field
        self.info = {}
        self._fullinfo = self.fields[7]
        infofields = self._fullinfo.split(";")[1:] # because the first field indicates a hotspot
        for field in infofields:
            if "=" in field:
                self.info[field.split("=")[0]] = field.split("=")[1]        
        for key, value in self.info.iteritems():
             
            if key == "FAO":
                values = [int(x) for x in value.split(",")]
                value = max(values) # as FAO can be a list for each allele
                
            if key in ["DP"]:
                value = int(value)
            setattr(self, key, value)
                
        # format field
        self._formatkeys = self.fields[8]
        self._formatvalues = self.fields[9]
        self.format = {}
        for key,value in zip(self._formatkeys.split(":"), self._formatvalues.split(":")):
            
            if key == "FAO":
                values = [int(x) for x in value.split(",")]
                value = max(values) # as FAO can be a list for each allele
            self.format[key] = value
            
        for key, value in self.format.iteritems():
            setattr(self, key,value)
    
   
        #print self.__dict__
    
        self.in_hotspot = "HOTSPOT" if self.is_in_hotspot() else "DENOVO"
        self.in_blacklist = "BLACK" if self.is_blacklisted() else "WHITE"
        
        # annotation
        
        if self.datasets["annotations"].get(self.chrompos):
            for key, value in self.datasets["annotations"][self.chrompos].iteritems():
                if key not in ["alt"]:
                    setattr(self, key,value)
                    
        # poly status
        
        if parser.poly_covered: # a file of polymorphisms was parsed
            if parser.poly_covered.get(self.chrompos):
                self.poly_covered = parser.poly_covered[self.chrompos]
            else:
                self.poly_covered = "NA"   
    
            if parser.poly_variant.get(self.chrompos):
                self.poly_variant = parser.poly_variant[self.chrompos]
            else:
                self.poly_variant = "NA"
        else:
            self.poly_covered = "NA"
            self.poly_variant = "NA" 

        
        # variant status
        self.is_variant = False
        
        if "," in self.alt:
            self.alt1 = self.alt.split(",")[0]
            self.alt2 = self.alt.split(",")[1]
            
            if self.alt1 == self.alt2:
                self.alt_consensus = self.alt1
            else:
                self.is_variant = True
                self.alt_consensus = self.alt
        
        else:
             self.alt_consensus = self.alt
            
        
        if self.ref != self.alt_consensus and self.alt_consensus != "." and self.FR == ".":
            self.is_variant = True
        
        
        # get alternate allele percentage 
        
        self.alt_percent = 0 
        
        if self.ir_version == "16":
            
            self.total_reads = int(self.FAO) + int(self.FRO)
             
            if self.total_reads > 1:
                self.alt_percent = round(int(self.FAO)/float(self.total_reads), 2) 
        
        elif self.ir_version == "14":            
            if "AD" in row: 
            
                allele_reads = self.AD.split(",")
                
                if len(allele_reads) >1:
                
                    self.FRO = int(allele_reads[0]) 
                    self.FAO = int(allele_reads[1]) 
                
                    self.total_reads = int(self.FAO) + int(self.FRO)
                     
                    if self.total_reads > 1:
                        self.alt_percent = round(int(self.FAO)/float(self.total_reads), 2) 

    def passes_custom_cutoff(self, string_filterset):
        """ Evaluates a list of cutoffs passed as an argument and returns True if all are met """        
        filterset = []
        for item in string_filterset:
            try: filterset.append(eval(item))
            except: filterset.append(False)
        return all(filterset)


    def passes_cutoff(self, filter_code):
        """ Evaluates a list of cutoffs and returns True if all are met """
        try:
            filterset_dict = {"all_positions":[True],
          "all_variants":[self.is_variant == True],
          "actionable_variants":[self.is_variant == True, 
                                 self.in_blacklist == "WHITE", 
                                 "exon" in self.loc, # and "exonic_nc" not in self.loc, 
                                 "syn" not in self.func, 
                                 "ref" not in self.func, 
                                  self.ir_version == "14" or int(self.FAO)>50,
                                  int(self.FRO)+int(self.FAO)>500, 
                                  self.FR == "."],
                              
                              
          "indels":[self.is_variant == True, self.type == "del" or self.type == "in" , "exon" in self.loc]
          }
            return all(filterset_dict[filter_code])
         
        except:
            return False

    def is_in_hotspot(self):
        """ Parses a hotspot bed file and checks if the variant falls into a hotspot """
        in_hotspot = False
        hotspots = parser.parse_hotspot_bed()
    
        if hotspots.get(self.chrom):    
            chrom_hotspots = hotspots[self.chrom]
    
            for interval in chrom_hotspots:    
                if interval[0] <= self.pos <= interval[1]:
                    in_hotspot = True
                    break
    
        return in_hotspot    
    
    def is_blacklisted(self):
        """ Parses a blacklist of false-positives and common polymorphisms and checks the chrompos"""
        
        in_blacklist = False        
        if self.chrompos in parser.blacklist:
            in_blacklist = True
        
        return in_blacklist
    
    def get_annotations(self): # not used right now
        annotations = parser.annotations

        try:
            annotation = "_".join(annotations[self.chrompos])
        except: 
            annotation = False
        
        return annotation
        

##############################################################################################################################################################################
##############################################################################################################################################################################
##############################################################################################################################################################################

class VariantComparison:
    """ Takes an old and a new variant of the class VCFrow and compares them """

    def __init__(self):
        self.old = None
        self.new = None
    
        self.chrompos = None
        self.ref = None
    
    def add_old(self, var):
        self.old = var
        self.chrompos = var.chrompos
        self.ref = var.ref

    def add_new(self, var):
        self.new = var
        self.chrompos = var.chrompos
        self.ref = var.ref

    ##########################################################
    # print options    
    
    def _fetch_fields(self, old_or_new, target_fields):
        """ Fetch all individual field for this row"""
        
        returned_fields = []
        for target_field in target_fields:
                if target_field in [",", "\t"]:
                    returned_fields.append(target_field)
                else:
                    try:
                       returned_fields.append(str(getattr(old_or_new, target_field)))
                    except:
                       returned_fields.append("-")         
        return returned_fields
    
    def check_call_similarity(self):
        """ Decides whether a position is a GAIN of call, LOSS of call or SAME"""
    
        if self.old and not self.new:
            self.similarity = "LOSS"
        elif not self.old and self.new:
            self.similarity = "GAIN"
        else:
            if not self.old.is_variant and self.new.is_variant:
                self.similarity = "GAIN"                
            elif self.old.is_variant and not self.new.is_variant:
                self.similarity = "LOSS"  

            else:
                self.similarity = "SAME"

    def check_allele_freq_diff(self):
        """ Compares the variant allele freqs between the samples"""
    
        if not self.old or not self.new:
            self.freq_diff = "NA"
            self.pvalue = "NA"
            
        else:
            old_frq = self.old.alt_percent
            new_frq = self.new.alt_percent
            
            if old_frq == 0 or new_frq == 0:
                self.freq_diff = "NA"
            
            else:
                self.freq_diff = abs(old_frq-new_frq)            
        
    def fetch_output_row(self, common_fields_to_print, fields_to_print, filter_code):
        """ Fetch all requested output fields"""
    
        old_passed_cutoff = False
        new_passed_cutoff = False

        self.check_call_similarity()
        self.check_allele_freq_diff()
                
        if self.old:
            common_fields = self._fetch_fields(self.old, common_fields_to_print)
            if self.old.passes_cutoff(filter_code):
                old_passed_cutoff = True
        
        if self.new:
            common_fields = self._fetch_fields(self.new, common_fields_to_print)
            if self.new.passes_cutoff(filter_code):
                new_passed_cutoff = True           
        
        old_fields = self._fetch_fields(self.old, fields_to_print)
        new_fields = self._fetch_fields(self.new, fields_to_print)
    
        outfields = "\t".join( common_fields + [self.similarity, str(self.freq_diff)] + old_fields + new_fields )
                
        if not old_passed_cutoff and not new_passed_cutoff:
            outfields = None
        
        return outfields
    
     

##############################################################################################################################################################################
##############################################################################################################################################################################
##############################################################################################################################################################################

class ComparisonDataset:
    """ Takes a collection of several VariantComparisons, performs output formatting and summaries """

    def __init__(self, comparison_list):
        self.allcomps = comparison_list
        self.allcomps.sort(key=operator.attrgetter('chrompos'))
    
        self.chromposes = [var.chrompos for var in self.allcomps]
        self.chromposes.sort()
                
    def create_header_row(self, fields_to_print, comp_name):
             
        oldname = comp_name.split("_vs_")[0]
        newname = comp_name.split("_vs_")[1]
        
        sample =  comp_name.split("_")[0]
             
        header = [sample, ]
        header.extend(fields_to_print[0][1:]) # as the first item is "samplename" which was already included
        header.extend(["Comparison", "Freq_Diff"])
        header.extend(fields_to_print[1])
        header.extend(fields_to_print[1])
        header.extend("\n")

        for n,i in enumerate(header):
            if i== "chrompos":
                header[n]= "chrom\tpos"
        
        header_row = "\t".join(header)
                
        return header_row
        

    def print_to_file(self, comp_name, field_code, filter_code, output_dir):

        field_dict = {
            "short_rows": [["filename", "chrompos", "ref", "gid", "loc", "func", "in_blacklist", "in_hotspot"], ["\t", "alt", "is_variant", "GT", "GQ", "GL" ,"DP", "FRO", "AD", "APSD","AST","ABQV"]],
            "full_rows": [["chrompos", "ref"],["alt", "call_state", "in_hotspot" ,"_fullinfo"]], 
            "comparison":[["samplename", "chrompos", "ref", "gid", "cds", "func", "in_hotspot", "poly_covered", "poly_variant"],["filename", "alt", "qual", "FR", "FRO", "FAO", "alt_percent"]]
        }
        
        # translate field code to actually requested fields
        fields_to_print = []
        if field_dict.get(field_code):
            fields_to_print.extend(field_dict[field_code])
        else:
            print "Sorry, couldnt translate ", field_code
                
        # fetch the requested fields for each comparison row 
        output_name = "%s_%s_%s.tsv" % (comp_name, field_code, filter_code) 
        
        with open(output_dir + output_name, "w") as output_file:
            
            output_file.write(self.create_header_row(fields_to_print, comp_name))
            printed_rows = 0
            
            for comp in self.allcomps:
                outrow = comp.fetch_output_row(fields_to_print[0], fields_to_print[1], filter_code)         
                if outrow:
                    output_file.write(outrow + "\n")
                    printed_rows += 1
                    
                    if filter_code == "actionable_variants":
                        print outrow
                        
            print "Printed %i variants to %s%s" % (printed_rows, output_dir, output_name)
    



