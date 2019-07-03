import re
f = open("stopwords.txt",'r')
STOPWORDS = [word for word in f]
STOP_LIST = ['a','an','the','is','or','of','for','if','not','with','on','as','per','at','etc','that','ago','and','our','but','by','to','with','such','be','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

def buildLCSmatrix(X, Y):
    """
    Returns the matrix with c and back pointer b obtained from dynamic programming of Longest Common Sequence (LCS)
    :param X: string
    :param Y: string
    :return: c,b matrix,matrix
    """
    m = len(X)
    n = len(Y)

    # initialization of matrix C to count the LCS
    c = [[0]* (n+1) for i in range(m+1)]

    # initialization of matrix b to trace the back pointer
    b = [[0]* (n+1) for i in range(m+1)]
  
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if (X[i-1] == Y[j-1]):
                c[i][j] = c[i - 1][j - 1] + 1
                b[i][j] = 'D'
            elif (c[i-1][j]>= c[i][j-1]):
                c[i][j] = c[i - 1][j]
                b[i][j] = 'U'
            else:
                c[i][j] = c[i][j - 1]
                b[i][j] = 'L'
    return c,b


def parseLCSmatrix(b, start_i, start_j, m, n, lcs_length, Stack, Vectorlist):
    """
    Returns the vector list containing the list of LCS on the corresponding list
    """
    for i in range(start_i, m+1):
        for j in range(start_j, n+1):
            if (b[i][j] == "D"):
                Stack.append((i,j))
                if lcs_length == 1:
                    v = buildVector(Stack, n)
                    Vectorlist.append(v)
                else:
                    parseLCSmatrix(b, i+1, j+1, m, n, lcs_length-1, Stack, Vectorlist)
                Stack.pop()
    return Vectorlist  


def buildVector(Stack, n):
    """
    Building the vector list from the Stack.
    """
    list = [0]*n
    for i,j in Stack:
        list[j-1] = i
    return list


def getFirstAndLastIndex(VectorList):
    """
    Returns the first and last index of the possible acronym in Vector list
    """
    first = next((i for i, x in enumerate(VectorList) if x), None)
    reverseV = VectorList[::-1]
    last = (len(VectorList)-1) - next((i for i, x in enumerate(reverseV) if x), None)
    return first, last


def vectorValues(V, types):
    """
    Calculation of the size, distance, stopcount and misses in the vector.
    """
    dict = {}
    i = 1
    first, last = getFirstAndLastIndex(V)
    dict['size'] = last - first + 1
    dict['distance'] = (len(V)-1) - last
    dict['stopcount'] = 0
    dict['misses'] = 0
    for i in range(first, last+1):
        if (V[i] > 0 and types[i] == 's'):
            dict['stopcount'] = dict['stopcount'] + 1
        elif (V[i] == 0 and types[i] != 's' and types[i] != 'h'):
            dict['misses'] = dict['misses'] + 1
    return dict


def compareVectors(A, B, Atypes, Btypes):
    """
    Comparing two Vectors based on the number of misses, stopcount, distance and size.
    """
    if A== None and B== None:
        return None
    elif A== None:
        return B
    elif B== None:
        return A
    resultA = vectorValues(A, Atypes)
    resultB = vectorValues(B, Btypes)

    if (resultA['misses'] > resultB['misses']):
        return B
    elif (resultA['misses'] < resultB['misses']):
        return A
    if (resultA['stopcount'] > resultB['stopcount']):
        return B
    elif (resultA['stopcount'] < resultB['stopcount']):
        return A
    if (resultA['distance'] > resultB['distance']):
        return B
    elif (resultA['distance'] < resultB['distance']):
        return A
    if (resultA['size'] > resultB['size']):
        return B
    elif (resultA['size'] < resultB['size']):
        return A
    else:
        return A


def prefindAcronym(words, acronym, stopwords):
    
    """
    Finding the acronym definition using the list of paragraph words and stopwords for the given acronyms
    :param words:
    :param acronym:
    :param stopwords:
    :return:
    """
    
    # Finding the position of the word in the list.''
    index = [i for i,s in enumerate(words) if acronym in s]

    if (index):
        indexAcronym = index[0]
    else:
        return "NA"

    # Find the pre-window
    preWindowFirstIndex = indexAcronym - 2 * len(acronym)
    
    if (preWindowFirstIndex < 0):
        preWindow = words[:indexAcronym]
    else:
        preWindow = words[preWindowFirstIndex:indexAcronym]

    #Separate hyphenated words in the list
    preWindowJoin = ' '.join(preWindow)
    preWindowS = re.findall(r'\w+', preWindowJoin)
    hyphenatedWords = re.findall(r'\w+-\w+[-\w+]*',preWindowJoin)
    # Find the leaders of the pre window
    leaders = [x[0].lower() for x in preWindowS]
    pretypes = []
    for x in preWindowS:
        flagStop = x in stopwords
        if (flagStop):
            pretypes.append('s')
        else:
            flagHyphen = 0
            for word in hyphenatedWords:
                listHyphen = ''.join(word).split('-')
                indexHyphen = None
                if (x in listHyphen):
                    flagHyphen = 1
                    indexHyphen = listHyphen.index(x)
                    if (indexHyphen == 0):
                        pretypes.append('H')
                    else:
                        pretypes.append('h')
            if (not flagHyphen):
                pretypes.append('w')

    #X and Y
    X = acronym.lower()
    Y = ''.join(leaders)

    # build LCS matrix
    c,b = buildLCSmatrix(X,Y)
    m = len(X)
    n = len(Y)
    
    if (c[m][n]< len(acronym)/2):
        return 'NA'
    PreVectors = parseLCSmatrix(b, 0, 0, m, n, c[m][n], [], [])

    precontext='A'
    #postcontext='A'
    PrechoiceVector= None
    #PostchoiceVector= None
    if (not PreVectors):
        return 'NA'

    else:
    # Choosing of vectors from the multiple vectors based on number of misses, stopcount, distance and size
        PrechoiceVector = PreVectors[0]
   
        for i in range(1, len(PreVectors)):
            PrechoiceVector = compareVectors(PrechoiceVector, PreVectors[i], pretypes,pretypes)

    if (PrechoiceVector== None):
        return'NA'

    finalList = []
    
    firstIndex, lastIndex = getFirstAndLastIndex(PrechoiceVector)

    countHyphen = 0
    textHyphen = ""
    for i,x in enumerate(PrechoiceVector):
        if (i>=firstIndex and i<=lastIndex):
            if (pretypes[i] == 'H' or pretypes[i] == 'h'):
                textHyphen += preWindowS[i]
                if (i+1 < len(pretypes) and pretypes[i+1] == 'h'):
                    countHyphen += 1
                    textHyphen += '-'
                    continue

                #Reset the hyphen parameters
            if (countHyphen != 0):
                textJoin = textHyphen
                textHyphen = ""
                countHyphen = 0
            else:
                textJoin = preWindowS[i]
            finalList.append(textJoin)
    return ' '.join(finalList)


def postfindAcronym(words, acronym, stopwords):
    
    """
    Finding the acronym definition using the list of paragraph words and stopwords for the given acronyms
    :param words:
    :param acronym:
    :param stopwords:
    :return:
    """
    
    # Finding the position of the word in the list.''
    index = [i for i,s in enumerate(words) if acronym in s]
    
    if (index):
        indexAcronym = index[0]
    else:
        return "NA"
    
    postcontext='A'
    PostchoiceVector= None

    '''to find out the right context'''

    postWindowLastIndex = indexAcronym + 2 * len(acronym)

    if (postWindowLastIndex > len(words)):
        postWindow = words[indexAcronym+1:]
    else:
        postWindow = words[indexAcronym+1:postWindowLastIndex]
        
     #Separate hyphenated words in the list
    postWindowJoin = ' '.join(postWindow)
    postWindowS = re.findall(r'\w+', postWindowJoin)
    hyphenatedWords = re.findall(r'\w+-\w+[-\w+]*',postWindowJoin)
    # Find the leaders of the pre window
    leaders = [x[0].lower() for x in postWindowS]
    
    posttypes = []
    for x in postWindowS:
        flagStop = x in stopwords
        if (flagStop):
            posttypes.append('s')
        else:
            flagHyphen = 0
            for word in hyphenatedWords:
                listHyphen = ''.join(word).split('-')
                indexHyphen = None
                if (x in listHyphen):
                    flagHyphen = 1
                    indexHyphen = listHyphen.index(x)
                    if (indexHyphen == 0):
                        posttypes.append('H')
                    else:
                        posttypes.append('h')
            if (not flagHyphen):
                posttypes.append('w')

    #X and Y
    X = acronym.lower()
    Y = ''.join(leaders)

    # build LCS matrix
    c,b = buildLCSmatrix(X,Y)
    m = len(X)
    n = len(Y)
    
    if (c[m][n]< len(acronym)/2):
        return 'NA'
    PostVectors = parseLCSmatrix(b, 0, 0, m, n, c[m][n], [], [])

    #print(PostVectors)
    if (not PostVectors):
        return 'NA'
    else:
    # Choosing of vectors from the multiple vectors based on number of misses, stopcount, distance and size
        PostchoiceVector = PostVectors[0]
   
        for i in range(1, len(PostVectors)):
            PostchoiceVector = compareVectors(PostchoiceVector, PostVectors[i], posttypes,posttypes)

    if (PostchoiceVector== None):
        return 'NA'
    
    finalList = []
    
    firstIndex, lastIndex = getFirstAndLastIndex(PostchoiceVector)

    countHyphen = 0
    textHyphen = ""
    for i,x in enumerate(PostchoiceVector):
    
        if (i>=firstIndex and i<=lastIndex):
            if (posttypes[i] == 'H' or posttypes[i] == 'h'):
                textHyphen += postWindowS[i]
                if (i+1 < len(posttypes) and posttypes[i+1] == 'h'):
                    countHyphen += 1
                    textHyphen += '-'
                    continue
                #Reset the hyphen parameters
            if (countHyphen != 0):
                textJoin = textHyphen
                textHyphen = ""
                countHyphen = 0
            else:
                textJoin = postWindowS[i]
            finalList.append(textJoin)
   
    return ' '.join(finalList)

def getAccroyms(filename):
    abbr = []
    file = open("./uploads/"+filename, "rb")
    text_words = file.read().decode('utf-8').split()
    file.close()
    
    file  = open("Acronyms.csv", "w")
    file.write("{0}\n".format('Acronym'))
    for i in range(0,len(text_words)-1):
        word = text_words[i]
        z = re.match(r'[\(\[\]\{A-Z0-9][A-Z0-9,//\-_/&\.@|]{,8}[A-Z0-9 \)\]=]$',word)
        acry=("".join(re.findall("[a-zA-Z]+", word)))
        nextIndex = i+1
        prevIndex = i-1
        if(z and len(word)>1 and len(word)<10 and word[:-1].isupper() and word not in STOPWORDS and acry not in STOPWORDS and ( not(text_words[i-1].isupper()) or not(text_words[i+1].isupper()))):
            abbr.append(word) 
            file.write("{0}\n".format(word))
    file.close()
    return abbr

def accroymFinder(filename):
    result, abbr = [], []
    file = open("./uploads/"+filename, "rb")
    text_words = file.read().decode('utf-8').split()
    file.close()

    postindex, preindex = 0, 0
    file  = open("Acronyms_fullform.csv", "w")
    file.write("{0},{1},{2}\n".format('Acronym','type','defin'))

    for i in range(0,len(text_words)-1):
        word = text_words[i]
        z=re.match(r'[\(\[\]\{A-Z0-9][A-Z0-9,//\-_/&\.@|]{,8}[A-Z0-9 \)\]=]$',word)
        acry=("".join(re.findall("[a-zA-Z]+", word)))
        nextIndex = i+1
        prevIndex = i-1
        if(z and len(word)>1 and len(word)<10 and word[:-1].isupper() and word not in STOPWORDS and acry not in STOPWORDS and ( not(text_words[i-1].isupper()) or not(text_words[i+1].isupper()))):
            abbr.append(word) 
    
    for acronym in set(abbr):
        word=("".join(re.findall("[a-zA-Z]+", acronym)))
        predefin = prefindAcronym(text_words, acronym, STOPWORDS)
        postdefin= postfindAcronym(text_words, acronym, STOPWORDS)
        if(predefin not in 'NA' and len(predefin.split())<= (max(2*len(acronym),len(acronym)+5))):
            if(predefin.split()[-1].lower() not in STOP_LIST and predefin.split()[0].lower() not in STOP_LIST):
                file.write("{0},{1},{2}\n".format(acronym, "left", predefin))
                preindex += 1
                result.append([acronym, "left", predefin])
                print(acronym + '--'+ 'left'+'>>>>'+predefin)
        if(postdefin not in 'NA' and len(postdefin.split())<= (max(2*len(acronym),len(acronym)+5))):
            if(postdefin.split()[-1].lower() not in STOP_LIST and postdefin.split()[0].lower() not in STOP_LIST):
                file.write("{0},{1},{2}\n".format(acronym, "right", postdefin))
                postindex += 1
                result.append([acronym, "right", postdefin])
                print(acronym + '--'+'right'+'>>>>'+ postdefin)
    file.close()         
    return result 


def getAllAcronyms():
    
    acronyms = []
    try:
        file = open("acronyms.csv", "r")
        acronyms = [row.split(",")[0] for row in file]
    except:
        pass

    file.close()
    return acronyms

def getAcronymFullForm(acronym):
    fullForm  = ""

    try:
        file = open("acronyms.csv", "r")
        fullFormsDict = {row.split(",")[0].upper() :  row.split(",")[2] for row in file}
        fullForm = fullFormsDict[acronym.upper()]
    except:
        pass

    file.close()
    return fullForm


def cal_precision():
   f1= pd.read_csv("Acronyms_fullform.csv")
   f2= pd.read_csv("Acronyms.csv")
   count=0
   ACCR1={}
   ACCR2={}
   if ".txt" in filename:
       for i,row in f2.iterrows():
           if str(row.Acronym) not in ACCR1:
               ACCR1[str(row.Acronym)]=""
               count+=1

       for j,row in f1.iterrows():
           if str(row.Acronym) not in ACCR2:
               ACCR2[str(row.Acronym)]=""
       final_dict = dict(ACCR1.items() & ACCR2.items())
       precision= (len(final_dict)/count+1)*100
       #print(precision)
       return precision
   elif ".csv" in filename:
       for i,row in f2.iterrows():
           if (str(row.Acronym),str(row[1])) not in ACCR1:
               ACCR1[(str(row.Acronym),str(row[1]))]=""
               count+=1

       for j,row in f1.iterrows():
           if (str(row.Acronym),str(row[2])) not in ACCR2:
               ACCR2[(str(row.Acronym),str(row[2]))]=""
       final_dict = dict(ACCR1.items() & ACCR2.items())
       precision= (len(final_dict)/(count+1))*100
       #print(precision)
       return precision