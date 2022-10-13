from time import sleep
from pathlib import Path
from pprint import pprint as pp
import json
import os,sys
import requests

package_root = os.path.dirname(os.path.realpath(__file__))+"/.."
sys.path.append(package_root)

from ichimoe.ichimoe_deconstructor import deconstruct

TATOEBA_FILENAME = "tatoeba.tsv"

#TODO:add download tsv functiton


if TATOEBA_FILENAME not in os.listdir():
    raise FileNotFoundError("Please download the sentence pairs tsv file from this link:\
            https://tatoeba.org/en/downloads\n and name it ", TATOEBA_FILENAME)
    exit()

if "cache.json" not in os.listdir():
    os.system("echo '{}' > cache.json")

with open('cache.json') as json_file:
    cache = json.load(json_file)

tatoeba_sentences = []

def clean_text(word):
    return word.split("\n")[0]

def clean_word(word):
    #removes unnessesery characters and returns the 'clean' word
    return word.split("【")[0].replace(' ',"").replace("1.","").replace("2.","").replace("3.","").replace("4.","")

def sublist(lst1, lst2):
   ls1 = [element for element in lst1 if element in lst2]
   ls2 = [element for element in lst2 if element in lst1]
   return ls1 == ls2

# open .tsv file
with open(TATOEBA_FILENAME) as f:
    for line in f:
        l = line.split('\t')
        tatoeba_sentences.append(l)

def get_destruction(text):
    global cache
    try:
        if text in cache:
            dec_text = cache[text]
        else:
            try:
                print("\rDestructing with ichimoe...", end="\r")
                dec_text = deconstruct(text)
            except:
                sleep(3600/4)
                dec_text = deconstruct(text)

            cache[text] = dec_text
            with open("cache.json", 'w') as f:
                    json.dump(cache, f)

            print(" "*50)
    except KeyboardInterrupt:
        print("Saving progress...")
        with open("cache.json", 'w') as f:
            json.dump(cache, f)
        print(" "*50)
        print("Saved!","Aborting...")
        exit()

    return dec_text

def get_sentences(word,amount=10):
    global tatoeba_sentences
    ret = []
    dec_word = get_destruction(word)
    sentences = list(filter(lambda s:word in s[1],tatoeba_sentences))
    print(word)

    for sentence in sentences:
        if (len(sentence[1])-len(sentence[1].replace("「","").replace("」","")))%2==0:
            dec_sentence=get_destruction(sentence[1])
            if sublist(dec_word,dec_sentence):
                if sentence[1] in list(map(lambda r:r["text"],ret)):
                    continue

                print("\t",len(ret),":",sentence[1])
                ret.append({
                    "text":sentence[1],
                    "trans":sentence[3],
                    "destruction":dec_sentence,
                    "source":"tatoeba"
                })

        if len(ret)>amount:
            print()
            break
    return ret

#TODO: convert main into functions, extend_n
def main():
    if "cache.json" not in os.listdir():
        os.system("echo '{}' > cache.json")

    with open('vocab.json') as json_file:
        vocab = json.load(json_file)

    for n in range(5):
        vocab_length = len(vocab["n"+str(n+1)])

        if f'n{str(n+1)}.json' in os.listdir("extended"):
            print(f'n{str(n+1)}.json already generated. Going to next n...')
            continue

        n_vocab = []
        for index, word in enumerate(vocab[f"n{n+1}"]):
            print(f"Getting n{n+1}, {index+1} of {vocab_length}")
            print(" ".join(word["writings"]))

            for example in word["examples"]:
                example["destruction"] = get_destruction(example["text"])
            word["frequiency"]=[]
            for writing in word["writings"]:
                frequiency = 0
                for sentence in get_sentences(clean_text(writing)):
                    frequiency += 1
                    word["examples"].append(sentence)
                word["frequiency"].append(frequiency)
            for example in word["examples"]:
                for dest in example["destruction"]:
                    for nn in range(1,6):
                        for v in vocab[f"n{nn}"]:
                            if clean_word(dest["word"]) in v["writings"]:
#                                print(f"'{clean_word(dest['word'])}':{v['writings']}")
                                dest["id"] = v["id"]
                                break
                                break
            n_vocab.append(word)
        if extended not in os.listdir():
            os.mkdir("extended")
        with open(f'extended/n{str(n+1)}.json', 'w') as f:
            json.dump(n_vocab, f)

if __name__ == "__main__":
    main()
