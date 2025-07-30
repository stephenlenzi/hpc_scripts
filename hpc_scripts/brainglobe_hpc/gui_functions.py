from xpmtd import metadata
from pathlib import Path


def get_unprocessed_items(mouse_ids, atlas, rawdatadir, derivatives_directory, serial2p_dir):
    items = []
    print(f"currently selected ids: {mouse_ids}")
    for mouse_id in mouse_ids:
        print(f"Getting unprocessed items for mouse ID: {mouse_id}")
        print(atlas)
        mtd = metadata.MouseMetadata(mouse_id,
                                     rawdata_directory=rawdatadir,
                                     derivatives_directory=derivatives_directory,
                                     serial2p_dir=serial2p_dir,
                                     atlas=atlas
                                    )
        items.extend(mtd.unprocessed_items())
    return items


def generate_module_versions(root_dir):
    rootp=Path(root_dir)
    paths = rootp.rglob("*")
    module_strings = ["/".join(p.parts[-2:]) for p in paths if "modulefiles" not in p.parts[-2:]]
    return module_strings

def get_gui_variables(pipeline_widget):
    mouse_ids = pipeline_widget.mouse_ids.choices
    atlas = pipeline_widget.atlas.value
    rawdatadir = pipeline_widget.rawdata_directory.value
    derivatives_directory = pipeline_widget.derivatives_directory.value
    serial2p_dir = pipeline_widget.serial2p_dir.value
    return mouse_ids, atlas, rawdatadir, derivatives_directory, serial2p_dir
