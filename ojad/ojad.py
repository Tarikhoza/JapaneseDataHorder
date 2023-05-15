import geckodriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from PIL import Image
from time import sleep
import os
import shutil
from pathlib import Path
from pprint import pprint as pp
#set options
#set webdriver to be headless, it means to make it invisble and in work in backgound
options = FirefoxOptions()
options.add_argument('-headless')
#install webdriver if needed
geckodriver_autoinstaller.install()

#setting profile so that the download folder is in the same path as the script
profile = webdriver.FirefoxProfile()




def key_out_background(file_name):
    img = Image.open(file_name)
    img = img.convert("RGBA")
    datas = img.getdata()
    newData = []
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    img.putdata(newData)
    img.save(file_name)


def get_pitched_text(text,name=None):
    if os.name == "nt":
        driver_path=os.path.join(os.getcwd(),"geckodriver.exe")
        driver = webdriver.Firefox(options=options,executable_path=driver_path)
    else:
        driver = webdriver.Firefox(options=options)


    #this function downloads the pitch accent graph, 
    #the pitch accent graphs are saved in the pitch_graph folder as png
    if "pitch_graph" not in os.listdir():
        os.mkdir("pitch_graph")

    if name == None:
        name = text
    driver.get("https://www.gavo.t.u-tokyo.ac.jp/ojad/phrasing")

    #putting text into the input field
    input_element = driver.find_element(By.ID,"PhrasingText")
    input_element.send_keys(text);

    #pressing the submit button and waiting for 5 seconds
    submit_button = driver.find_element(By.ID, "phrasing_submit_wrapper").find_element(By.TAG_NAME,"input")
    submit_button.click()
    sleep(5)

    #making a screenshot of the generated pitch accent graph
    driver.find_element(By.CLASS_NAME,"phrasing_phrase_wrapper").screenshot(f"pitch_graph/{name}.png")
    return f"pitch_graph/{name}.png"

#TODO: make a function download_all from optimised
#TODO: add custom path to get_pitched_text()

def download_pitched_vocab(expanded):
    for index,word in enumerate(expanded):
        most_used_writing = word["writings"].index(max(word["frequency"]))
        print(f"{index} of {vocab_length}", end="\r")
        if  f"w_{word['id']}.png" not in os.listdir("pitch_graph") and f"w_{word['id']}.wav" not in os.listdir("pitch_audio"):
            try:
                ojad.get_pitched_text(word["word"],name=f"w_{word['id']}")
            except Exception as e:
                print(e)
                sleep(3600/4)
                ojad.get_pitched_text(word["word"],name=f"w_{word['id']}")

#if __file__ == "__main__":
#    package_root = os.path.dirname(os.path.realpath(__file__))+"/.."
#    sys.path.append(package_root)
#    from optimiser.optimiser import best_sentence
#    for n in range(0,5):
#        with open('n{n+1}_optimised.json') as json_file:
#            n_vocab = json.load(json_file)
#        vocab_length = len(n_vocab)
#        for index,word in enumerate(n_vocab):
#            print(index, "of", vocab_length,f"n{n+1} words",end="\r")
#            if  f"w_{word['id']}.png" not in os.listdir("image") and
#                f"w_{word['id']}.wav" not in os.listdir("audio"):
#                try:
#                    ojad.get_pitched_text(word["word"],name=f"w_{word["id"]}")
#                except Exception as e:
#                    print(e)
#                    sleep(3600/4)
#                    ojad.get_pitched_text(word["word"],name=f"w_{word["id"]}")

#            if  f"s_{word['id']}.png" not in os.listdir("image") and
#                f"s_{word['id']}.wav" not in os.listdir("audio"):
#                try:
#                    ojad.get_pitched_text(best_sentence(word)["text"], name=f"s_{word["id"]}")
#                except Exception as e:
#                    print(e)
#                    sleep(3600/4)
#                    ojad.get_pitched_text(best_sentence(word)["text"], name=f"s_{word["id"]}")




