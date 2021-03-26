from burp import IBurpExtender
from burp import IContextMenuFactory
 
from javax.swing import JMenuItem
from java.util import List, ArrayList
from java.net import URL
 
import socket
import urllib
import json
import re
import base64

from threading import Thread

 
bing_api_key = "cd78b019fc034569afecffee014fbab4"

class MyThread(Thread):
    def __init__(self, func, link, port, flag, http_request):
        Thread.__init__(self)
        self.result = ""
        self.func   = func
        self.link   = link
        self.port   = port
        self.flag   = flag
        self.http_request = http_request

    def run(self):
        self.result = self.func(self.link, self.port, self.flag, self.http_request).tostring()

    def get_result(self):
        return self.result


 
class BurpExtender(IBurpExtender, IContextMenuFactory):

    def registerExtenderCallbacks(self,callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self.context = None
 
        callbacks.setExtensionName("Use Bing")
        callbacks.registerContextMenuFactory(self)
 
        return
 
    def createMenuItems(self, context_menu):
        self.context = context_menu
        menu_list = ArrayList()
        menu_list.add(JMenuItem("Send to Bing", actionPerformed=self.bing_menu))
        return menu_list
 
    def bing_menu(self, event):
        http_traffic = self.context.getSelectedMessages()
 
        print "%d requests highlighted" % len(http_traffic)
 
        for traffic in http_traffic:
            http_service = traffic.getHttpService()
            host = http_service.getHost()
 
            print "User selected host: %s" % host
 
            self.bing_search(host)
 
        return
 
    def bing_search(self, host):
        is_ip = re.match("[0-9]+(?:\.[0-9]+){3}", host)
 
        if is_ip:
            ip_address = host
            domain = False
        else:
            ip_address = socket.gethostbyname(host)
            domain = True
 
        bing_query_string ="'ip:%s'" % ip_address
        self.bing_query(bing_query_string)
		
        if domain:
            bing_query_string = "'domain:%s'" % host
            self.bing_query(bing_query_string)
        print(bing_query_string)
 
 
    def bing_query(self, bing_query_string):
        print "Performing Bing search: %s" % bing_query_string
		
        quoted_query = urllib.quote(bing_query_string)
        print("quoted_query: %s" %quoted_query)
        
 
        #http_request  = "GET https://api.datamarket.azure.com/Bing/Search/Web?$format=json&$top=20&Query=%s HTTP/1.1\r\n" % quoted_query
        http_request  =  "GET /v7.0/search?q=%s HTTP/1.1\r\n" % quoted_query
        http_request +=  "Host: api.bing.microsoft.com\r\n"
        
        #http_request +=  "Connection: close\r\n"
        #http_request += "Authorization: Basic %s\r\n" % base64.b64encode(":%s" % bing_api_key)
        #http_request += "User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36\r\n\r\n"
        
        http_request += "User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0\r\n"
        http_request += "Accept: */*\r\n"
        #http_request += "Ocp-Apim-Subscription-Key: %s\r\n\r\n" %base64.b64encode("%s" % bing_api_key) " 
        http_request += "Ocp-Apim-Subscription-Key: %s\r\n\r\n" %bing_api_key
 
        jsthread  = MyThread(self._callbacks.makeHttpRequest, "api.bing.microsoft.com", 443, True, http_request)
        jsthread.start()
        #jsthread.run()
        jsthread.join()
        json_body = jsthread.get_result()
  
        print("json_body: %s" %json_body)
        json_body = json_body.split("\r\n\r\n", 1)[1]
        #print("json_body: %s" %json_body)
 
        try:
            r = json.loads(json_body)
            print(r)
 
            if len(r["d"]["results"]):
                for site in r["d"]["results"]:
 
                    print "*" * 100
                    print site['Title']
                    print site['Url']
                    print site['Description']
                    print "*" * 100
 
                    j_url = URL(site['Url'])
 
            if not self._callbacks.isInScope(j_url):
                print "Adding to Burp scope"
                self._callbacks.includeInScope(j_url)
 
        except:
            print "No results from Bing"
            pass
 
        return
