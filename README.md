## Browser GUI for [DEMUCS](https://github.com/facebookresearch/demucs) v1.0

### SETUP Instructions to run on AWS

1. Start the instance
1. clone/pull from github
1. create env
1. pip install flask and demucs
1. add necessary env attributes
1. create /uploads in /tmp
1. `mkfifo fpipe`
1. activate env
1. start screen
1. in one `flask --app main run` or
1. `flask --app main --debug run` or
1. `flask --app main --debug run --host=0.0.0.0` in PRD
1. in another run `./listener.sh`
