def star_generate(num):
    full = '★'
    empty = '☆'
    text = ''
    for i in range(5):
        if i < num:
            text += full
        else:
            text += empty
    return text