import fire
from magicgui import magicgui
from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout
from pathlib import Path
import warnings
from hpc_scripts.slurm_config import slurm_params
from xpmtd import metadata
import subprocess
from brainglobe_hpc.brainreg_commands import save_brainreg_array_job
from brainglobe_hpc.cellfinder_commands import save_cellfinder_array_job


def parse_rsync_dryrun_for_real_file_changes(result):
    lines = result.stdout.strip().splitlines()
    file_lines = [
    line for line in lines 
    if line 
    and not line.startswith("sending incremental") 
    and not line.startswith("sent ") 
    and not line.startswith("total size is")
]

    if file_lines:
        print("Changes detected")
        return True
    else:
        print("No changes")



def sync_raw_and_processed_data(
    raw_directory,
    processed_directory,
    mouse_id=None,
):
    """
    Runs rsync command from python to copy across necessary data from raw to processed directories. May require
    modification for use on Windows. Tested on Linux.

    :param raw_directory:
    :param processed_directory:
    :return:
    """
    if mouse_id is not None:
        raw_directory = raw_directory / str(mouse_id)
        processed_directory = processed_directory / str(mouse_id)

    print(f"transferring {raw_directory} to {processed_directory}")
    cmd = "rsync -nrtv --exclude='*.avi' --exclude='*.imec*' --exclude='.mp4' {raw_directory}/* {processed_directory}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if parse_rsync_dryrun_for_real_file_changes(result):
        cmd = f"rsync -tvr --chmod=D2775,F664 --exclude='*.avi' --exclude='*.imec*' --exclude='.mp4' {raw_directory}/* {processed_directory} --checksum --append-verify"
        p = subprocess.Popen(cmd, shell=True)
        p.wait()



@magicgui(
    path_to_remote_data_folder={"mode": "d"},
    rawdata_directory={"mode": "d"},
    derivatives_directory={"mode": "d"},
    batch_script_ouptut_directory={"mode": "d"},
    serial2p_dir={"mode": "d"},
    cellfinder_model_path={"mode": "d"},
    mouse_ids={"widget_type": "Select", "choices": [], "allow_multiple": True},
    unprocessed_items={"widget_type": "Select", "choices": [], "allow_multiple": True},
    atlas={"choices": ["allen_mouse_10um", "kim_mouse_10um"]}
)
def pipeline_widget(
                    path_to_remote_data_folder =Path("/ceph/margrie/"),
                    rawdata_directory=Path("/ceph/margrie/slenzi/2024/SC/rawdata/"),
                    derivatives_directory=Path("/ceph/margrie/slenzi/2024/SC/derivatives/"),
                    serial2p_dir=Path("/ceph/margrie/slenzi/serial2p/whole_brains/raw/"),
                    cellfinder_model_path=Path("/ceph/margrie/juliaw/trained_models/training_output/model-epoch.03-loss-0.088.h5"),
                    batch_script_ouptut_directory = Path("/ceph/margrie/slenzi/batch_scripts/"),
                    mouse_ids=[],
                    unprocessed_items=[],
                    brainreg: bool = False,
                    cellfinder: bool = False,
                    run_locally: bool = False,
                    display_unprocessed_sessions: bool = False,
                    atlas: str = "allen_mouse_10um",

):

    print(f"The following mouse IDs will now be analysed: {mouse_ids}")
    for mouse_id in mouse_ids:
        print(f"Processing mouse ID: {mouse_id}")
        print("syncing data...")
        sync_raw_and_processed_data(mouse_id=mouse_id,
                                    raw_directory=rawdata_directory,
                                    processed_directory=derivatives_directory)

        mtd = metadata.MouseMetadata(
                            mouse_id,
                            rawdata_directory=rawdata_directory,
                            derivatives_directory=derivatives_directory,
                            serial2p_dir=serial2p_dir,
                            atlas=atlas
                            )

        if not mtd.mouse_dir_rawdata.exists():
            warnings.warn("mouse directory not found")
            raise ValueError

    array_job_outpath=pipeline_widget.batch_script_ouptut_directory.value
    if brainreg:
        print("brainreg job setup...")

        save_brainreg_array_job(
                        rawdata_directory=rawdata_directory,
                        serial2p_directory_raw = serial2p_dir,
                        array_job_outpath = array_job_outpath, 
                        atlas=pipeline_widget.atlas.value,
                        overwrite_existing = False,
                        slurm_params=slurm_params,
                        mouse_ids_to_process = mouse_ids,
                        ceph_path_root=pipeline_widget.path_to_remote_data_folder.value,
                        )

    if cellfinder:
        save_cellfinder_array_job(rawdata_directory, 
                                      serial2p_dir,
                                      array_job_outpath=array_job_outpath, 
                                      atlas=pipeline_widget.atlas.value,
                                      overwrite_existing=False,
                                      slurm_params=slurm_params,
                                      model_path=pipeline_widget.cellfinder_model_path.value,
                                      ceph_path_root=pipeline_widget.path_to_remote_data_folder.value,

                                  )


def load_experiment_directories(event=None):
    p = pipeline_widget.rawdata_directory.value
    if p is None:
        print("No directory selected")
        return
    paths = list(Path(p).glob("*"))
    mouse_ids = [path.stem for path in paths if path.is_dir()]
    print("Mouse IDs:", mouse_ids)
    pipeline_widget.mouse_ids.choices = mouse_ids


def display_unprocessed_items(event=None):
    items = []
    print(f"currently selected ids: {pipeline_widget.mouse_ids.choices}")
    for mouse_id in pipeline_widget.mouse_ids.choices:

        print(f"Getting unprocessed items for mouse ID: {mouse_id}")
        print(pipeline_widget.atlas.value)
        mtd = metadata.MouseMetadata(mouse_id,
                            rawdata_directory=pipeline_widget.rawdata_directory.value,
                            derivatives_directory=pipeline_widget.derivatives_directory.value,
                            serial2p_dir=pipeline_widget.serial2p_dir.value,
                            atlas=pipeline_widget.atlas.value
                              )
        items.extend(mtd.unprocessed_items())
    pipeline_widget.unprocessed_items.choices = items


def set_derivatives_directory(event=None):
    pipeline_widget.derivatives_directory.value = pipeline_widget.rawdata_directory.value.parent / "derivatives"


pipeline_widget.rawdata_directory.changed.connect(set_derivatives_directory)
pipeline_widget.rawdata_directory.changed.connect(load_experiment_directories)
pipeline_widget.display_unprocessed_sessions.changed.connect(display_unprocessed_items)


def pipelinerz_gui():
    app = QApplication([])
    widget = pipeline_widget
    main_window = QWidget()

    layout = QVBoxLayout()
    layout.addWidget(widget.native)

    main_window.setLayout(layout)
    main_window.setWindowTitle("Pipeline Widget")
    main_window.show()

    app.exec_()


def main():
    fire.Fire(pipelinerz_gui())


if __name__ == "__main__":
    main()
