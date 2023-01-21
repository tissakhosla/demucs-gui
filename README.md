# Browser GUI for [DEMUCS](https://github.com/facebookresearch/demucs) v1.0

## SETUP Instructions to run on AWS

### On an new instance
1. Create a new instance of latest Ubuntu build.
    - Ideally t3.2xlarge - 32GiB Memory - 8vCPUs
    - ubuntu image
    - use security group 1 (ports 22 and 5000)
    - 64 gb
1. Allocate an Elastic IP.
1. Associate the IP with the new Instance.
1. Use existing key pair or create new one.
1. `vi .ssh/config`
1. Add the following to it:
```
Host <DEMUCS_INSTANCE>
        HostName <ELASTIC_IP>
        IdentityFile /path/to/key.cer
        User ubuntu
```
7. `ssh <DEMUCS_INSTANCE>`
1. In a separate terminal window
    - `rsync -nav .ssh/<GITHUB_KEY> <DEMUCS_INSTANCE>:/home/ubuntu/.ssh`
    - `rsync -av .ssh/<GITHUB_KEY> <DEMUCS_INSTANCE>:/home/ubuntu/.ssh`
1. Back to SSH Terminal
1. `touch .ssh/config`
1. `vi .ssh/config`
1. Add the following to it:
```
Host github.com
    IdentityFile /home/ubuntu/.ssh/<GITHUB_KEY>
    User git
```
13. `sudo apt dist-upgrade`
1. `sudo apt update`
1. `apt list --upgradeable`
1. `sudo apt upgrade`
1. `sudo apt install ffmpeg`
1. `sudo apt install python3-venv`
1. `mkdir envs`
1. `python3 -m venv envs/<ENVNAME>`
1. `git clone git@github.com:tissakhosla/demucs-gui.git`
1. `cd demucs-gui`
1. `export <ENV ATTRIBUTES>`
1. `. ~/envs/<ENVNAME>/bin/activate`
1. `python3 -m pip list`
1. `python3 -m pip install --upgrade pip` if needed
1. `pip install -r requirements.txt`
1. `mkdir /tmp/uploads`
1. `mkfifo fpipe`
1. `screen`
1. `↵`
1. in screen 1 - `flask --app main --debug run --host=0.0.0.0`
1. create another screen - `^+a, c`
1. in screen 2 - `./listener.sh`
1. go to `<ELASTIC_IP>:5000` to test

### Updates needed
- use LARGE instance... I think it's definitely faster
- add frontend radio buttons
    - add support to export mp3s
    - add support to use other models
- create new email address to handle all this
- Get DNS
-  Make the frontend pretty (CSS)
- <♩♩♩♩/> and make it an HTML email
- cron removal of separated tracks once a week
- upload completed files to S3 with [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- don't use flask built in server in PRD
- make separate class for functions, so routes are in one place, methods in another. 
- send a zip file for download?
- SSL
- Figure out cost spread w Sukhi