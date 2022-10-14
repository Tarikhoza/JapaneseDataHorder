from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from time import sleep
import os
import json
#import geckodriver_autoinstaller
#geckodriver_autoinstaller.install()

options = FirefoxOptions()
options.add_argument('-headless')

if os.name == "nt":
    driver_path=os.path.join(os.getcwd(),"geckodriver.exe")
    driver = webdriver.Firefox(options=options,executable_path=driver_path)
else:
    driver = webdriver.Firefox(options=options)




URL = "https://takoboto.jp/lists/study/n{}vocab/?page={}"
WORD_URL = "https://takoboto.jp/?w={}"

def get_vocab(n,page):
    driver.get(URL.format(n,page))
    word_banner = driver.find_elements(By.CLASS_NAME,"ResultDiv")
    banner_count = 0
    vocab=[]
    word_ids = []

    for i in word_banner:
        banner_count=max([banner_count,int(i.get_attribute('id').replace("ResultWord",""))])

    for i in range(banner_count + 1):
        banner = driver.find_element(By.ID,"ResultWord"+str(i))
        word_id = banner.get_attribute("onclick").replace("onResultClick(","").replace(")","").split(",")[2]
        word_ids.append(word_id)

    for i,word_id in enumerate(word_ids):
        print(f"Getting {i+1} word of {len(word_ids)}")
        word = get_word_by_id(word_id,n)
        sleep(1)
        if word != None:
            vocab.append(word)

    return vocab

def get_word_by_id(word_id,n):
    try:
        driver.get(WORD_URL.format(word_id))
        container = driver.find_element(By.CLASS_NAME,'WordJapDiv');
        writings = []
        examples = []
        usages = []
        trans = []
        notes = []
        last_id = 0
        driver.execute_script("""
                for(var con of document.getElementsByTagName("div")){
                    con.style.width="fit-content"
                    con.style.border="none";
                    con.style.color="gray";
                }
            """
        )

        while True:
            if(container.get_attribute("class")!='WordJapDiv'):
                break
            last_id = int(container.get_attribute("id").replace("WordJapDiv",""))
            writings.append(container.find_element(By.TAG_NAME,"span").text )
            container = container.find_element(
                    By.XPATH,"//div[@id='{}']/following-sibling::div".format(
                        container.get_attribute("id")
                    )
            )

        try:
            container = driver.find_element(By.ID,"WordJapDiv"+str(last_id+1)).find_element(By.XPATH,"..")
            writings.append(container.find_element(By.TAG_NAME,"span").text)
            container.screenshot("accent/"+word_id+".png")
        except:
            print("No accent")

        eng = driver.find_element(By.CSS_SELECTOR, "img[src*='/flags/en.png']").find_element(By.XPATH,"../../..").find_elements(By.CSS_SELECTOR, "img[src*='/flags/en.png']")

        for i in eng:
            trans.append(i.find_element(By.XPATH,"..").text)
            usages.append(i.find_element(By.XPATH,"../..").find_element(By.TAG_NAME,"span").text)

        try:
            examples_container = driver.find_elements(By.CSS_SELECTOR, "img[src*='/flags/en.png']")[-1]
            examples_container = examples_container.find_element(By.XPATH,"../../..").find_elements(By.CSS_SELECTOR, "img[src*='/flags/en.png']")
            driver.find_element(By.ID, "MorePhrasesDiv").find_element(By.TAG_NAME, "a").click()
            sleep(1)
            for example in examples_container:
                divs = example.find_element(By.XPATH,"../..").find_elements(By.TAG_NAME,"div")
                jap = divs[0].text
                translation = divs[2].text
                examples.append({"text":jap,"trans":translation})
        except:
            print("No examples")
        return {
            "id":word_id,
            "writings":writings,
            "examples":examples,
            "usages":usages,
            "trans":trans,
            "source":"takoboto",
            "n":n
        }
    except Exception as e:
        print(e)
        print("Something went wrong but we are going on...")
        return None

#TODO:add progress saving feature to download_n_vocab


def download_n_vocab(n,overwrite = False,file_out=""):
    n_pages = [68,36,63,12,12]
    pages = n_pages[n-1]
    vocab=[]
    if file_out == "":
        file_out = f"N{n}.json"

    if(file_out not in os.listdir() or overwrite==True):
        for page in range(pages):
            print(f"N{n},Page {page+1} of {pages}")
            v = get_vocab(n,page+1)
            for i in v:
                vocab.append(i)

        with open(file_out, 'w') as f:
            json.dump(vocab, f)
            print(f"Downloading vocab finished. \nSaved vocab into {file_out}.")
    else:
        print(f"Warning: {file_out} already generated.\n If you want to overwrite it please use download_all_vocab(overwrite=True)")
    return vocab

def load_n_vocab(n,file_in=""):
    if file_in == "":
        file_in = f"N{n}.json"
    if file_in in os.listdir():
        with open(file_in) as f:
            return json.load(vocab, f)
    else:
        raise FileNotFoundError(f"{file_in} does not exist. Have you downloaded it with download_n_vocab()?")

def load_all_vocab(file_in="vocab.json"):
    if file_in in os.listdir():
        with open(file_in) as f:
            return json.load(vocab, f)
    else:
        raise FileNotFoundError(f"{file_in} does not exist. Have you downloaded it with download_all_vocab()?")


def download_all_vocab(overwrite = False,file_out="vocab.json"):
    #downloads vocab from list N1 - N5 and saves it to file_out
    #overwrite argument decides if files with the same file name as file_out get overwritten or not
    #file_out argument is the file name where the downloaded data is saved
    vocab = {}
    if file_out not in os.listdir():
        for n in range(1,6):
            vocab[f"N{n}"] = download_n_vocab(n,overwrite = overwrite)
        with open(file_out, 'w') as f:
            json.dump(vocab, f)
        return vocab
    return load_all_vocab(file_out="vocab.json")


