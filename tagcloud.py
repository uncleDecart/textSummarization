#!/usr/bin/python3

import os, sys, re, math, csv
from collections import Counter

REDUNTANT_WORDS_FILEPATH = "./redundant/"

def extract_content(text):
    content = text.lower()
    content = re.sub('\s+', ' ', content)  # condense all whitespace
    content = re.sub('[^А-Яа-я ]+', '', content)  # remove non-alpha chars
    return content

def get_redundant_words():
    words = []
    for file in os.listdir(REDUNTANT_WORDS_FILEPATH):
        if file.endswith(".txt"):
            with open(os.path.join(REDUNTANT_WORDS_FILEPATH, file),'r') as f:
                for line in f.readlines():
                    words.append(line[:-1].lower())
    return words

class TextAnalyzer():

    def __init__(self, words):
        
        self.bigramm_frequency = {}
        self.bigramm_list = [] 
        self.words_frequency = Counter(words)
        self.N = len(self.words_frequency)
    
        prev_key = ""
        for i in range(len(words) - 1):
            bigramm = words[i:i+2]
            bigramm.sort()
            key = ' '.join(bigramm)
            if key != prev_key:
                if key in self.bigramm_frequency:
                    self.bigramm_frequency[key] += 1
                else:
                    self.bigramm_frequency[key] = 1
            prev_key = key

    def most_common_bigramms(self, amount):
        if not self.bigramm_list:
            self.bigramm_list = [[k, self.bigramm_frequency[k]] for k in sorted(self.bigramm_frequency, key=self.bigramm_frequency.get, reverse=True)]
        for i in range(amount):
            bigramm = self.bigramm_list[i]
            print(bigramm)
            print("MI:{0} t-score{1} log-likelihood:{2}".format(self.get_mi(bigramm[0]), self.get_t_score(bigramm[0]), self.get_log_likehood(bigramm[0])))

    def most_common_words(self, amount):
        print("Top {0} words".format(amount))
        for word, count in words_frequency.most_common(10):
            print("{0} : {1}".format(word, count))
     
    def f(self, params):
        if len(params) == 2:
            key = ' '.join(params)
            if key  in self.bigramm_frequency:
                return self.bigramm_frequency[key]
            else:
                return 0
        elif isinstance(params, str):
            return self.words_frequency[params]
        
    def get_mi(self, key):
        bigramm = key.split(' ')
        return math.log2((self.f(bigramm)*self.N)/(self.words_frequency[bigramm[0]]*self.words_frequency[bigramm[1]]))

    def get_t_score(self, key):
        bigramm = key.split(' ')
        return (self.f(bigramm) - (self.words_frequency[bigramm[0]]*self.words_frequency[bigramm[1]])/(self.N))/(math.sqrt(self.f(bigramm)))
     
    def get_log_likehood(self, key):
        bigramm = key.split(' ')

        O = [[0 for x in range(2)] for y in range(2)]
        E = [[0 for x in range(2)] for y in range(2)]
        
        O[0][0] = self.f(bigramm)
        O[0][1] = self.f(bigramm[0]) - self.f(bigramm)
        O[1][0] = self.f(bigramm[1]) - self.f(bigramm)
        O[1][1] = self.N - self.f(bigramm[0]) - self.f(bigramm[1]) + self.f(bigramm)

        E[0][0] = (O[0][0] + O[0][1])*(O[0][0] + O[1][0])/self.N
        E[0][1] = (O[0][0] + O[0][1])*(O[1][0] + O[1][1])/self.N 
        E[1][0] = (O[0][0] + O[1][0])*(O[1][0] + O[1][1])/self.N
        E[1][1] = (O[0][0] + O[1][0])*(O[1][0] + O[1][1])/self.N

        res = 0
        for i in range(2):
            for j in range(2):
                if O[i][j]*E[i][j] <= 0:
                    return math.inf
                else:
                    res += O[i][j]*math.log(O[i][j]/E[i][j])
        return res*2

    def to_file(self, filename, collocations_amount):
        with open(filename, 'w') as f:
            wr = csv.writer(f)
            wr.writerow(['коллокаты', 'частота слов', 'MI', 't-score', 'loglikelihood'])
            length = min(len(self.bigramm_list), collocations_amount)
            data = []
            for i in range(length): 
                collocation = self.bigramm_list[i]
                collocation += [self.get_mi(collocation[0]), self.get_t_score(collocation[0]), self.get_log_likehood(collocation[0])]
                data.append(collocation)
                #wr.writerow(collocation)
            data.sort(key=lambda x : x[2], reverse=True)
            for elem in data:
                wr.writerow(elem)

if len(sys.argv) == 2:
     
    redundant_words = get_redundant_words()
    filepath = str(sys.argv[1])
    with open(filepath, 'r') as f:
        
        content = extract_content(f.read())
        words = [w for w in content.split() if w not in redundant_words]
         
        ta = TextAnalyzer(words)
        ta.most_common_bigramms(10)
        ta.to_file('res.csv', 100) 
else:
    print("usage: ./tagcloud filepath")
