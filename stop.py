import json

ngramlen = 2

bins = [0, 500]
# stop = ['s', 'a']
stop = [
    'a',
    'so',
    'i',
    'it',
    's',
    'by',
    'multiplayer',
    'do',
    'didn',
    'an',
    'm',
    # 'over', 'also', 'played', 'real', 'really', 'time', 'other', 'one',
    # 'these', 'things',
    'also',
    'real',
    'time',
    'x',
    'my',
    'ah',
    'k',
    'wii',
    'v',
    'us',
    'am',
    'thats',
    'im',
    'p',
    'sp',
    'aa',
    'cd',
    'sc',
    'un',
    'ol',
    'rb',
    'hd',
    'ut',
    'isn',
    'h',
    'ex',
    'of',
    'yo',
    'gameplay',
    'bo',
    'bc',
    'ap',
    'os',
    'eh',
    'r',
    'cc',
    'rr',
    'doesnt',
    'ny',
    'nd',
    'kd',
    'si',
    'xp',
    'ua',
    'ad',
    'ii',
    'z',
    'tb',
    'sd',
    'ww',
    'ac',
    'l',
    'bf',
    'lo',
    'da',
    'e',
    'su'
]  # stop = []
# stop  ['s']'he', 'fp', 'tv', 'sp', 'dr', 'sh', 'mr', 'mo','gp']    'r',    'v',

# 85.26
# stop = ["a", "s", "t", "ve", "m", "and", "the"]
# stop = ["the"]

# stems = {}
# with open('lemmas.json', 'r') as fin:
#     stems = json.loads(fin.read())
