## Browser GUI for [DEMUCS](https://github.com/facebookresearch/demucs) v1.0

### SETUP Instructions to run on a server

1. clone from github
1. create env
1. pip install flask and demucs
1. `mkfifo fpipe`
1. start screen
1. in one `flask --app main run` or
1. `flask --app main --debug run` or
1. `flask --app main --debug run --host=0.0.0.0` in PRD
1. in another run `./listener.sh`
