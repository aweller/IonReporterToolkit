import os

for filename in [x for x in os.listdir("all_nhs_datasets") if x.endswith("vcf")]:
    
    f = filename.split("_") 
    
    sample = "_".join(f[:-3])
    chp = f[-2]
    ir = f[-1].rstrip(".vcf")
    
    print "\t".join([filename, sample, chp, ir])