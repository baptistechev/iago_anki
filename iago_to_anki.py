from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import undetected_chromedriver as uc
import romkan
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import genanki

username = ""
password = ""

kanji_list = []
kana_list = {}
def_list = {}
example_list = {}
src_list = {}

#Last word
f = open("save","r+")
last_word = f.read()

#Connection
chrome_options = uc.ChromeOptions()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--profile-directory=Default")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--disable-plugins-discovery")
chrome_options.add_argument("--incognito")
chrome_options.add_argument("user_agent=DN")
driver = uc.Chrome(version_main=113,options=chrome_options)
driver.delete_all_cookies()

driver.get("https://app.getiago.com/login")
elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[1]/div/div/div/div/div[2]/div/div[2]/div/div[2]/div[1]/button")))

elem.click()
elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,"//*[@id=\"identifierId\"]")))
elem.send_keys(username)
elem.send_keys(Keys.RETURN)
elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id=\"password\"]/div[1]/div/div[1]/input")))
time.sleep(1)
elem.send_keys(password)
elem.send_keys(Keys.RETURN)
time.sleep(8)

cpt=0
find_last_word = False
#Main code: get all vocab
while not find_last_word:

    word_list = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id=\"__next\"]/div/div[1]/div/div[1]/div/main/div[1]/div/div/section/table/tbody")))
    words = WebDriverWait(word_list, 10).until(EC.presence_of_all_elements_located((By.XPATH, '*')))
    for word in words:

        #Get the kanji
        kanji_div = WebDriverWait(word, 10).until(EC.presence_of_all_elements_located((By.XPATH, '*')))[1]
        kanji = WebDriverWait(kanji_div, 10).until(EC.presence_of_all_elements_located((By.XPATH, '*')))[0]
        kanji = kanji.get_attribute("title") #-----------Kanji
        
        #Check if not last_word
        if kanji == last_word:
            find_last_word == True
            break

        #Check if not already in the list
        if kanji not in kanji_list:
            cpt+=1
            print("{}/{}".format(cpt))
            kanji_list.append(kanji)
            kana_list[kanji] = []
            def_list[kanji] = []
            example_list[kanji] = []
            src_list[kanji] = []
        
            kanji_div.click()    
            #Get the kanas
            kanas = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,"//*[@id=\"__next\"]/div/div[1]/div/div[1]/div/main/div[3]/div[2]/header/div/h2")))
            time.sleep(1)
            kana = romkan.to_hiragana(kanas.text[1:-1]) #--------------Kanas
            kana_list[kanji].append(kana)

            #Get the definitions
            definition_list = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[1]/div/div[1]/div/main/div[3]/div[2]/div[1]/div/div")))
            time.sleep(1)
            definitions = WebDriverWait(definition_list, 10).until(EC.presence_of_all_elements_located((By.XPATH,'*')))
            for d in definitions[1:]:
                defi = d.text.split("\n")[1] #-------------Defs
                def_list[kanji].append(defi)
            
            #Get example sentences and sources (if there is)
            try:
                example_sentence = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH,"//*[@id=\"__next\"]/div/div[1]/div/div[1]/div/main/div[3]/div[2]/div[2]/div/div[1]/div[1]/div[2]")))
                example_words = WebDriverWait(example_sentence, 10).until(EC.presence_of_all_elements_located((By.XPATH,'*')))
                time.sleep(2)
                sentence = ""
                for w in example_words:
                    sentence += w.text
                example_list[kanji].append(sentence)

                #Get source
                src = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,"//*[@id=\"__next\"]/div/div[1]/div/div[1]/div/main/div[3]/div[2]/div[2]/div/div[1]/div[2]/a/span")))
                src_list[kanji].append(src.text)
            except:
                pass

            #Exit kanji page
            exi = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,"//*[@id=\"__next\"]/div/div[1]/div/div[1]/div/main/div[3]/div[1]/button")))
            exi.click()
            
            if len(kanji_list)>=N:
                break

driver.close()

#Update last word
f.seek(0)
f.write(kanji_list[0])
f.truncate()
f.close()

#Creating Anki deck
with open('styling.css', 'r') as file:
    styling = file.read()

my_model = genanki.Model(
  1977358759,
  'Iago Card',
  fields=[
    {'name': 'Kanji'},
    {'name': 'Exemple'},
    {'name': 'Source'},
    {'name': 'Kana'},
    {'name': 'Definition'},
  ],
  templates=[
    {
      'name': 'Card 1',
      'qfmt': '{{Kanji}}<br><br><span class="example_sentence">{{Exemple}}<br>{{Source}}</span>',
      'afmt': '{{FrontSide}}<hr id="answer"><span class="kana">{{Kana}}</span><br><span class="defi">{{Definition}}</span>',
    },
  ],css = styling)

my_deck = genanki.Deck(
  1092277170,
  'Iago Deck')

kanji_list.reverse()
for k in kanji_list:
    
    the_def = def_list[k][0]
    for d in def_list[k][1:]:
        the_def += "<br>" + d 
    
    if example_list[k] != []:

      my_note = genanki.Note(
        model=my_model,
        fields=[k,example_list[k][0],'('+src_list[k][0]+')',kana_list[k][0],the_def])
    else:
        my_note = genanki.Note(
        model=my_model,
        fields=[k,'','',kana_list[k][0],the_def])
    
    my_deck.add_note(my_note)

genanki.Package(my_deck).write_to_file('iago_deck.apkg')
