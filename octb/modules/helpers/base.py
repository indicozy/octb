import re

def hashtag_escape(hashtag):
    return re.sub('[\,\ \+]+', '_', hashtag)
    
def generate_menu(items):
    menu_new = [
        [],
    ]

    for i in items:
        if len(menu_new[-1]) >= 3:
            menu_new.append([i]) 
        else:
            menu_new[-1].append(i)
    return menu_new

def generate_post(headline, text, hashtags, args={}):
    hashtags_text = " ".join([f'#{hashtag_escape(hashtag.lower())}' for hashtag in hashtags])
    args_text = "\n".join([f'{key}: {value}' for key, value in args.items()])
    return f"""{hashtags_text}
{headline}

{text}

{args_text}
"""