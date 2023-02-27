### Demucs-Gui Setup

1. `rsync -nav .ssh/<GITHUB_KEY> <DEMUCS_INSTANCE>:/home/ubuntu/.ssh`
1. `rsync -av .ssh/<GITHUB_KEY> <DEMUCS_INSTANCE>:/home/ubuntu/.ssh`
1. Back to `<DEMUCS_INSTANCE>` Terminal
1. `touch .ssh/config`
1. `vi .ssh/config`
1. Add the following to it:
```
Host github.com
    IdentityFile /home/ubuntu/.ssh/<GITHUB_KEY>
    User git
```
1. `mkdir envs`
1. `python3 -m venv envs/<ENVNAME>`
1. `git clone git@github.com:tissakhosla/demucs-gui.git`
1. `cd demucs-gui`
1. `. ~/envs/<ENVNAME>/bin/activate`
1. `python3 -m pip list`
1. `python3 -m pip install --upgrade pip` if needed
1. `pip install -r requirements.txt`
1. `mkfifo fpipe`
1. `export <ENV ATTRIBUTES>`
1. `. ~/envs/<ENVNAME>/bin/activate` if not already
1. `mkdir /tmp/uploads`
1. `screen`
1. `↵`
1. in screen 1 - `flask --app main --debug run --host=0.0.0.0` GUNICORN 
1. create another screen - `^+a, c`
1. in screen 2 - `./listener.sh`
1. go to `<ELASTIC_IP>:5000` to test
