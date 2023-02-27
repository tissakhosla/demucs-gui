### AWS setup

1. Create a new instance of latest Ubuntu build.
    - Ideally t3.2xlarge - 32GiB Memory - 8vCPUs
    - ubuntu image
    - select key pair if already in aws
    - use security group 1
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
7. `ssh <DEMUCS_INSTANCE>`
1. `sudo apt dist-upgrade`
1. `sudo apt update`
1. `apt list --upgradeable`
1. `sudo apt upgrade`
1. `sudo apt install ffmpeg`
1. `sudo apt install python3-venv`
1. `sudo apt install nginx`
1. Go to nginx.md