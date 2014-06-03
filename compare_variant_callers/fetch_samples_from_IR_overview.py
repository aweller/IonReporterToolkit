
to_fetch = "../data/nhs_to_fetch_for_40.txt"
IR_dump = "/home/ionadmin/andreas/projects/nhs_update_validation/data/all_nhs_datasets/IonReporter_Sample_Data_3_1_2014.csv"

samples = [x[:-2] for x in open(to_fetch).readlines()]

with open(IR_dump) as all_data:
    for row in all_data:
        
        for sample in samples:
            if row.startswith(sample):
                
                print sample, row.split(",")[2]
                break
        
        
