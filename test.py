import pywikibot

title = "زلزال د لحوز 2023"
site = pywikibot.Site("ary", "wikipedia")
page = pywikibot.Page(site, title)
item = pywikibot.ItemPage.fromPage(page)
#item_dict = item.get()

print(item.getID())
