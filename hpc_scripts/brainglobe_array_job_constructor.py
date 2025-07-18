from pathlib import Path
from hpc_scripts.brainglobe_hpc.brainreg_commands import save_brainreg_array_job
from hpc_scripts.brainglobe_hpc.cellfinder_commands import save_cellfinder_array_job

from hpc_scripts.slurm_config import slurm_params

def main():
    atlas = "allen_mouse_10um"
    overwrite_existing=False
    rawdata_directory = Path("/ceph/margrie/slenzi/2025/dr/photometry/rawdata/")   
    serial2p_directory_raw = Path("/ceph/margrie/slenzi/serial2p/whole_brains/raw/")
    array_job_outpath="/ceph/margrie/slenzi/batch_scripts2/" 
    
    model_path = None  #CELLFINDER ONLY: if you have your own custom model

    save_brainreg_array_job(
                            rawdata_directory = rawdata_directory,   
                            serial2p_directory_raw = serial2p_directory_raw,
                            array_job_outpath=array_job_outpath, 
                            atlas=atlas,
                            overwrite_existing=overwrite_existing,
                            slurm_params=slurm_params,
                            ceph_path_root=None,
                            )
    

    save_cellfinder_array_job(
                              rawdata_directory = rawdata_directory,   
                              serial2p_directory_raw = serial2p_directory_raw,
                              array_job_outpath=array_job_outpath, 
                              atlas=atlas,
                              overwrite_existing=overwrite_existing,
                              slurm_params=slurm_params,
                              model_path=model_path,
                              ceph_path_root=None,
                              )
    
if __name__ == "__main__":
    main()

