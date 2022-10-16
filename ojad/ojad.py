#import geckodriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from PIL import Image
from time import sleep
import os
import shutil
from pathlib import Path

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
    #this function downloads the pitch accent graph, as well as the audio generated from OJAD-Suzuki-kun
    #the audio is saved in the audio folder as wav and the pitch accent graphs are saved in the image folder as png
    if "pitch_graph" not in os.listdir():
        os.mkdir("pitch_graph")

    if "pitch_audio" not in os.listdir():
        os.mkdir("pitch_audio")
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
    generate_btn=driver.find_element(By.ID,"phrasing_main").find_elements(By.CLASS_NAME,"submit")

    #executing the JS function to generate the audio
    driver.execute_script("synthesis_and_get_filename()")
    sleep(5)

    #executing the JS function to download the audio

    driver.execute_script("wav_filename_save()")
    sleep(5)


    #waiting for the download to complete
    while len(os.listdir("download"))==0:
        sleep(1)

    #the audio is saved in the download folder
    #we don't know the name of the downloaded file
    #only one file should be in the download folder and this is the downloaded audio
    #we can move it to the audio folder and rename it
    #we expect only the audio file in the folder

    file_to_move = os.path.join("download",os.listdir("download")[0])

    audio_path = os.path.join(os.getcwd(),"pitch_audio",name + ".wav")
    shutil.copy2(file_to_move, audio_destination)
    sleep(1)

    #remove every file from download folder
    for i in os.listdir("download"):
        os.remove(os.path.join("download",i))
    #returns audio path, image path
    return audio_path,f"pitch_graph/{name}.png"

#TODO: make a function download_all from optimised
#TODO: add custom path to get_pitched_text()

def download_pitched_vocab(vocab):
    vocab_length = len(vocab)
    for index,word in enumerate(vocab):
        most_used_writing = word["writings"].index(max(word["writings"]["frequency"]))
        print(f"{index} of {vocab_length}", end="\r")
        if  f"w_{word['id']}.png" not in os.listdir("image") and
            f"w_{word['id']}.wav" not in os.listdir("audio"):
            try:
                ojad.get_pitched_text(word["word"],name=f"w_{word["id"]}")
            except Exception as e:
                print(e)
                sleep(3600/4)
                ojad.get_pitched_text(word["word"],name=f"w_{word["id"]}")

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




