def generate_post(headline, text, hashtags, args={}):
    return f"""{f'#{hashtag}' for hashtag in hashtags}
{headline}

{text}

{f'{key}: {value}' for key, value in args.items()}
"""