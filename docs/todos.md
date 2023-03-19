## TODOs
- downloads if I copy and paste the link, but not if I click?

### Pre Release Updates
- sign in and then subscribe? let users know they are going to need to pay 6$
- forgot email or password
- terms and conditions - data privacy?
- listener has to use demucs command from env!
    -   open `screen`, activate env
- cron backup db
- figure out reactivation status change? or its just a new scription
- add subscription status to DB and update on login, display in user-status
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
- add http redirect
 - more info on the listener log
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