import os   
import fire
from magicgui import magicgui
from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout
from pathlib import Path
import warnings
from hpc_scripts.slurm_config import slurm_params
from xpmtd import metadata
import subprocess
from hpc_scripts.brainglobe_hpc.gui_functions import get_unprocessed_items, generate_module_versions, get_gui_variables
from hpc_scripts.brainglobe_hpc.brainreg_commands import save_brainreg_array_job
from hpc_scripts.brainglobe_hpc.cellfinder_commands import save_cellfinder_array_job
from hpc_scripts.brainglobe_hpc.file_management import sync_raw_and_processed_data

# if e.g. opencv has been imported then the qt path gets altered and this will break everything
# to solve this we just set the plugin path to something empty and let it find a suitable default
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = ""

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
    mouse_ids, atlas, rawdatadir, derivatives_directory, serial2p_dir = get_gui_variables(pipeline_widget)
    unprocessed_items = get_unprocessed_items(mouse_ids, atlas, rawdatadir, derivatives_directory, serial2p_dir)
    pipeline_widget.unprocessed_items.choices = unprocessed_items


def set_derivatives_directory(event=None):
    pipeline_widget.derivatives_directory.value = pipeline_widget.rawdata_directory.value.parent / "derivatives"

def widget_module_versions(event=None):
    modules_directory_value = pipeline_widget.modules_directory.value    
    root_dir = Path(modules_directory_value)
    pipeline_widget.module_strings.choices = generate_module_versions(root_dir)

@magicgui(
    path_to_remote_data_folder={"mode": "d"},
    rawdata_directory={"mode": "d"},
    derivatives_directory={"mode": "d"},
    batch_script_ouptut_directory={"mode": "d"},
    serial2p_dir={"mode": "d"},
    cellfinder_model_path={"mode": "d"},
    modules_directory={"mode": "d"},
    mouse_ids={"widget_type": "Select", "choices": [], "allow_multiple": True},
    unprocessed_items={"widget_type": "Select", "choices": [], "allow_multiple": True},
    atlas={"choices": ["allen_mouse_10um", "kim_mouse_10um"]},
    module_strings={"widget_type": "Select", "choices": [], "allow_multiple": True},

)
def pipeline_widget(
                    path_to_remote_data_folder =Path("/ceph/margrie/"),
                    rawdata_directory=Path("/ceph/margrie/slenzi/2024/SC/rawdata/"),
                    derivatives_directory=Path("/ceph/margrie/slenzi/2024/SC/derivatives/"),
                    batch_script_ouptut_directory = Path("/ceph/margrie/slenzi/batch_scripts/"),
                    serial2p_dir=Path("/ceph/margrie/slenzi/serial2p/whole_brains/raw/"),
                    cellfinder_model_path=Path("/ceph/margrie/juliaw/trained_models/training_output/model-epoch.03-loss-0.088.h5"),
                    modules_directory=Path("/ceph/apps/ubuntu-24/modulefiles/"),
                    mouse_ids=[],
                    unprocessed_items=[],
                    brainreg: bool = False,
                    cellfinder: bool = False,
                    run_locally: bool = False,
                    display_unprocessed_sessions: bool = False,
                    atlas: str = "allen_mouse_10um",
                    module_strings= [],


):

    print(f"The following mouse IDs will now be analysed: {mouse_ids}")
    for mouse_id in mouse_ids:
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
                        module_strings=[module for module in module_strings],

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
                                  module_strings=[module for module in module_strings],

                                  )


pipeline_widget.rawdata_directory.changed.connect(set_derivatives_directory)
pipeline_widget.rawdata_directory.changed.connect(load_experiment_directories)
pipeline_widget.display_unprocessed_sessions.changed.connect(display_unprocessed_items)
pipeline_widget.modules_directory.changed.connect(widget_module_versions)


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
