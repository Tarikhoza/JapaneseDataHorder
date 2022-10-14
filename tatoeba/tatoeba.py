from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
from pathlib import Path
from pprint import pprint as pp
import json
import os,sys
import shutil
import requests
import geckodriver_autoinstaller



package_root = os.path.dirname(os.path.realpath(__file__))+"/.."
sys.path.append(package_root)

from ichimoe.ichimoe import deconstruct



#set options
#set webdriver to be headless, it means to make it invisble and in work in backgound
options = FirefoxOptions()
options.add_argument('-headless')
#install webdriver if needed
#geckodriver_autoinstaller.install()

#setting profile so that the download folder is in the same path as the script
profile = webdriver.FirefoxProfile()
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.manager.showWhenStarting", False)
profile.set_preference("browser.download.dir", os.path.join(os.getcwd(),"download"))
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")

if os.name == "nt":
    driver_path=os.path.join(os.getcwd(),"geckodriver.exe")
    driver = webdriver.Firefox(options=options,executable_path=driver_path)
else:
    driver = webdriver.Firefox(options=options)


#intialising driver

TATOEBA_FILENAME = "tatoeba.tsv"

def download_sentence_pairs(s_language="Japanese", t_language="English",file_out="tatoeba.tsv"):
    print("Downloading sentence pairs from tatoeba.com")
    driver = webdriver.Firefox(options=options,firefox_profile=profile)
    driver.get("https://tatoeba.org/en/downloads")
    sleep(2)
    driver.find_element(By.CLASS_NAME,"export-card").click()
    driver.find_element(By.ID,"input-910").send_keys(s_language,Keys.RETURN)
    driver.find_element(By.ID,"input-911").send_keys(t_language,Keys.RETURN)
    sleep(1)
    driver.find_element(By.ID,"custom-export").find_elements(By.TAG_NAME,"button")[4].click()
    print("Waiting collection to be compiled...")
    sleep(5)
    driver.find_element(By.ID,"custom-export").find_elements(By.TAG_NAME,"button")[4].click()
    if "download" not in os.listdir():
        os.mkdir("download")
    else:
        shutil.rmtree("download")
    sleep(1)
    while len(os.listdir("download"))==0:
        sleep(1)

    file_to_move = os.path.join("download",os.listdir("download")[0])
    shutil.copy2(file_to_move, file_out)
    for i in os.listdir("download"):
        os.remove(os.path.join("download",i))
    shutil.rmtree("download")
    print("Download succesful")

if TATOEBA_FILENAME not in os.listdir():
    download_sentence_pairs()


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
        if "extended" not in os.listdir():
            os.mkdir("extended")
        with open(f'extended/n{str(n+1)}.json', 'w') as f:
            json.dump(n_vocab, f)

if __name__ == "__main__":
    main()
