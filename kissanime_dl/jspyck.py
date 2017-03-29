import re

modifyaswego = ''

def decode(input, isEval=True, isFilter=True, isDebug=False):
    # fuck python 2
    global modifyaswego

    if isFilter:
        fillVer = 'filter'
    else:
        fillVer = 'fill'

    if isEval:
        modifyaswego = input[828:-3]
    else:
        modifyaswego = input

    SIMPLE = {
        # 'false':      '![]',
        'true':       '!![]',
        'undefined':  '[][[]]',
        'NaN':        '+[![]]',
        'Infinity':   '+(+!+[]+(!+[]+[])[!+[]+!+[]+!+[]]+[+!+[]]+[+[]]+[+[]]+[+[]])'
    }

    CONSTRUCTORS = {
        # 'Array':    '[]',
        'Number':   '(+[])',
        'String':   '([]+[])',
        'Boolean':  '(![])',
        # 'Function': '[]["fill"]',
        # 'RegExp':   'Function("return/"+false+"/")()'
    }

    CHARPRIM = {
        'o': '("true"[' + fillVer + '])[10]',
        'c': '([][' + fillVer + ']0)[3]',
        'y': '(NaN+[Infinity])[10]',
    }

    CHARCOMPLEX = {
        'g': ['(0NaNString[constructor])[20]'],
        'S': ['(0String[constructor])[10]'],
        'm': ['(Number[constructor]0)[11]'],
        'A': ['(00[constructor])[10]'],
        'B': ['(0Boolean[constructor])[10]'],
        'C': ['[][filter][constructor](return+("NaN"[filter])[11]+escape)()(String[italics]()[0])[2]', '0[filter][constructor](return escape)()(String[italics]()[0])[2]'],
        'D': ['[][filter][constructor](return+("NaN"[filter])[11]+escape)()(String[fontcolor]()[11])[2]'],
        'E': ['([][filter][constructor](return+(false+[0])[italics]()[10]+[0]+(false+[0])[italics]()[10])()[constructor]0)[12]'],
        'F': ['(00[filter][constructor])[10]'],
        'G': ['("false"[filter][constructor](return 0[filter][constructor](return escape)()(=)2ate)()())30'],
        'H': ['0[filter][constructor](return+("NaN"[filter])[11]+unescape)()([][filter][constructor](return+("NaN"[filter])[11]+escape)()(String[italics]()[0])[0]+(48)0)'],
        'J': ['([][filter][constructor](return+("NaN"[filter])[11]+new+("NaN"[filter])[11]0[filter][constructor](return+("NaN"[filter])[11]+escape)()(String[fontcolor]()[11])[2]+ate+("false"[filter])[20]+[2]+[0]+[0]+[0]+[0]+[0]+[0]+[0]+[0]+("true"[filter])[20])()0)[4]', '([][filter][constructor](return new 0[filter][constructor](return escape)()(=)[2]+ate+(+[2]+[0]+[0]+[0]+[0]+[0]+[0]+[0]+[0]+))()0)[4]'],
        'K': ['[][filter][constructor](return+("NaN"[filter])[11]+unescape)()([][filter][constructor](return+("NaN"[filter])[11]+escape)()(String[italics]()[0])[0]+[4]+b)'],
        'M': ['("true"[filter][constructor](return+("NaN"[filter])[11]0[filter][constructor](return+("NaN"[filter])[11]+escape)()(String[fontcolor]()[11])[2]+ate)()())[30]'],
        'O': ['([][filter][constructor](return+("NaN"[filter])[11]+new+("NaN"[filter])[11]0[filter][constructor](return+("NaN"[filter])[11]+escape)()(String[fontcolor]()[11])[2]+ate+("false"[filter])[20]+[2]+[4]+[0]+[0]+[0]+[0]+[0]+[0]+[0]+[0]+[0]+("true"[filter])[20])()0)[4]'],
        'R': ['(00[filter][constructor](return+(false+[0])[italics]()[10]+[0]+(false+[0])[italics]()[10])()[constructor])[10]'],
        'T': ['("NaN"[filter][constructor](return+("NaN"[filter])[11]0[filter][constructor](return+("NaN"[filter])[11]+escape)()(String[fontcolor]()[11])[2]+ate)()())[30]'],
        '=': ['String[fontcolor]()[11]'],
        '.': ['(+(11e+[2]+[0])0)[1]'],
        '(': ['("false"[filter])[20]'],
        '/': ['(false+[0])[italics]()[10]'],
        ',': ['[[]][concat]([[]])0'],
        "'": ['0[filter][constructor](return unescape)()([][filter][constructor](return escape)()(String[italics]()[0])[0]+(27)0)'],
        '"': ['String[fontcolor]()[12]'],
        ')': ['("true"[filter])[20]'],
        ';': ['b)'],
        '\+': ['+(+(1+(10)[3]+[1]+[0]+[0])0)[2]'],
        '': ['0[filter][constructor](return unescape)()([][filter][constructor](return escape)()(String[italics]()[0])[0]+[3]', '[][filter][constructor](return unescape)()([][filter][constructor](return escape)()(String[italics]()[0])[0]+[3]']
}

    def replaceComplex():
        global modifyaswego
        for key in sorted(CHARCOMPLEX.iterkeys() ):
            for innerkey in CHARCOMPLEX[key]:
                modifyaswego = modifyaswego.replace(innerkey, key)

    def combineLetters(group):
        # f + i + l + l

        return re.sub(r'(?<!\\)\+', '', group.group(1) )

    def modifyCombineLetters():
        global modifyaswego
        modifyaswego = re.sub(r'(([^\)\]]\+)+[^\[\(])', combineLetters, modifyaswego)

    for key in CONSTRUCTORS:
        modifyaswego = modifyaswego.replace(CONSTRUCTORS[key], key)

    for key in SIMPLE:
        modifyaswego = modifyaswego.replace(SIMPLE[key], key)

    # Turns out false isn't so simple after all
    modifyaswego = modifyaswego.replace('!+[]', '1')
    modifyaswego = modifyaswego.replace('+[]', '0')
    modifyaswego = modifyaswego.replace('+![]', '0')
    modifyaswego = modifyaswego.replace('![]', 'false')

    def placeQuotesAround(group):
        # true0
        return '"' + group.group(1) + '"'

    modifyaswego = re.sub(r'([a-zA-Z]+)0', placeQuotesAround, modifyaswego)

    def addUpOnes(group):
        # 1 + 1 + 1
        return str(group.group(1).count('1') )

    modifyaswego = re.sub(r'(1(\+1)+)', addUpOnes, modifyaswego)

    modifyaswego = modifyaswego.replace('+1', '1')

    def strAndNum(group):
        # 1 + [0] = 10
        # assumes group 1 is the first digit and group 2 is the digit inside brackets
        return group.group(1) + group.group(2)

    modifyaswego = re.sub(r'(\d)\+\[(\d)\]', strAndNum, modifyaswego)
    modifyaswego = modifyaswego.replace('[false]+undefined', '"falseundefined"')

    def letterArray(group):
        # 'false'[0]
        # group 1 = word, group 2 = pos
        return group.group(1)[int(group.group(2) )]

    modifyaswego = re.sub(r'\(\"(\w+)\"\)\[(\d+)\]', letterArray, modifyaswego)

    modifyCombineLetters()

    for key in CHARPRIM:
        modifyaswego = modifyaswego.replace(CHARPRIM[key], key)

    modifyCombineLetters()

    replaceComplex()

    modifyCombineLetters()

    replaceComplex()

    modifyaswego = modifyaswego.replace('toString', '"toString"')
    modifyaswego = re.sub(r'(\d)\+\[(\d)\]', strAndNum, modifyaswego)

    def removeSheath(group):
        # (+(20))
        return group.group(1)

    modifyaswego = re.sub(r'\(\+\((\d+)\)\)', removeSheath, modifyaswego)

    def radixConvert(group):
        def baseN(num, radix):
            result = ""
            while num > 0:
                result = "0123456789abcdefghijklmnopqrstuvwxyz"[num % radix] + result
                num /= radix
                num = int(num)
            return result
        # 20["toString"](21)
        return str(baseN(int(group.group(1) ), int(group.group(2) ) ) )

    modifyaswego = re.sub(r'(\d+)\[\"toString\"\]\((\d+)\)', radixConvert, modifyaswego)
    modifyaswego = re.sub(r'(\w+)\[(\d+)\]', letterArray, modifyaswego)

    modifyCombineLetters()

    def charCode(group):
        return chr(int(group.group(1), 16) )

    modifyaswego = re.sub(r'\[\]\[filter\]\[constructor\]\(return\+\(\"NaN\"\[filter\]\)\[11\]\+unescape\)\(\)\(\[\]\[filter\]\[constructor\]\(return\+\(\"NaN\"\[filter\]\)\[11\]\+escape\)\(\)\(String\[italics\]\(\)\[0\]\)\[0\]\+\((\d+)\)0\)', charCode, modifyaswego)

    replaceComplex()

    modifyaswego = modifyaswego.replace('("NaN"[filter])[11]', ' ')

    modifyCombineLetters()

    replaceComplex()

    if isDebug:
        print(modifyaswego)

    def cleanDigits(group):
        return group.group(1)

    modifyaswego = re.sub(r'\[(\d+)\]', cleanDigits, modifyaswego)

    modifyCombineLetters()

    modifyaswego = modifyaswego.replace(')+;', ');')

    modifyaswego = re.sub(r'(?<!\\)\+', '', modifyaswego)

    modifyaswego = modifyaswego.replace('\+', '+')

    if isDebug:
        print(modifyaswego)

    return modifyaswego