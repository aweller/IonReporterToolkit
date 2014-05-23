'''
Created on 11 May 2012

@author: wooda1
'''

class Analysis:
    '''
    classdocs
    '''
                                
    def __init__(self,ir_version=None,
                 t_sample=None,n_sample=None,analysis_name=None,workflow=None,
                 status=None,user=None,analysis_date=None):
        '''
        Constructor
        '''
        self.ir_version = ir_version
        self.t_sample = t_sample
        self.n_sample = n_sample
        self.analysis_name = analysis_name
        self.workflow = workflow
        self.status = status
        self.user = user
        self.analysis_date = analysis_date
     
    def print_analysis_info(self):
        
        info_list = [
                     self.ir_version,
                     self.t_sample,
                     self.n_sample,
                     self.analysis_name,
                     self.workflow,
                     self.status,
                     self.user,
                     self.analysis_date,
                    ]
        info_string = ",".join([str(info) for info in info_list])
        
        return info_string        