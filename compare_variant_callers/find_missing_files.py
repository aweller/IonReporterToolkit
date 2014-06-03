
# G154409H_v2_CHP1_IR14.tsv

import sys
import os

target_dir = sys.argv[1]

files = [x.rstrip(".vcf") for x in os.listdir(target_dir) if x.endswith("vcf")]

samples = []
chps = ["CHP1", "CHP2"]
irs = ["IR14", "IR16"]

for file in files:
    f = file.split("_")
    
    
    sample = f[0]
    chp = f[2]
    ir = f[3]
    
    samples.append(sample)


for sample in samples:
    
    out = [sample, ]
    
    for ir in irs:        
        for chp in chps:
            
            found = False
            for file in files:
                if file.startswith(sample) and chp in file and ir in file:
                    found = True
#                     print file, chp, ir
            
            if found:  
                out.append("V")
            else:
                out.append("x")
                
    print "\t".join(out)