import requests
import bs4

URL = "https://ichi.moe/cl/qr/?q={}&r=htr"

def get_gloss(sentence):
    req = requests.get(URL.format(sentence))
    soup = bs4.BeautifulSoup(req.text,"html.parser")
    return soup.find(class_="gloss-all")

def deconstruct(sentence):
    gloss = get_gloss(sentence)
    try:
        meaning_containers=gloss.find_all(class_="gloss-content")
        meanings = []
        for i in meaning_containers:
            container=i.find(class_="alternatives")
            if type(container)!=type(None):
                word=container.find("dt")
                defi=container.find("dd")
                meanings.append({
                        "word":word.text.replace("  ",""),
                        "definition":defi.text.replace("  ","")
                        }
                    )
    except Exception:
        return []

    return meanings
