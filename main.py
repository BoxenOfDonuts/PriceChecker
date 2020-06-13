import configparser
import time
import praw
import prawcore
import os
import requests
from logger import logger

config = configparser.ConfigParser(interpolation=None)
configfile = os.path.join(os.path.dirname(__file__), 'config.ini')
submission_txt = os.path.join(os.path.dirname(__file__), 'old_submissions.txt')

sales_dict = {
    'Samsung SSD': ['970', 'Samsung','TB'],
    'Other SSD': ['SN750','TB'],
    'PSU': ['SF600']
}


def praw_auth():
    config.read(configfile)
    reddit = praw.Reddit(client_id=config['praw']['client_id'],
                         client_secret=config['praw']['client_secret'],
                         user_agent='python:nourl:v0.01 by /u/BoxenOfDonuts',
                         username=config['praw']['username'],
                         password=config['praw']['password'])
    logger.info('logged into praw')

    return reddit


def telegram_send(message):
    bot_token = config['telegram']['token']
    bot_chatID = config['telegram']['chatID']

    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + message
    try:
        r = requests.get(send_text)
        r.raise_for_status()
        response = r.json()['ok']
        logger.info("GET to telegram", extra={"Response": response, 'URL': r.url})
    except requests.exceptions.RequestException as e:
        logger.error("something went wrong", extra={"error": e})
        response = r.json()['ok']

    return response


def main():
    reddit = praw_auth()

    with open(submission_txt, 'r') as f:
        old_submission_ids = f.read().splitlines()

    try:
        for submission in reddit.subreddit('buildapcsales').stream.submissions():
            if submission.id in old_submission_ids:
                logger.info('Old Submission Found')

            # custom any function that iterates over the sales_dict
            elif any(submission.title):
                logger.info('Matched Deal Found!',  extra={'matched': 'yes'})
                message = "Deal Found!\n" \
                          "{}\n" \
                          "{}".format(submission.title, submission.url)

                response = telegram_send(message)

                if response:
                    with open(submission_txt, 'a') as f:
                        f.write(submission.id + "\n")

                    old_submission_ids.append(submission.id)
                    logger.info("Message Sent")
                else:
                    logger.error("Message Not Sent")
            else:
                logger.info('new post found, no matching criteria', extra={'matched': 'no'})

    except prawcore.exceptions.ServerError as e:
        logger.error('error with praw, sleeping then restarting', extra={'error', e})
        time.sleep(10)
    except prawcore.exceptions.RequestException as e:
        logger.error('request exception', extra={'error': e})
        time.sleep(10)


def any(title):
    # see https://docs.python.org/3/library/functions.html#any
    for k, v in sales_dict.items():
        if all(x in title for x in v):
            return True
    return False


if __name__ == "__main__":
    main()
