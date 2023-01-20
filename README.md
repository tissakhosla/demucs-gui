## Browser GUI for [DEMUCS](https://github.com/facebookresearch/demucs) v1.0

### SETUP Instructions to run on AWS

### On an new instance
1. Create a new instance of latest Ubuntu build
1. Allocate an Elastic IP
1. Associate the IP with the new Instance
1. confirm key pair
1. `vi .ssh/config`
1. Add the following to it:
```
Host <DEMUCS_INSTANCE>
        HostName <ELASTIC_IP>
        IdentityFile /path/to/key.cer
        User ubuntu
```
7. `ssh <DEMUCS_INSTANCE>`
1. `rsync -nav .ssh/<GITHUB_KEY> <DEMUCS_INSTANCE>:/home/ubuntu/.ssh`
1. `rsync -av .ssh/<GITHUB_KEY> <DEMUCS_INSTANCE>:/home/ubuntu/.ssh`
1. `touch .ssh/config`
1. `vi .ssh/config`
1. Add the following to it:
```
Host github.com
    IdentityFile /home/ubuntu/.ssh/<GITHUB_KEY>
    User git
```
1. `sudo apt dist-upgrade`
1. `sudo apt update`
1. `apt list --upgradeable`
1. `sudo apt upgrade`
1. `git clone git@github.com:tissakhosla/demucs-gui.git`
1. `mkdir envs`
1. `python3 -m venv envs/<ENVNAME>`
1. `cd demucs-gui`
1. `. ~/envs/<ENVNAME>/bin/activate`
1. `python3 -m pip list`
1. `python3 -m pip install --upgrade pip` if needed
1. `pip install -r requirements.txt`
1. add necessary env attributes
1. `mkdir /tmp/uploads`
1. `mkfifo fpipe`
1. `screen`
1. `flask --app main --debug run --host=0.0.0.0` in PRD
1. in another run `./listener.sh`
1. go to 
