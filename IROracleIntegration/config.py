config = {
    #Log
    'log_file':'IROracleIntegration.log',
    
    #authentication token
    'token':'Uhi5vNyadzCbnU9eSiLhDyBqDGLAwye7RES6QzqLDR2HXWbMKc5Q+UcZGb7X+MamkemomG892FcXfp8HnQkH2g==',
    
    # Location specific files
    
    #'lab_sample_list':'Input_files/NHS_samples_nov13.csv',
    #'sample_bc_mapping':'Input_files/NHS_2_2_samples.csv',
    #'output_file':'Output_files/NHS_IR_Analysis_Info.csv',

    'lab_sample_list':'Input_files/quasar_samples.csv',
    'sample_bc_mapping':'None',
    'output_file':'Output_files/WTC_IR_Analysis_Info.csv',

    
    # General Input Files
    'ir_sample_list':'Input_files/IonReporter_Sample_Data_26_11_13.csv',
    'ir14_analysis_file':'Input_files/analysis_summary_14.csv',
    'ir16_analysis_file':'Input_files/analysis_summary_16.csv',
    
    # General Output Files
    'output_path':'Output_files/',
    
    #URL for all analyses
    'all_analysis_16_base_url':'https://ir16-retired.ionreporter.lifetechnologies.com/ir16/rest/sample/getcontainers',
    'all_analysis_14_base_url':'https://ir16-retired.ionreporter.lifetechnologies.com/ir14/rest/sample/getcontainers',
    #'all_analysis_40_base_url':''
    
    #URL for all samples
    'all_samples_1x_base_url':'https://ir16-retired.ionreporter.lifetechnologies.com/ir16/rest/sample/metadata?sampleName='
}


