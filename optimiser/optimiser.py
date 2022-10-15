import json
from random import shuffle
from pprint import pprint as pp
import numpy as np
import matplotlib.pyplot as plt
import os
from PIL import Image
import PIL
import sys


kanji_ranges = [
        ( 0x4E00,  0x62FF),
        ( 0x6300,  0x77FF),
        ( 0x7800,  0x8CFF),
        ( 0x8D00,  0x9FCC),
        ( 0x3400,  0x4DB5),
        (0x20000, 0x215FF),
        (0x21600, 0x230FF),
        (0x23100, 0x245FF),
        (0x24600, 0x260FF),
        (0x26100, 0x275FF),
        (0x27600, 0x290FF),
        (0x29100, 0x2A6DF),
        (0x2A700, 0x2B734),
        (0x2B740, 0x2B81D),
        (0x2B820, 0x2CEAF),
        (0x2CEB0, 0x2EBEF),
        (0x2F800, 0x2FA1F)
    ]



def is_kanji(char):
    char = ord(char)
    for bottom, top in kanji_ranges:
        if char >= bottom and char <= top:
            return True
    return False

def kanji_only(text):
    #every character that is not kanji from string
    return "".join(list(filter(lambda c:is_kanji(c),text)))

with open("data/heisig.json") as json_file:
    heisig = json.load(json_file)

with open("data/kklc.json") as json_file:
    kklc = json.load(json_file)

def clean_word(word):
    #removes unnessesery characters and returns the 'clean' word
    return word.split("【")[0].replace(' ',"").replace("1.","").replace("2.","").replace("3.","").replace("4.","")


def sentence_difficulty(sentence_with_desturction):
    word_difficulties = []
    for word in sentence_with_desturction["destruction"]:
        for n in range(1,6):
            n_vocab = load_n(f"extended/n{n}.json")
            #pun not intended
            for n_word in n_vocab:
                if clean_word(word["word"]) in " ".join(n_word["writings"]):
                    word_difficulties.append(n)
                    break
                    break
    sentence_with_desturction["difficulty"] = max(word_difficulties)



def high_minus_low(num1,num2):
    if num1>num2:
        return num1-num2
    return num2-num1

def word_relation(word1,word2):
    #frequiency
    #getting most used writing style for word
    most_used1 = word1["writings"][word1["frequiency"].index(max(word1["frequiency"]))]
    most_used2 = word2["writings"][word2["frequiency"].index(max(word2["frequiency"]))]
    most_used1 = word1["writings"][0]
    most_used2 = word2["writings"][0]


    rating = len(kanji_only(most_used1))+len(kanji_only(most_used2))
    same = set(kanji_only(most_used1))-set(kanji_only(most_used2))
    rating -= len(same)


def kanji_index(kanji_string,kanji_list="heisig"):
    global heisig,kklc
    indexes=[]
    if kanji_list=="heisig":
        kanji = heisig
    elif kanji_list=="kklc":
        kanji = kklc

    for i in kanji_string:
        if i in kanji:
            indexes.append(kanji.index(i))
    return indexes


def relative_position(word,kanji_list="heisig"):
    #getting most used writing style for word
    most_used = word["writings"][word["frequiency"].index(max(word["frequiency"]))]
    used_kanji = kanji_only(most_used)
    kanji_indexes = kanji_index(used_kanji,kanji_list=kanji_list)
    ret = 0
    for index,i in enumerate(kanji_indexes):
        ret+=i*1000/(index+1)
    return ret

def rate_sentence(word, dep):
    #word is a member of the vocab json, and dep is the dependency set
    #gives every sentence a rating
    #lower is better
    # if there are no sentences for the word give max rating of 999999 is given
    ratings = []

    if(len(word["examples"]) == 0):
        word["min_rating"] = 999999
        word["max_rating"] = 999999
        word["dep"]=len(dep)
        return word["min_rating"]

    for sentence in word["examples"]:
        sentence_difficulty(sentence)
        try:
            sentence_words = set(map(lambda w:clean_word(w["word"]),sentence["destruction"]))
            sentence["rating"] = len(sentence_words)-len(sentence_words&dep)
            ratings.append(sentence["rating"])
        except:
            sentence["rating"] = 999999
    word["min_rating"] = min(ratings)
    word["max_rating"] = max(ratings)
    word["dep"] = len(dep)
    return word["min_rating"]

def rate_optimised(optimised_list):
    #optimised_list is a list of optimised lists
    #rate([optimised_n1,optimised_n2,optimised_n3...])
    #It returns an integer that symbolises the rating of the optimised list
    #Lower is better

    rating = 0

    for optimised in optimised_list:
        ratings = list(map(lambda word:best_sentence(word)["rating"],optimised))
        rating += np.asarray(ratings).sum()

    return rating

def best_sentence(word):
    #returns the example sentence with the lowest rating
    if len(word["examples"])>0:
        return sorted(word["examples"], key = lambda s:s["rating"])[-1]


def optimise(file_in,file_out,dep = None, throw_out=True,order="normal"):
    #file_in is the file name that should be loaded, it is a string
    #file_out is the file name that the optimsed list should be saved, it is a string
    #dep is the dependency set, is is a set of strings
    #throw_out is a bool, if True throw out the words without sentences
    #the dependency set symbolises the words that someone has learned before
    #it is the sum of all words in previous best example sentences
    #the goal is to learn only one new word at a time
    #so we want as few unknown words as possible so we can focus just on the word we are currently learning
    #this problem is an NP problem so there is no optimal solution for without spending an internery on computing this solution
    #because of that we will shuffle the vocab every time and generate different results and select the with the best ratings
    #order is a string, it decides which ordering mode is used
    #There are:
    #the heisig order(order that uses the heisig order to sort the words and chooses the best word in range
    #the kklc order(order that uses the kklc order to sort the words and chooses the best word in range
    #the normal order just gets the best order that and
    #the shuffle order shuffles the words every time
    if dep == None:
        dep=set()
    no_sentence_words = []
    with open(file_in) as json_file:
        print(f"Loading {file_in}...")
        vocab = json.load(json_file)

    vocab_length = len(vocab)
    print(f"Loaded {vocab_length} words.")
    optimised = []

    #with these loops we go trough every word in vocab and compare their example sentences with our already learned words
    #we choose the word with the best rating and put it into the optimised list and remove it from the vocab list
    #in the end we have a suboptimal ordered list with words all words if possible have only one new word
    #if possible we should get example sentences for every word, so that our list is complete
    print(f"Using '{order}' ordering system...")
    while len(vocab)>0:
        print(vocab_length-len(vocab),"of", vocab_length, end="\r")
        if order == "normal":
            vocab = sorted(vocab,key=lambda w:rate_sentence(w,dep))

        elif order=="heisig":
            vocab = sorted(vocab,key=lambda w:rate_sentence(w,dep)+relative_position(w))

        elif order=="kklc":
            vocab = sorted(vocab,key=lambda w:rate_sentence(w,dep)+relative_position(w,kanji_list="kklc"))

        elif order == "shuffle":
            shuffle(vocab)
            vocab = sorted(vocab,key=lambda w:rate_sentence(w,dep))
        else:
            raise NameError(f'Ordering mode:"{order}" does not exist.\n Only "normal","heisig", and "shuffle" exist.')
        best_word = vocab[0]
        best_example = best_sentence(best_word)
        if best_example != None and "destruction" in best_example:
            example_words = set(map(lambda w:clean_word(w["word"]),best_example["destruction"]))
            for w in example_words:
                #dep.add(w)
                pass
        else:
            no_sentence_words.append(best_word)
            if throw_out:
                vocab.pop(0)
                continue
        optimised.append(best_word)
        vocab.pop(0)

    with open(file_out, 'w') as fp:
        json.dump(optimised, fp)

    print(f"Optimised {file_in} with {len(no_sentence_words)} words without sentences")
    return optimised, dep



def savefig(optimised,title,order,rating,path):
    plt.suptitle(f"{order} - Score:{rating}")
    plt.title(title)
    plt.xlabel("Word")
    plt.ylabel("Difficulty")
    plt.plot(list(map(lambda word:word["min_rating"],optimised)))
    plt.savefig(path, bbox_inches='tight')
    plt.clf()

def merge_images(images,file_out="optimised/graph.png"):
    imgs    = [ Image.open(i) for i in images]
# pick the image which is the smallest, and resize the others to match it (can be arbitrary image shape here)
    min_shape = sorted( [(np.sum(i.size), i.size ) for i in imgs])[0][1]
    imgs_comb = np.hstack( (np.asarray( i.resize(min_shape) ) for i in imgs ) )

# save that beautiful picture
    imgs_comb = Image.fromarray( imgs_comb)
    imgs_comb.save(file_out)

# for a vertical stacking it is simple: use vstack
#    imgs_comb = np.vstack( (np.asarray( i.resize(min_shape) ) for i in imgs ) )
#    imgs_comb = Image.fromarray( imgs_comb)
#    imgs_comb.save( 'Trifecta_vertical.jpg' )

def optimise_all(order="normal",shuffle_list=True):
    if "optimised" not in os.listdir():
        os.mkdir("optimised")

    optimised_n5, dep = optimise("extended/n5.json","optimised/optimised_n5.json",order=order)
    optimised_n4, dep = optimise("extended/n4.json","optimised/optimised_n4.json",order=order, dep=dep)
    optimised_n3, dep = optimise("extended/n3.json","optimised/optimised_n3.json",order=order, dep=dep)
    optimised_n2, dep = optimise("extended/n2.json","optimised/optimised_n2.json",order=order, dep=dep)
    optimised_n1, dep = optimise("extended/n1.json","optimised/optimised_n1.json",order=order, dep=dep)

    rating = rate_optimised([
        optimised_n5,
        optimised_n4,
        optimised_n3,
        optimised_n2,
        optimised_n1
    ])

    savefig(optimised_n5,"N5",order,rating,"optimised/N5graph.png")
    savefig(optimised_n4,"N4",order,rating,"optimised/N4graph.png")
    savefig(optimised_n3,"N3",order,rating,"optimised/N3graph.png")
    savefig(optimised_n2,"N2",order,rating,"optimised/N2graph.png")
    savefig(optimised_n1,"N1",order,rating,"optimised/N1graph.png")

    merge_images([
        "optimised/N5graph.png",
        "optimised/N4graph.png",
        "optimised/N3graph.png",
        "optimised/N2graph.png",
        "optimised/N1graph.png",
        ])

    os.rename("optimised","optimised_"+str(rating))
    print("Optimised with rating:",rating)

def load_n(n_path):
    with open(n_path) as f:
        return json.load(f)

def print_n(n,amount):
    for i in range(amount):
        pp(" ".join(n[i]["writing"]))
        pp(best_sentence(n[i])["text"],best_sentence(n[i])["rating"])
