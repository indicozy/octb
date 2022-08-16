def star_generate(num):
    full = '★'
    half = '⯨'
    empty = '☆'
    text = ''
    for i in range(5):
        if i+1 < num:
            text += full
        elif i+0.5 <= num:
            text += half
        else:
            text += empty
    return text