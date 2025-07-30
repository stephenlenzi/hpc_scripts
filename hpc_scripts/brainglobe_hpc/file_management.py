
import subprocess


def parse_rsync_dryrun_for_real_file_changes(result):
    """
    Checksums etc are slow, but get applied whether or not data needs to be copied.
    This function performs a quick dry run to find real changes, bypassing the need
    for slow checksums unless files are being moved.
    """
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
        print(f"Processing mouse ID: {mouse_id}")
        print("syncing data...")
        raw_directory = raw_directory / str(mouse_id)
        processed_directory = processed_directory / str(mouse_id)
    else:
        print(f"processing all folders in : {raw_directory}")

    print(f"transferring {raw_directory} to {processed_directory}")
    cmd = "rsync -nrtv --exclude='*.avi' --exclude='*.imec*' --exclude='.mp4' {raw_directory}/* {processed_directory}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if parse_rsync_dryrun_for_real_file_changes(result):  #only do slow copy when necessary 
        cmd = f"rsync -tvr --chmod=D2775,F664 --exclude='*.avi' --exclude='*.imec*' --exclude='.mp4' {raw_directory}/* {processed_directory} --checksum --append-verify"
        p = subprocess.Popen(cmd, shell=True)
        p.wait()
