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
36. `sudo vim /etc/nginx/sites-available/default` add the following in the location block
```
include proxy_params;
proxy_pass http://unix:/tmp/demucs.sock;
```
37. add `client_max_body_size 10000M;` to the end of the `server{}` block as well.
1. `sudo ln -s /etc/nginx/sites-available/demucs /etc/nginx/sites-enabled`
1. `sudo ufw enable`
1. `sudo ufw allow ssh`
1. `sudo ufw allow 'Nginx HTTP'`
1. Setup SSL - followed [Digital Ocean tutorial](https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-nginx-in-ubuntu-22-04)
1. `sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned-demucs.key -out /etc/ssl/certs/nginx-selfsigned-demucs.crt`
1. `sudo openssl dhparam -out /etc/nginx/dhparam.pem 4096`
1. `sudo vi /etc/nginx/snippets/self-signed-demucs.conf` and add to it
```
ssl_certificate /etc/ssl/certs/nginx-selfsigned-demucs.crt;
ssl_certificate_key /etc/ssl/private/nginx-selfsigned-demucs.key;
```
46. `sudo vi /etc/nginx/snippets/ssl-params.conf` and add to it
```
ssl_protocols TLSv1.3;
ssl_prefer_server_ciphers on;
ssl_dhparam /etc/nginx/dhparam.pem;
ssl_ciphers EECDH+AESGCM:EDH+AESGCM;
ssl_ecdh_curve secp384r1;
ssl_session_timeout  10m;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off;
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
# Disable strict transport security for now. You can uncomment the following
# line if you understand the implications.
#add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
```
47. `screen`
1. `sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.bak`
1. `sudo vi /etc/nginx/sites-available/default`
1. uncomment the following lines and add the includes below them
```
listen 443 ssl default_server;
listen [::]:443 ssl default_server;
include snippets/self-signed-demucs.conf;
include snippets/ssl-params.conf;
```
51. `sudo ufw allow 'Nginx HTTPS'`
1. `sudo ufw status verbose` should say something like
```
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)
New profiles: skip

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW IN    Anywhere
80/tcp (Nginx HTTP)        ALLOW IN    Anywhere
443/tcp (Nginx HTTPS)      ALLOW IN    Anywhere
22/tcp (v6)                ALLOW IN    Anywhere (v6)
80/tcp (Nginx HTTP (v6))   ALLOW IN    Anywhere (v6)
443/tcp (Nginx HTTPS (v6)) ALLOW IN    Anywhere (v6)
```
53. `sudo nginx -t` should say
```
nginx: [warn] "ssl_stapling" ignored, issuer certificate not found for certificate "/etc/ssl/certs/nginx-selfsigned-demucs.crt"
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```
54. `sudo systemctl restart nginx`
1. Allow Port 443 in AWS security Group
1. Point DNS
1. `sudo vi /etc/nginx/sites-available/default`
1. comment the following lines and add the includes below them
```
#       listen 80 default_server;
#       listen [::]:80 default_server;
```
59. `sudo ufw delete allow 'Nginx HTTP'`
1. `sudo ufw status verbose` should now say
```
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)
New profiles: skip

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW IN    Anywhere
443/tcp (Nginx HTTPS)      ALLOW IN    Anywhere
22/tcp (v6)                ALLOW IN    Anywhere (v6)
443/tcp (Nginx HTTPS (v6)) ALLOW IN    Anywhere (v6)
```
61. Remove port 80 from AWS security Group
1. Buy Certificate from GoDaddy and Download Zip File
1. put key and crt in appropriate directories and adjust .conf file and nginx default file appropriately

# Production Notes
## Paypal
1. Changed base URL in pay.py to live
1. Clicked Sandbox<>Live Slider on Paypal Developer Dashboard to live.
1. Created a new app and got CLIENT_ID and CLIENT_SECRET
### Locally
1. Export Env vars
1. In IDE, run Payment.create_product()
```
from pay import Payment
p = Payment()
p.get_token()
p.create_product()
p.create_billing()
```
1. `flask --app wsgi --debug run`
1. Test payment flow, it works!

## On EC2
1. `sudo systemctl stop demucs`
1. always back this up `demucs-gui/users.db`
1. pull and checkout appropriate branch
1. `. ~/envs/demucs/bin/activate`
1. `python3 -m pip install -r demucs-gui/requirements.txt`
1. `deactivate`
1. `sudo vim /etc/systemd/system/demucs.service` - update as needed
1. `sudo systemctl daemon-reload`
1. screen
1. screen 1 (listener): 
```
$ . ~/envs/demucs/bin/activate
$ cd demucs-gui
$ ./listener.sh (must be chmod -x)
```
1. screen 2 (wsgi log): `$ sudo journalctl -u demucs -f`
1. screen 3 (nginx error): `$ tail -F /var/log/nginx/error.log`
1. screen 4 (nginx access): `$ tail -F /var/log/nginx/access.log`
1. screen 5 (users): 
```
$ cd demucs-gui
$ python3
>>> import sqlite3
>>> con = sqlite3.connect("users.db")
>>> cur = con.cursor()
>>> for row in cur.execute('SELECT * FROM users'):
>>>     print(row)
```