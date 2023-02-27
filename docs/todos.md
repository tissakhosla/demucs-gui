## TODOs

### Pre Release Updates
- don't use flask built in server in PRD - nginx
    - proxy from nginx to wsgi (gunicorn?)
    - https
    - use secure flag on cookie w https
- apply DNS
- cron backup db

- Create Test Cases
    - login
        - create
            - new user
            - user already exists
        - read
            - sign in
            - wrong username
            - wrong password
        - update
        - delete

### Post Release Updates
- Security
    - secure and test against SQL injection
- assert ffmpeg is installed?
- assert listener is running
- reset password/delete user and remake
- email should go to signed in user
- create new email address to handle all this
- cron removal of uploaded tracks
- cron removal of separated tracks once a week
- upload completed files to S3 with [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- Figure out cost spread w Sukhi
- style flash messages better