# -*- coding: utf-8 -*-
"""
Created on Wed Aug  4 13:44:34 2021

@author: kristen
@purpose: Compare items shared to an ArcGIS Hub or Hubs with a previous check to determine
what items have been newly shared. Send an email report.
This script is intended to be run on a regular interval, for example, once a week as a scheduled task.
@requirements: must be run on Python 3 in an environment with the ArcGIS API for Python installed (the arcgis module)
the smtplib is also required for email notification
"""
from arcgis import GIS
from os.path import exists, join
from os import remove


def send_mail(to, SUBJECT, TEXT):
    import smtplib 

    # USER EDIT- enter the "from" address for the email
    FROM = 'me@yahoo.com'  

    if isinstance(to, list):
        TO = to
    else:
        TO = [to] # must be a list

    # Send the mail
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s""" % (FROM, ", ".join(TO), SUBJECT, TEXT)

    # USER EDIT- enter the smtp address for your org
    server = smtplib.SMTP('smtp.stuff.edu')
    server.sendmail(FROM, TO, message)
    server.quit() 


def writeToText(textFile, stuff):
    mode = "w"
    if exists(textFile):
        mode = "a"
    FILE = open(textFile,mode)
    FILE.write(stuff)
    FILE.close()
    
    
def getItemTitleOwner(gis, item_id):
    
    item1 = gis.content.get(item_id)
    
    return [item1.title, item1.owner]


def main():

    # USER EDIT- the list of emails to be informed of the changes
    email_list = ['whoever@gmail.com',"person@uu.edu",'me@yahoo.com']
    
    # USER EDIT- this is the dictionary of Hub/s, the name of their text files, and what you like to call it for reporting
    # set variables
    hub_group_dict = {"d1c57d9bc70541a3a118a52ab579c0ca": ["HubItems.txt", "Kansas Geoportal"],
                    "77b463a9eff546b58079429c91c08c75": ["HubArchiveItems.txt", "Archive Hub"]} # main hub, archive hub
    # USER EDIT- this is where the text docs of the hub item ids will live
    hub_item_folder = r"C:\myfolder"

    # USER EDIT- fill in your admin username & password
    un = ""
    pw = ""
    
    # connect to AGO
    gis = GIS("https://www.arcgis.com", un, pw)
    
    msg = ""
    
    # loop through hubs
    for hub_group_id in hub_group_dict:
        
        # get variables
        info_list = hub_group_dict[hub_group_id]
        txt_name = info_list[0]
        hub_name = info_list[1]
        
        # define text file
        hub_item_txt = join(hub_item_folder, txt_name)
    
        # get list of last week's items
        with open(hub_item_txt) as f:
            lines = f.readlines()
            
        old_item_ids = lines[0].strip().split(",")
        
        # get the hub group
        hub_group = gis.groups.get(hub_group_id)
        
        now_item_ids = []
        
        for item in hub_group.content():
            now_item_ids.append(item.id)
            
        # compare the two lists
        if old_item_ids == now_item_ids:
            msg = "No new items"
            
        else:
            # see what items were unshared
            unshared_ids = set(old_item_ids) - set(now_item_ids)
            
            # see what new items were shared
            shared_ids = set(now_item_ids) - set(old_item_ids)
            
            unsharedTxt = ""
            sharedTxt = ""
            
            if len(unshared_ids) != 0:
                unsharedTxt = "The following items were removed from the %s:\n\r" % hub_name
                
                for u_id in unshared_ids:
                    title, owner = getItemTitleOwner(gis, u_id)
                    unsharedTxt += "%s, %s\n" % (title, owner)
                    
            if len(shared_ids) != 0:
                sharedTxt = "The following items were shared with the %s:\n\r" % hub_name
                
                for s_id in shared_ids:
                    title, owner = getItemTitleOwner(gis, s_id)
                    sharedTxt += "%s, %s\n" % (title, owner)
            
            if unsharedTxt != "":
                msg += unsharedTxt + "\n\r" + sharedTxt
            else:
                msg += sharedTxt + "\n\r"
            
            # rewrite record of group items
            if exists(hub_item_txt):
                remove(hub_item_txt)
            item_ids_str = ",".join(now_item_ids)
            writeToText(hub_item_txt, item_ids_str)
        
    send_mail(email_list, "Weekly Hub Item Report", msg)
        

if __name__ == '__main__':
    main()  
