#!/usr/bin/python
'''
Importing The required Modules
'''
import wx, sys, requests, urllib2, re, os, Queue
from bs4 import BeautifulSoup
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
import threading, time
import  cStringIO
import wx.html
from wx.lib.pubsub import Publisher 

'''
Global variables declaration
'''
proxy = None

########################################################################################################################################################################
class Holder():
  def __init__(self):
    self.anime_list ={}
    self.episode_list={}
    self.glist_chk = 0
    self.gelist_chk= 0
    self.BitMapImage=0
    self.dlist = []
    self.html_code= "Sorry Broken link"
    self.q = Queue.PriorityQueue(1)
  def resetflags(self):
    '''
    Resets the flags used by 
    '''
    self.glist_chk=0
    self.gelist_chk=0
  
  def resetSum(self):
    '''
    Resets the image and summary variable
    '''
    self.BitMapImage=0
    self.html_code= "Sorry Broken link"
  
  def resetalist(self):
    self.anime_list={}
  
  def resetelist(self):
    self.episode_list ={}
  
  def resetIm(self):
    self.BitMapImage=0
  
  def resetdlist(self):
    self.dlist=[]
  
def check():
     try:
          r = requests.head("http://www.animerush.tv/",proxies = proxy)
          dialog = wx.ProgressDialog("Loading List", "Please wait...", maximum = 3000,style=wx.PD_SMOOTH)
          print "[+] Test 1 Connection Established Success:"
          start(load_anime_list)
          progressLdisplay(dialog)
     except requests.exceptions.ConnectionError:
          g = wx.MessageBox("[+] Check Internet Connection !", "Error", wx.OK|wx.ICON_ERROR)  
          pass

def progressLdisplay(dialog):
  count = 0
  while not container.glist_chk:
    if count<1000:
      count = count + 1
    elif count >=2500:
      count +=0.001
    else:
      count = count + 0.01
    dialog.Update(count)
    wx.Sleep(0.01)
  container.resetflags()
  dialog.Destroy()

  
def progressELdisplay(dialog):
  count = 0
  while not container.gelist_chk:
    if count<500:
      count = count + 1
    elif count>750:
      count += 0.001
    else:
      count = count + 0.01
    dialog.Update(count)
    wx.Sleep(0.01)
  container.resetflags()
  dialog.Destroy()  
  
def load_anime_list():
      container.resetalist()
      container.resetflags()
      if not container.anime_list:
          count = 0
	  print ("[+] Loading the list...")
          page = requests.get("http://www.animerush.tv/anime-series-list/",proxies = proxy)
          anime = set(re.findall("http://www.animerush.tv/anime/[^/]*/",page.content))
          anime = list(anime)
          for j in anime:
	    temp = j
	    temp = temp.split("/")[-2]
	    d = temp.replace("-"," ").lower()
	    container.anime_list[d]=j
	  print ("[+] Test 2 Success the list is Downloaded!")
	  container.glist_chk = 1

def load_episode_list(check_url,listctrlobj):
      container.resetelist()
      container.resetSum()
      container.resetflags()
      r = requests.get(check_url,proxies=None)
      b = BeautifulSoup(r.content)
      container.html_code = (b.find_all('div',attrs={'align':'justify'})[0].text)
      s = b.find_all('div',attrs={'class':'episode_list'})
      episode = BeautifulSoup(str(s))
      epi = episode.find_all("a",attrs={'href':True})
      temp = re.findall('http://www.animerush.tv/[^/]*/[^/]*jpg',r.content)[-1]
      temp = requests.get(temp).content
      container.BitMapImage= cStringIO.StringIO(temp)
      
      
      for i in reversed(epi):
        if "Coming soon" not in str(i):
          temp=i['href'].split("/")[-2].replace("-"," ").title()
          epi_no = i['href'].split('-')[-1].replace("/","")
          index = listctrlobj.InsertStringItem(sys.maxint,str(epi_no))
          listctrlobj.SetStringItem(index,1,temp)
          container.episode_list[index] = (temp,i['href'])
      container.gelist_chk=1
      
#########################################################################################################################################################################

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)

#########################################################################################################################################################################

class Load_Episode_Frame(wx.Frame):
     def __init__(self, parent, id, title):
          style = (wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX |wx.CLIP_CHILDREN | wx.FRAME_FLOAT_ON_PARENT)
          wx.Frame.__init__(self, parent, id, title, size=(700,600),style=style)
          panel = wx.Panel(self,-1)
          sizer = wx.GridBagSizer(4,10)
          dialog1 = wx.ProgressDialog("Loading Episodes", "Please wait....", maximum = 1000,style=wx.PD_SMOOTH)
          self.episode_listbox = CheckListCtrl(panel)
          self.episode_listbox.InsertColumn(0, "#", width=75)
          self.episode_listbox.InsertColumn(1, "Episode Name")
          sizer.Add(self.episode_listbox, (0,16),(22,4), wx.EXPAND|wx.RIGHT|wx.TOP, 12)
          self.checkall = wx.Button(panel, -1, "Check All")
          sizer.Add(self.checkall, (23,16), (1,1), wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.TOP, 12)
          self.Bind(wx.EVT_BUTTON, self.OnCheckAll, id=self.checkall.GetId())
          self.uncheckall = wx.Button(panel, -1, "Uncheck All")
          sizer.Add(self.uncheckall, (23,17), (1,1), wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.TOP, 12)
          self.Bind(wx.EVT_BUTTON, self.OnUncheckAll, id=self.uncheckall.GetId())
          self.download = wx.Button(panel, -1, "Download")
          sizer.Add(self.download, (23,18), (1,1), wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.TOP, 12)
          self.Bind(wx.EVT_BUTTON, self.OnDownload, id=self.download.GetId())
          self.episode_listbox.DeleteAllItems()
          container.resetelist()
          check_url = container.anime_list[first.anime_listbox.GetStringSelection().lower()]
          checking_url = "animerush"
          if checking_url in check_url:
             flag = True
             start(load_episode_list,check_url,self.episode_listbox,)
             progressELdisplay(dialog1)
          if container.BitMapImage:
             BMI=container.BitMapImage
             
             image = wx.BitmapFromImage(wx.ImageFromStream(BMI))
             image = wx.ImageFromBitmap(image)
             image = image.Scale(240,320, wx.IMAGE_QUALITY_HIGH)
             image = wx.BitmapFromImage(image)
             wx.StaticBitmap(panel,-1,image,(5,5))
          htmlwin=wx.html.HtmlWindow(panel,-1,pos=(10,340), size=(240,240))
          htmlwin.SetPage(container.html_code)
          
          #sizer.Add(self.static_image,(2,2),(11,8))
          self.Bind(wx.EVT_CLOSE, self.on_close)
          self.Centre()
          panel.SetSizer(sizer)

     def on_close(self, event):
             self.MakeModal(False)
             event.Skip()

     def OnCheckAll(self, event):
          num = self.episode_listbox.GetItemCount()
          for i in range(num):
               self.episode_listbox.CheckItem(i)

     def OnUncheckAll(self, event):
          num = self.episode_listbox.GetItemCount()
          for i in range(num):
               self.episode_listbox.CheckItem(i, False)

     def OnDownload(self, event):
          num = self.episode_listbox.GetItemCount()
          cnt = 0
          for i in range(num):
             if self.episode_listbox.IsChecked(i):
                index1 = first.progresstable.InsertStringItem(sys.maxint, str(container.episode_list[i][0]))
                first.progresstable.SetStringItem(index1, 1, '--')
                first.progresstable.SetStringItem(index1, 2, "--")
                first.progresstable.SetStringItem(index1, 3, 'Queued')
                container.dlist.append([index1,str(container.episode_list[i][0]),str(container.episode_list[i][1])])
                cnt +=1
          if cnt:
	   container.dlist
	   print str(first.anime_listbox.GetStringSelection())
           #p = threading.Thread(target=producer, args=(container.dlist,container.q))
           p = threading.Thread(target=producer,args=(container.q,first.anime_listbox.GetStringSelection()))
           p.start()
                
          print "Test-3 Success the number of items selected:"
          self.Close()

#def producer(dlinklist,index_epi, q, animename, down_link, listbox_selection):

def producer(q,animename):
   for uniq in range(len(container.dlist)): 
     while True:
          if q.full():
               time.sleep(2)
               continue
          else:
               thread = MyThread(container.dlist[uniq][0],container.dlist[uniq][1],container.dlist[uniq][2],animename,q)
               thread.setDaemon(True)
               thread.start()
               q.put(thread, True)
               break
   q.join()  
#######################################################################################################################################################################
class MyThread(threading.Thread):
    def __init__(self, index_epi, path, down_link, animename, q,proxy=None):
        threading.Thread.__init__(self)
        self.ind = index_epi
        self.path = path
        self.url = down_link
        self.animename = animename
        self.durl = ''
        self.q = q
        self.resume=False
        self.proxy = proxy
        
    def mirror_gen(self):
        mirrorlist=[]
        url = requests.get(self.url)
        bs  = BeautifulSoup(url.content)
        res = bs.find_all('div',attrs={'id':'episodes'})
        res = BeautifulSoup(str(res))
        res = res.find_all('a',attrs={'href':True})
        for i in range(1,len(res),2):
	   mirrorlist.append(res[i])
        return mirrorlist
    
    def link_gen(self):  
      res = self.mirror_gen()
      print "Links found:"+str(len(res))
      for i in res:
        url = requests.get(i['href'])
        bs  = BeautifulSoup(url.content)
        bs  = bs.find_all('iframe')
        for i in bs:
          temp = i['src']
          if ('videoweed' in temp) or ('uploadc' in temp)  or ('daily' in temp) or ('novamov' in temp) or ('facebook' in temp) or ('yucache' in temp) or ('sock' in temp): 
            pass
          else:
	   temp = self.link_selector(temp)
           if temp:
	     self.durl = temp
        if self.durl:
          print "[+]Test-4 Successfully Completed found link of ",self.durl,self
          break
      if  not self.durl:
	  print "No link found"
          
    def link_selector(self,temp):
      
      if re.search('auengine',temp):
            try:
	      new_r = requests.get(temp)
              j = re.findall("http://s[^']*",new_r.content)
              for i in j:
		if 'mp4' in i:
		   down_link = urllib2.unquote(i)
              self.resume = True
              return down_link
            except:
	      self.log(temp)
              return None
                 
      elif re.search('mp4upload',temp):
            try:
             new_r = requests.get(temp)
             j = re.findall("file': '[^']*",new_r.content)[0].split("'")[-1]
             down_link = urllib2.unquote(j)
             self.resume = True
             return down_link
            except Exception as e:
	     print e
	     self.log(temp)
             return None
 
            
         
      elif re.search('youru',temp):
            try: 
             new_r = requests.get(temp)
             j = re.findall('http://stream.vi[^"]*',new_r.content)
             if not j:
              j=re.findall('http://stream[^"]*',new_r.content)
             down_link = j[0]  
	     self.resume = True
             return down_link
            except:
	      self.log(temp)
              return None
      
      elif re.search('drive',temp):
            try: 
             new_r = requests.get(temp)
             j=re.findall('file: "[^"]*',new_r.content)
             down_link = j[0].split('"')[-1]
             self.resume = True
             return down_link
            except:
	      self.log(temp)
              return None
      
      elif re.search('videofun',temp):
            try:
             new_r = requests.get(temp)
             j = re.findall('url:.*',new_r.content)
             down_link = j[-1].split('"')[1]
             down_link = urllib2.unquote(down_link)
             self.resume = True
             return down_link
            except:
             self.log(temp)
             return None
      
      
      
      elif re.search('video44',temp):
            try:
             new_r = requests.get(temp)
             j=re.findall("http[^']*mp4",new_r.content)
             down_link = j[0]
             down_link = urllib2.unquote(down_link)
             self.resume = False
             return down_link
            
            except Exception as e:
	     self.log(temp)
             return None
      
      elif re.search('play44',temp):
            try:
             new_r = requests.get(temp)
             j = re.findall("url: 'http://g.*",new_r.content)
             down_link = j[0].split("'")[1]
             down_link = urllib2.unquote(down_link)
             self.resume = True
             return down_link
            except:
             self.log(temp)
             return None
         
    def log(self,temp):
         f = open('log.txt','a')
         f.writelines(str(temp)+'\n')
         f.close()
    
    def startdownload(self,path,down_link):
	cursize=0        
	print "[!] Downloading!"
	down_res = requests.get(down_link,stream=True,proxies=self.proxy)
        total_size = int(down_res.headers['content-length'])
        with open(path,"a+b") as myfile:
             for buf in down_res.iter_content(chunk_size=512):
                 myfile.write(buf)
		 myfile.flush()
                 cursize+=512
                 wx.CallAfter(Publisher.sendMessage,'update percentage',[self.ind,total_size,cursize])
             myfile.close
        if os.path.getsize(path)>=total_size:
                 wx.CallAfter(Publisher.sendMessage,'update status',[self.ind,1]) 
    def dequeue(self):
      self.q.get()
      
    def resumedownload(self,path,down_link):
        print "[!] Resuming Download!"
        file_size = os.path.getsize(path)
        cursize =file_size
	headers = {'Range':'bytes=%s-' % (file_size)}
        r = requests.Request('HEAD', down_link)
        r.headers = headers
        req = r.prepare()
        try: 
           down_res = requests.get(req.url,headers=req.headers,stream=True,proxies=self.proxy)
           total_size = int(down_res.headers['content-length'])
           total = requests.head(down_link)
           with open(path,"a+b") as myfile:
	       for buf in down_res.iter_content(chunk_size=512):
                   myfile.write(buf)
                   myfile.flush()
                   cursize+=512
		   wx.CallAfter(Publisher.sendMessage,'update percentage',[self.ind,(total_size+file_size),cursize])
               myfile.close
           if os.path.getsize(path)>=total_size:
                 wx.CallAfter(Publisher.sendMessage,'update status',[self.ind,1])    
        except Exception as e:
	   print e
           wx.CallAfter(Publisher.sendMessage,'update status',[self.ind,3])
    
    def run(self):
        self.link_gen()
        down_link = self.durl
        if not down_link:
           wx.CallAfter(Publisher.sendMessage,'update status',[self.ind,2])
           self.dequeue()
        ext = requests.get(down_link,stream=True)
	first.progresstable.SetStringItem(self.ind, 1, str(int(ext.headers['content-length'])/(1024*1024)) + " MB")
        ext = ext.headers['content-type'].split('/')[-1].split('-')[-1]
        if ext == 'stream':
	   ext ='mp4'
        if not os.path.isdir(self.animename):
           os.makedirs(self.animename)
        path = self.animename+'/'+self.path + '.' + ext
        file_present = os.path.isfile(path)
        if file_present and self.resume == True:
            wx.CallAfter(Publisher.sendMessage,'update status',[self.ind,4]) 
	    self.resumedownload(path,down_link)   
        elif file_present and self.resume == False:
            os.remove(path)
	    wx.CallAfter(Publisher.sendMessage,'update status',[self.ind,4])
	    self.startdownload(path,down_link)            
        else:
            wx.CallAfter(Publisher.sendMessage,'update status',[self.ind,4])     
            self.startdownload(path,down_link)
        self.dequeue()

        
#######################################################################################################################################################################        
class MainFrame(wx.Frame):
    def __init__(self, parent, id, title):
        style = (wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX |
                 wx.CLIP_CHILDREN)
        wx.Frame.__init__(self, parent, id, title, size = (910,655), style=style)
        Publisher.subscribe(self.update_percent, "update percentage")
        Publisher.subscribe(self.update_status , "update status")
        self.init_gui()
	self.dir=None
    def init_toolbar(self):
	toolbar = self.CreateToolBar()
	toolbar.AddSeparator()	
	#toolbar.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENUBAR))
        directory = toolbar.AddLabelTool(wx.ID_ANY, 'Directory', wx.Bitmap('icons/directory.png'))
        toolbar.AddSeparator()
	play = toolbar.AddLabelTool(wx.ID_ANY,'Start Downloads',wx.Bitmap('icons/play.png'))
	toolbar.AddSeparator()	
	stop = toolbar.AddLabelTool(wx.ID_ANY,'Stop Downloads',wx.Bitmap('icons/pause.png'))
	toolbar.AddSeparator()	
	proxy = toolbar.AddLabelTool(wx.ID_ANY,'Proxy',wx.Bitmap('icons/proxy.png'))
	toolbar.AddSeparator()	
	queue = toolbar.AddLabelTool(wx.ID_ANY,'Queue length',wx.Bitmap('icons/queue.png'))
	toolbar.AddSeparator()	
	about = toolbar.AddLabelTool(wx.ID_ANY,'About',wx.Bitmap('icons/about.png'))
	toolbar.Realize()
        self.Bind(wx.EVT_TOOL, self.OnDirectory,directory)
	self.Bind(wx.EVT_TOOL, self.OnStart,play)
	self.Bind(wx.EVT_TOOL, self.OnStop,stop)
	self.Bind(wx.EVT_TOOL, self.OnProxy,proxy)
	self.Bind(wx.EVT_TOOL, self.OnQueue,queue)
	self.Bind(wx.EVT_TOOL, self.OnAbout,about)
	
    
    def init_gui(self):
        panel = wx.Panel(self,-1)
	self.init_toolbar()        
	sizer = wx.GridBagSizer(4,10)
        
        self.anime_searchbox = wx.TextCtrl(panel, -1, "", style=wx.TE_PROCESS_ENTER)
        sizer.Add(self.anime_searchbox, (0,0), (1,8), wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 10)
        self.button1 = wx.Button(panel,-1,"search")
        self.Bind(wx.EVT_BUTTON, self.OnSearch, id=self.button1.GetId())
        self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch)
        sizer.Add(self.button1,(0,8),(1,1), wx.TOP,10)
        self.anime_listbox = wx.ListBox(panel, -1, choices=[])
        sizer.Add(self.anime_listbox, (1,0), (22,10), wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        self.load_episodes = wx.Button(panel, -1, "Load Episodes")
        sizer.Add(self.load_episodes, (23,5), (1,1), wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.TOP, 12)
        self.Bind(wx.EVT_BUTTON, self.OnLoadEpisodes, id=self.load_episodes.GetId())
        self.progresstable = wx.ListCtrl(panel, style = wx.LC_REPORT | wx.LC_HRULES |wx.LC_VRULES)
        self.progresstable.InsertColumn(0, "Name", width=235)
        self.progresstable.InsertColumn(1, "Size",wx.LIST_FORMAT_CENTRE, width=70)
        self.progresstable.InsertColumn(2, "Completion",wx.LIST_FORMAT_CENTRE, width=95)
        self.progresstable.InsertColumn(3,"Status ",width=100)
        sizer.Add(self.progresstable, (0, 10), (23,27), wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 12)
        panel.SetSizer(sizer)
        self.Centre()
        self.Show()
    
    def OnSearch(self, event):
       if container.anime_list: 
        self.anime_listbox.Clear()
        animename = self.anime_searchbox.GetValue().lower()
        print ("[!] Checking for similar names!")
        r = [] 
        for near_names in container.anime_list:        
            if near_names.startswith(animename[0:4]) or near_names.endswith(animename[-4:]):
                r.append(near_names)
        if r:  
            for i in r:
                self.anime_listbox.Append(i.title())
    def OnDirectory(self,e):
	if not self.dir:	
		self.dir = wx.DirDialog(self, message='Select Download Directory', defaultPath='./', style=wx.DD_NEW_DIR_BUTTON,pos=wx.DefaultPosition,size=(200,200), name='Download Directory Selection')      
		self.dir.ShowModal()
		print self.dir.GetPath() 
		print self.dir.GetMessage()		
		self.dir=None
    def OnStart(self,e):
        pass
    def OnStop(self,e):
        pass
    def OnProxy(self,e):
        pass
    def OnQueue(self,e):
        pass
    def OnAbout(self,e):
        description = """Acnologia Download Manager is a Data scraping,Mutithreaded download manager where you can search for the anime and see a synopsis of the title  download  most of the links are of of resume capabilities and all the credits go to the streaming sites hence any kindness you people want to bestow upon us must go as donation to the streaming sites from which we data scraped.All the materials presented for download are the propery of the respective copyright owners and we are simply providing an easy way of access.
"""

        licence = """Acknologia Download Manager is free software; you can redistribute 
it and/or modify it under the terms of the GNU General Public License as 
published by the Free Software Foundation; either version 2 of the License, 
or (at your option) any later version.

File Hunter is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the GNU General Public License for more details. You should have 
received a copy of the GNU General Public License along with File Hunter; 
if not, write to the Free Software Foundation, Inc., 59 Temple Place, 
Suite 330, Boston, MA  02111-1307  USA"""


        info = wx.AboutDialogInfo()
	info.SetIcon(wx.Icon('icons/about.png', wx.BITMAP_TYPE_PNG))
        info.SetName('Acnologia Download Manager')
        info.SetVersion('1.0')
        info.SetDescription(description)
        info.SetCopyright('(C) Fucker')
        info.SetWebSite('http://fucker.com')
        info.SetLicence(licence)
        info.AddDeveloper('Quintessence')
	info.AddDeveloper('Sniper')
        info.AddDocWriter('None')
        info.AddArtist('None')
        info.AddTranslator('None')
	wx.AboutBox(info)
    
    def update_percent(self,mesg):
        total_size1 = float(mesg.data[1])
        current_size=float(mesg.data[2])
        up_size = (current_size * 100) / total_size1
        up_size = round(up_size,2)
        
        try:
         self.progresstable.SetStringItem(mesg.data[0],2, str(up_size) + " %")
        except Exception as e:
	  print e
    def update_status(self,mesg):
      if mesg.data[1] == 1:
        self.progresstable.SetStringItem(mesg.data[0],3,'Completed')
      elif mesg.data[1] ==2:
        self.progresstable.SetStringItem(mesg.data[0],3,'No link found')
      elif mesg.data[1] ==3:
	self.progresstable.SetStringItem(mesg.data[0],3,'Link Expired')
      elif mesg.data[1] ==4:
        self.progresstable.SetStringItem(mesg.data[0],3,'Downloading')
    
    def OnLoadEpisodes(self, event):
            if first.anime_listbox.GetStringSelection():
             container.resetelist()
             second = Load_Episode_Frame(self, -1, str(first.anime_listbox.GetStringSelection()))
             second.Show()
             second.MakeModal(True)   
##################################################################################################################################################################################

def start(func, *args): 
    thread = threading.Thread(target=func, args=args)
    thread.setDaemon(True)
    thread.start()

container=Holder()
app = wx.App()
first = MainFrame(None, -1, "Acnologia - Anime Downloader")
check()
app.MainLoop()
