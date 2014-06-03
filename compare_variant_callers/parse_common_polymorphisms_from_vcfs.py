import variant_class as vc
import sys
import os

target_folder = sys.argv[1]
target_files = [x for x in os.listdir(target_folder) if x.endswith("vcf")]

polys = {}

###########################################################################################################

for filename in target_files:
    with open(target_folder + filename) as vcf:
        
        for row in vcf:
            if row[0] == "#": continue
            var = vc.VCFrow(row, None, filename.split(".")[0])

            
            if all([int(var.FAO)>50, int(var.FRO)+int(var.FAO)>500]):
             
                if not polys.get(var.chrompos):
                    polys[var.chrompos] = {"chrompos":var.chrompos, "all":0, "CHP1_IR14":0,"CHP2_IR14":0,"CHP1_IR16":0,"CHP2_IR16":0}
                 
                polys[var.chrompos]["all"] += 1
                 
                if "CHP1" in filename and "IR14" in filename:
                    polys[var.chrompos]["CHP1_IR14"] += 1
                     
                elif "CHP2" in filename and "IR14" in filename:
                    polys[var.chrompos]["CHP2_IR14"] += 1
                     
                elif "CHP1" in filename and "IR16" in filename:
                    polys[var.chrompos]["CHP1_IR16"] += 1
                     
                elif "CHP2" in filename and "IR16" in filename:
                    polys[var.chrompos]["CHP2_IR16"] += 1                           
                 
#     print target_folder + filename, "done"
     
###########################################################################################################
     
rows = polys.values()
keys = ["chrompos", "all", "CHP1_IR14","CHP2_IR14","CHP1_IR16","CHP2_IR16"]
             
for chrompos, row in polys.iteritems():
    values = [str(row[x]) for x in keys]
     
    print "\t".join(values)

