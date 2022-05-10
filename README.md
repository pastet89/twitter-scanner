# twitter_notification_bot
Twitter bot tracking multiple twitter accounts and sending emails only when the tweets contain some specific string


Uses a simple JSON file for DB to keep track of emailed notifications.


INSTALLATION AND USAGE:

You need Python 3 (the bot is built with Python 3.9.2).

Create a virtual environment: 

```
python -m venv /path/to/new/virtual/environment
```

Activate it:

```
source /path/to/new/virtual/environment/bin/activate
```

Install the dependencies:

```
pip install -r requirements.txt
```

Set permissions on the bash script:

```
chmod +X restart.sh
```

- Create a Twitter API account [here](https://developer.twitter.com/en/docs/twitter-api). From the credentials all you need is the Bearer Token.

- Create an email server. You can create one using AWS SES [here](https://aws.amazon.com/about-aws/whats-new/2011/12/13/amazon-simple-email-service-gets-simpler-with-smtp/).
The AWS SES pricing can be found [here](https://aws.amazon.com/ses/pricing/).

- Change the config settings in ```config.py```: enter your Twitter API Bearer Token, the email server settings, the email from which you wish to send the email and the email on which you wish to receive emails.

- In ```twitter.py``` enter the projects you wish to follow using the example ```tracked_users``` variable. Enter the username of each account you wish to follow. In ```keyword_filter``` if you wish to receive all tweets, simply leave ```None```.
If you wish to filter the tweets and get only those of them which contain certain strings, use a string which contains all strings you are interested in, separated by ```|``` as shown in the file example. For example,
if you wish to receive only tweets that contain ```NFT```, ```whitelist```, ```discord```, use:

```
"NFT|whitelist|discord"
```

Note: this IS case-sensitive. So you might need to use better:

```
"NFT|whitelist|discord|Discord|Whitelist"
```

NOTE: The bot will NOT send tweets which are not posted by the account but represent just replies to other users.


Restart/start the bot using:

```
sh restart.sh
```
