import pywikibot, traceback

DEFAULT_SAVE_TO_LOG = ""

def AryPage(pywikibot.Page):
    def __init__(self,site,title):
        super().__init__(site,title)

    def get_final_target(self):
        pass

    
#Abstract class
class Loggable():
    def __init__(self,name,wikilog,local_log,github):
        self.name           = name         #string
        self.wikilogs       = wikilogs        #dictionary
        self.local_log      = local_log       #string
        self.github         = github          #string

    def __str__(self):
        return ""


    def __repr__(self):
        return ""

    def get_page(self,site):
        return pywikibot.Page(site,'User:'+self.name)

    def write_to_wikilog(self,site,message):
        wikilog_page = pywikibot.Page(site,self.wikilog)
        try:
            wikilog_page.text+='\n'+message
            wikilog_page.text.strip()
            wikilog_page.save(DEFAULT_SAVE_TO_LOG)
        except:
            with open(self.local_log,"w",encoding="utf-8") as log:
                log.write("\nCould not write message to wikilog\n")
                log.write("Message: "+message+"\n")
                log.write(traceback.format_exc())

class ArywikiBot(Loggable):
    def __init__(self,name,wikilog,local_log,github):
        super().__init__(name,wikilog,local_log,github)


    def __str__(self): #redefine
        return ""


    def __repr__(self): #redefine
        return ""



class Bottask():
    def __init__(self,name,wikilog,local_log,github,bot,tasknumber,script_path):
        super().__init__(name,wikilog,local_log,github)
        self.bot             = bot #should I keep this? Yes
        self.tasknumber      = tasknumber
        self.script_path     = script_path


    def __str__(self):
        return ""


    def __repr__(self):
        return "" 
    

class Subtask(Bottask):
    def __init__(self,bot,taskname,tasknumber,task_page_title,wikilog,local_log,github,script_path,supertask):
        super().__init__(bot,taskname,tasknumber,task_page_title,wikilog,local_log,github,script_path)
        self.supertask = supertask

class Run():
    def __init__(self,run_id,task,params):
        self.run_id = run_id
        self.task   = task
        self.params = params

class Trigger():
    def __init__(self,ttype,threshold):
        self.ttype       = ttype
        self.threshold   = threshold

    def is_on(self,value):
        """
        For numeric triggers, probably all of them
        can be converted to numeric
        """
        return value >= self.threshold

