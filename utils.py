import re
import time
import random


def safe_path(filename):
    return re.sub('[^\w\-_\. ]', ' ', str(filename)) #noqa

def exp_backoff(n):
    time.sleep((2 ** n) + (random.randint(0, 1000) / 1000))
