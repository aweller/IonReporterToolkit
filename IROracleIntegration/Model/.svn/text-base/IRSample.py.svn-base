'''
Created on 11 May 2012

@author: wooda1
'''

import Model.Sample as Sample

class IRSample(Sample.Sample):
    '''
    classdocs
    '''
                                
    def __init__(self,irsample_id=None,ir_analyses=[],run_id=None,sample_filepath=None,file_type=None,
                 chip_id=None,chip_type=None,device_id=None,qc_file_path=None,lib_prep=None, 
                 promo=None,status=None,org=None,imported_by=None,pathology=None,
                 pathology_summary=None,gender=None,barcode=None):
        '''
        Constructor
        '''
        super(IRSample, self).__init__(irsample_id)
        self.ir_analyses = ir_analyses
        self.run_id = run_id
        self.sample_filepath = sample_filepath
        self.file_type = file_type
        self.chip_id = chip_id
        self.chip_type = chip_type
        self.device_id = device_id
        self.qc_file_path = qc_file_path
        self.lib_prep = lib_prep
        self.promo = promo
        self.status = status
        self.org = org
        self.imported_by = imported_by
        self.pathology = pathology
        self.pathology_summary = pathology_summary
        self.gender = gender
        self.barcode = barcode
   
    def print_sample_info(self):
        
        info_list = [
                     self.sample_id,
                     self.file_type,
                     self.sample_filepath
                    ]
        info_string = ",".join([str(info) for info in info_list])
        
        return info_string
        