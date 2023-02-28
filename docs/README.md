# Browser GUI for [DEMUCS](https://github.com/facebookresearch/demucs) v1.0
Thanks for using Demucs-Gui

### Instructions to deploy to production
1. Create a new instance of latest Ubuntu build.
    - Ideally t3.2xlarge - 32GiB Memory - 8vCPUs
    - ubuntu image
    - select key pair if already in aws
    - use security group `launch-wizard-1`
        - (inbound from all IPs, ports 22, 5000, 80)
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
7. `rsync -nav .ssh/<GITHUB_KEY> <DEMUCS_INSTANCE>:/home/ubuntu/.ssh`
1. `rsync -av .ssh/<GITHUB_KEY> <DEMUCS_INSTANCE>:/home/ubuntu/.ssh`
7. `ssh <DEMUCS_INSTANCE>`
1. `sudo apt dist-upgrade`
1. `sudo apt update`
1. `apt list --upgradeable`
1. `sudo apt upgrade`
1. `sudo apt install ffmpeg nginx python3-venv`
1. `sudo systemctl status nginx` to confirm nginx
1. `curl -4 icanhazip.com`
1. `curl <IP from above cmd>` to confirm net access
1. `vi .ssh/config`
1. Add the following to it:
```
Host github.com
    IdentityFile /home/ubuntu/.ssh/<GITHUB_KEY>
    User git
```
20. `ssh -T github.com` to test
1. `mkdir envs`
1. `python3 -m venv envs/demucs`
1. `git clone git@github.com:tissakhosla/demucs-gui.git`
1. `git fetch` to get branches if necessary
1. `git checkout <BRANCH>` if necessary
1. `. ~/envs/demucs/bin/activate`
1. `python3 -m pip list`
1. `python3 -m pip install --upgrade pip`
1. `pip install -r demucs-gui/requirements.txt`
1. `deactivate`
1. `mkfifo ~/demucs-gui/fpipe`
1. `mkdir /tmp/uploads`
1. `sudo vim /etc/systemd/system/demucs.service` and add to it
```
[Unit]
Description=Gunicorn instance to serve demucs-gui
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/demucs-gui
Environment="PATH=/home/ubuntu/envs/demucs/bin"
Environment="OTHER_ENV_VARS=whatever they are"
ExecStartPre=/bin/mkdir -p /tmp/uploads
ExecStart=/home/ubuntu/envs/demucs/bin/gunicorn --bind unix:/tmp/demucs.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```
34. `sudo systemctl enable demucs` to run it on boot
1. `sudo vim /etc/nginx/sites-available/demucs` and add to it
```
server {
        listen 80;
        server_name aws-Private-IPv4-address;

        location / {
                include proxy_params;
                proxy_pass http://unix:/tmp/demucs.sock;
        }
}
```
36. `sudo vim /etc/nginx/sites-available/default` and in the appropriate area add to it
```
include proxy_params;
proxy_pass http://unix:/tmp/demucs.sock;
```
37. `sudo ln -s /etc/nginx/sites-available/demucs /etc/nginx/sites-enabled`
1. `sudo ufw enable`
1. `sudo ufw allow ssh`
1. `sudo ufw allow 'Nginx HTTP'`
