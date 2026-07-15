from re import sub


def strip_tags(s):
    return sub(r'<.*?>', '', s)
