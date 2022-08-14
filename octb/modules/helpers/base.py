import re

def hashtag_escape(hashtag):
    return re.sub('[\,\ \+]+', '_', hashtag)
    

def generate_post(headline, text, hashtags, args={}):
    hashtags_text = " ".join([f'#{hashtag_escape(hashtag.lower())}' for hashtag in hashtags])
    args_text = "\n".join([f'{key}: {value}' for key, value in args.items()])
    return f"""{hashtags_text}
{headline}

{text}

{args_text}
"""