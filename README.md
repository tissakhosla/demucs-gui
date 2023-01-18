## Browser GUI for [DEMUCS](https://github.com/facebookresearch/demucs) v1.0

### SETUP Instructions to run on AWS

1. Start the AWS instance.
1. `git clone git@github.com:tissakhosla/demucs-gui.git`
1. `python3 -m venv envs/<ENVNAME>`
1. `. envs/<ENVNAME>/bin/activate`
1. `python3 -m pip list`
1. `python3 -m pip install --upgrade pip` if needed
1. `cd demucs-gui`
1. pip install flask and demucs
1. add necessary env attributes
1. `mkdir /tmp/uploads`
1. `mkfifo fpipe`
1. activate env
1. start screen
1. in one `flask --app main run` or
1. `flask --app main --debug run` or
1. `flask --app main --debug run --host=0.0.0.0` in PRD
1. in another run `./listener.sh`
