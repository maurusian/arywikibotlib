import pywikibot
import traceback
from pywikibot.exceptions import NoPageError
import json, os

#for functionalities presumably not covered by the API
import requests
from bs4 import BeautifulSoup
from copy import deepcopy

###################   Helpful Constants   #######################

PARAM_FILE_PAGE_TTL = "ميدياويكي:پاراميطرات عامة.json"

REQUEST_HEADER = {
        'User-Agent': 'DarijaBot/0.1 (Edition Windows 10 Home, Version 20H2, OS build 19042.1165, Windows Feature Experience Pack 120.2212.3530.0) Python3.9.0',
        'Content-Type': 'text/text; charset=utf-8'
    }

PARAMS = {'GLOBAL_IGNORE_LIST':["الصفحة اللولا"]
          }

MONTHS = [{"en_name":"January","ary_name":u"يناير","day_count":31,"alt_name":""}
         ,{"en_name":"February","ary_name":u"فبراير","day_count":29,"alt_name":u"يبراير"}
         ,{"en_name":"March","ary_name":u"مارس","day_count":31,"alt_name":""}
         ,{"en_name":"April","ary_name":u"أبريل","day_count":30,"alt_name":""}
         ,{"en_name":"May","ary_name":u"ماي","day_count":31,"alt_name":""}
         ,{"en_name":"June","ary_name":u"يونيو","day_count":30,"alt_name":""}
         ,{"en_name":"July","ary_name":u"يوليوز","day_count":31,"alt_name":""}
         ,{"en_name":"August","ary_name":u"غشت","day_count":31,"alt_name":""}
         ,{"en_name":"September","ary_name":u"شتنبر","day_count":30,"alt_name":""}
         ,{"en_name":"October","ary_name":u"أكتوبر","day_count":31,"alt_name":u"كتوبر"}
         ,{"en_name":"November","ary_name":u"نونبر","day_count":30,"alt_name":""}
         ,{"en_name":"December","ary_name":u"دجنبر","day_count":31,"alt_name":""}]

LANGUAGES = {'fr':'French'
            ,'ar':'Arabic'
            ,'es':'Spanish'
            ,'sv':'Swedish'
            ,'en':'English'
            ,'de':'German'
            ,'pt':'Portuguese'
            ,'it':'Italian'
            ,'pl':'Polish'
            ,'el':'Greek'
            ,'lij':'Ligurian'
            ,'vec':'Venetian'}

#POINT_EVENT_TYPE_CODES = []
#PERIOD_EVENT_TYPE_CODES = []

DIACRITICS = "ًٌٍَُِّْٰٖٗ'ٗ'"


###################   Gerenal Help Functions   #######################
def extractYearDay(time):
    full_date = time.split('T')[0]

    year = int(full_date[:-6])
    daymonth = full_date[-2:]+full_date[-5:-3]

    return year, daymonth

#return ary month name by number, example: 2 => فبراير
def getMonthName(number):
    if number < 1 or number > 12:
        return None
    else:
        return MONTHS[number-1]["ary_name"]

#load json params from params.json
def load_params():
    with open("./params.json",'r',encoding="utf8") as p:
        json_str = p.read()

        json_obj = json.loads(json_str)

        return json_obj

#PARAMS = load_params()

#load page titles from recent log
def load_pages_in_log(RECENT_LOG_FILE):
    if not os.path.exists(RECENT_LOG_FILE):
        return []
    with open(RECENT_LOG_FILE,'r',encoding='utf-8') as f:
        page_name_list = f.read().strip().splitlines()
    
    for i in range(len(page_name_list)):
        page_name_list[i] = page_name_list[i].strip()
    
    return page_name_list

#verify page should not be ignored
def validate_page(page,namespace,page_type,task_number,option):
    if page.title() in PARAMS['GLOBAL_IGNORE_LIST']:
        return False
    return True



###################   Wikidata Functions   #######################
def getItemPropertyNumericId(page,property_x_code):
    try:
        item = pywikibot.ItemPage.fromPage(page)
        
        return list(item.get()["claims"][property_x_code])[0].toJSON()['mainsnak']['datavalue']['value']['numeric-id']
    except NoPageError:
        #print(traceback.format_exc())
        return None
    except KeyError:
        print("Item does not have the property "+str(property_x_code))
        #print(traceback.format_exc())
        return None

def getItemPropertyNumericIds(page,property_x_code): #all IDs
    try:
        item = pywikibot.ItemPage.fromPage(page)

        IDs = []

        lis = list(item.get()["claims"][property_x_code])

        for el in lis:
            IDs.append(el.toJSON()['mainsnak']['datavalue']['value']['numeric-id'])
        return IDs
    except NoPageError:
        #print(traceback.format_exc())
        return None
    except KeyError:
        print("Item does not have the property "+str(property_x_code))
        #print(traceback.format_exc())
        return None

def getItemPropertyValue(page,property_x_code):
    try:
        item = pywikibot.ItemPage.fromPage(page)

        return getItemPropertyValueFromItem(item,property_x_code)
    except NoPageError:
        #print(traceback.format_exc())
        return None
    except KeyError:
        print("Item does not have the property "+str(property_x_code))
        #print(traceback.format_exc())
        return None

def getItemPropertyValueFromItem(item,property_x_code):
    """
    TODO: should get highest ranking value
    """
    try:
        item_value_list = list(item.get()["claims"][property_x_code])

        if len(item_value_list) == 0:
            return None

        if len(item_value_list) == 1:
            item_value_dict = item_value_list[0].toJSON()['mainsnak']['datavalue'] #['value']

        else:
            found_preferred = False
            for item in item_value_list:
                #print(item.toJSON()["rank"])
                if item.toJSON()["rank"] == "preferred":
                    
                    item_value_dict = item.toJSON()['mainsnak']['datavalue']
                    found_preferred = True
            if not found_preferred:
                item_value_dict = item_value_list[0].toJSON()['mainsnak']['datavalue']
                    
        #print(list(item.get()["claims"][property_x_code]))
        #print(item_value_dict)
        entity_type = item_value_dict['type']

        if entity_type == 'wikibase-entityid':
            return item_value_dict['value']['numeric-id']
        elif entity_type == 'time':
            #print("time: "+item_value_dict['value']['time'])
            #print("precision: "+str(item_value_dict['value']['precision']))
            return item_value_dict['value']['time'], int(item_value_dict['value']['precision'])
        else:
            print("Entity type "+entity_type+" not handled")
            return item_value_dict
    except NoPageError:
        print(traceback.format_exc())
        return None
    except KeyError:
        print("Item does not have the property "+str(property_x_code))
        #print(traceback.format_exc())
        return None


def has_wikipedia_article(qid, lang):
    repo = pywikibot.Site().data_repository()
    item = pywikibot.ItemPage(repo, qid)
    if item.exists():
        sitelinks = item.sitelinks
        return lang + 'wiki' in sitelinks.keys()
    return False

def get_lang_page_from_item(qid):
    pass

def getItemIdentity(page):
    return 'Q'+str(getItemPropertyNumericId(page,"P31"))

def getItemIdentities(page):
    IDs = getItemPropertyNumericIds(page,"P31")
    if IDs is not None and len(IDs) > 0:
        return ['Q'+str(ID) for ID in IDs if ID is not None]

    return []

def getItemIdentitiesFromItem(item):
    #IDs = getItemPropertyNumericIds(page,"P31")
    try:
        IDs = []

        lis = list(item.get()["claims"]["P31"])

        for el in lis:
            IDs.append(el.toJSON()['mainsnak']['datavalue']['value']['numeric-id'])
        return IDs
    except NoPageError:
        #print(traceback.format_exc())
        return None
    except KeyError:
        print("Item does not have the property P31")
        #print(traceback.format_exc())
        return None
    if IDs is not None and len(IDs) > 0:
        return ['Q'+str(ID) for ID in IDs if ID is not None]

    return []

def isHuman(page):
    
    return (getItemIdentity(page) == 5) #human entity Wikidata code = Q5

def hasPropertyXValue(page,property_x_code,value_wd_code):
    try:
        item = pywikibot.ItemPage.fromPage(page)

    except NoPageError:
        #print(traceback.format_exc())
        return None
    except KeyError:
        print("Item does not have the property P31")
        #print(traceback.format_exc())
        return None
    
    return value_wd_code == getItemPropertyNumericId(page,property_x_code)

def isPointEvent(page):
    return False

def isPeriodEvent(page):
    return False

def interlink_page_with_qid(page, lang, qid, namespace):
    site = pywikibot.Site(lang, 'wikipedia')
    #page = pywikibot.Page(site, page_title)
    
    repo = site.data_repository()
    item = pywikibot.ItemPage(repo, qid)
    
    if item.exists():
        sitelinks = item.sitelinks
        if lang + "wiki" not in sitelinks.keys():
            #sitelinks[lang + 'wiki'] = page.title()
            item.setSitelink(page, summary=u'Setting sitelink by ary '+namespace)


def interlink_page(ary_page,lang_page,lang,namespace): #lang is not needed
    try:
        item = pywikibot.ItemPage.fromPage(ary_page)
        print(len(item.sitelinks.keys()))
        if len(item.sitelinks.keys()) == 1:
            #MESSAGE = ""
            #write_to_task_wikilog(WIKILOG,MESSAGE)
            return False
        #TODO: check if isolated object
        return True #nothing to link
    except:
        print(traceback.format_exc())
        try:
            item = pywikibot.ItemPage.fromPage(lang_page)
            
            if 'arywiki' not in item.sitelinks.keys():
                item.setSitelink(ary_page, summary=u'Setting sitelink by adding ary '+namespace)
                #print("Linked ary page with "+LANGUAGES[lang]+" equivalent")
                return True

            
        except:
            print(traceback.format_exc())
            return False


###################   Wikipedia Functions   #######################
def getOnlyArticles(site):
    """
    Returns a generator that contains only articles (with no redirects)
    """
    return site.allpages(namespace=0,filterredir=False)

def get_user_edit_count(username,section1,section2):
    """
    Returns edit count for user with username=username as an integer.
    Returns 0 if there's an error with the retrieval process.
    Input:
    -username
    - section1: usually the language code. Can also be "www" (for wikidata),
    "meta" for meta.wikimedia.org, "commons", etc.
    -section2: usually the project or website, e.g. "wikipedia", "wiktionary",
    "wikimedia", "wikidata"...
    """
    url = "https://en.wikipedia.org/wiki/Special:CentralAuth?target="+username

    response = requests.get(url,headers=REQUEST_HEADER)

    soup = BeautifulSoup(response.content, 'html.parser')

    elements = soup.find_all('a',{"href":"//"+section1+"."+section2+".org/wiki/Special:Contributions/"+username})

    #print(len(elements))

    try:

        return int(elements[0].get_text().replace(',',''))

    except:
        print(traceback.format_exc())
        return 0


def get_all_subcategories(site,category_name):
    print(category_name)
    category = pywikibot.Category(site, category_name)
    subcategories = set(category.subcategories())
    #print(subcategories)
    temp = deepcopy(subcategories)

    while True:
        for cat in temp:
            subcategories = subcategories.union(set(cat.subcategories()))
            #print(set(cat.subcategories()))
        if len(subcategories) == len(temp):
            break
        temp = deepcopy(subcategories)

    return subcategories

################# Generic help functions ####################

def print_to_console_and_log(MSG,LOCAL_LOG):
    MESSAGE = MSG+'\n'
    with open(LOCAL_LOG,'a',encoding="utf-8") as log:
        log.write(MESSAGE)
    print(MSG)

def load_pages_in_log(RECENT_LOG_FILE):
    if not os.path.exists(RECENT_LOG_FILE):
        return []
    with open(RECENT_LOG_FILE,'r',encoding='utf-8') as f:
        page_name_list = f.read().strip().splitlines()
    
    for i in range(len(page_name_list)):
        page_name_list[i] = page_name_list[i].strip()
    
    return page_name_list



if __name__=='__main__':

    #time = '+00000001969-06-28T00:00:00Z'

    #print(extractYearDay(time))

    #lis = [4,8,1,-9,23,1,457,813153,1531,-98]
    #lis.sort()
    #print(lis)
    print(PARAMS)
    #title = "نتيخابات تشريعية لمغريبية د 2021"
    title = PARAMS['GLOBAL_IGNORE_LIST'][0]
    print(title)
    site = pywikibot.Site('ary','wikipedia')
    page = pywikibot.Page(site,title)
    print(getItemPropertyValue(page,"P17"))
    print(validate_page(page,0,"article",16,"GCLAV"))


