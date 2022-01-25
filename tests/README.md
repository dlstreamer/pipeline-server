# Intel(R) DL Streamer Pipeline Server Tests and Scans

## Tests Run Script Reference
The `run.sh` can be used to run tests or scans with option to select only one at a time, default selected as --pytest-gstreamer. It uses [docker/run.sh](../docker/run.sh) to pass common options to the underlying docker run command [Reference Doc](../docs/run_script_reference.md).
```
tests/run.sh --help
```
```
usage: run.sh
  [ --pytest-gstreamer : Run gstreamer tests ]
  [ --pytest-ffmpeg: Run ffmpeg tests ]
  [ --pylint : Run pylint scan ]
  [ --pybandit: Run pybandit scan ]
  [ --clamav : Run antivirus scan ]
```

### Architecture
* RESULTS_DIR : Results directory is created and volume mounted according to test or scan selected, Directory path is Set as environment varible used by entrypoint scripts to save results in the directory.
* ENTRYPOINT: selected in the script according to test or scan selected.
* Entrypoint Args can be changed through environment variable defined in respective entrypoint scripts, or through --entrypoint-args option.

#### Entrypoint Scripts
Entrypoint directory used to maintain Docker entrypoint scripts to run tests and scans. Each entrypoint script contains below mentioned details if supported.
* Support to read RESULTS_DIR environment variable to save results in that path.
* Other environment args required and that can be updated from run.sh.
* Command to run respective tests/scans.