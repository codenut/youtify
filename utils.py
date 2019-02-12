import re


def safe_path(filename):
    return re.sub('[^\w\-_\. ]', ' ', str(filename)) #noqa
