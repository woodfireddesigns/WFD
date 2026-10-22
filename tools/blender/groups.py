# Kiln group for each anatomical muscle name (lowercased). Order matters: first match wins.
GROUPS = ['chest', 'shoulders', 'triceps', 'lats', 'upperback', 'traps', 'biceps', 'forearms', 'quads', 'hamstrings', 'glutes', 'calves', 'abs', 'lowerback']
RULES = [
    ('chest', ['pectoralis major', 'pectoralis minor']),
    ('shoulders', ['deltoid']),
    ('triceps', ['triceps brachii', 'anconeus']),
    ('lats', ['latissimus dorsi', 'teres major']),
    ('upperback', ['transverse part of trapezius', 'ascending part of trapezius']),   # mid/lower traps: rows, face pulls
    ('traps', ['trapezius']),
    ('upperback', ['rhomboid', 'infraspinatus', 'teres minor', 'supraspinatus', 'serratus posterior']),
    ('biceps', ['biceps brachii', 'brachialis', 'coracobrachialis']),
    ('forearms', ['brachioradialis', 'carpi', 'pronator', 'supinator', 'palmaris', 'flexor digitorum superficialis', 'flexor digitorum profundus',
                  'extensor digitorum muscle', 'extensor digitorum.', 'extensor digiti minimi muscle', 'extensor indicis', 'extensor pollicis', 'abductor pollicis longus', 'flexor pollicis longus']),
    ('hamstrings', ['biceps femoris', 'semitendinosus', 'semimembranosus', 'adductor magnus']),
    ('quads', ['iliotibial tract', 'rectus femoris', 'vastus', 'sartorius', 'adductor longus', 'adductor brevis', 'gracilis', 'pectineus']),
    ('glutes', ['gluteus', 'tensor fasciae latae', 'tensor of fascia lata']),
    ('calves', ['gastrocnemius', 'soleus', 'tibialis anterior', 'fibularis', 'peroneus', 'plantaris', 'extensor digitorum longus', 'extensor hallucis longus', 'flexor digitorum longus', 'flexor hallucis longus', 'tibialis posterior']),
    ('abs', ['rectus abdominis', 'abdominal oblique', 'external oblique', 'internal oblique', 'transversus abdominis', 'pyramidalis', 'serratus anterior']),
    ('lowerback', ['erector spinae', 'iliocostalis', 'longissimus', 'spinalis', 'multifidus', 'quadratus lumborum']),
]
def group_of(name):
    n = name.lower().replace('(', '').replace(')', '')
    if 'longissimus capitis' in n or 'cervicis' in n or 'capitis' in n: return None   # neck parts of erectors
    for g, keys in RULES:
        if any(k in n for k in keys): return g
    return None
