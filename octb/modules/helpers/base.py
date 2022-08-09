def selling_map(is_selling):
    if is_selling:
        return 'Продам'
    return 'Куплю'

def generate_post(headline, text, hashtags, args={}):
    hashtags_text = " ".join([f'#{hashtag}' for hashtag in hashtags])
    args_text = "\n".join([f'{key}: {value}' for key, value in args.items()])

    print(headline, hashtags)
    return f"""{hashtags_text}
{headline}

{text}

{args_text}
"""