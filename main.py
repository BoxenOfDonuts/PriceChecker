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
            if ('SN750' and 'TB') in submission.title and submission.id not in old_submission_ids or \
                    ('970' and 'Samsung' and 'TB') in submission.title and submission.id not in old_submission_ids:
                logger.info('Matched Deal Found!',  extra={'matched': 'yes'})
                message = "SSD Deal!\n" \
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
            elif submission.id in old_submission_ids:
                logger.info('Old Submission Found')
            else:
                logger.info('new post found, no matching criteria', extra={'matched': 'no'})

    except prawcore.exceptions.ServerError as e:
        logger.error('error with praw, sleeping then restarting', extra={'error', e})
        time.sleep(10)
    except prawcore.exceptions.RequestException as e:
        logger.error('request exception', extra={'error': e})
        time.sleep(10)


if __name__ == "__main__":
    main()
