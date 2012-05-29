import urllib2
#import re
#import urlparse


class search:
    
    index ={} # index for the search engine
    graph ={} # graph used by the page ranking algorithm
    rank ={}  # ranking score evaluated by the page ranker

    # initializer
    def __init__(self,seed):
        self.crawl_seed(seed)

    # retrieves the best 3 documents based on page rank
    def retrieve(self,keyword):
        list_of_documents = self.index[keyword]
        n = len(list_of_documents)
        
        for i in range(1,n):
            doc = list_of_documents[i]
            val = self.rank[doc]
            j = i-1
            while j>=0 and self.rank[list_of_documents[j]] < val:
                list_of_documents[j+1] = list_of_documents[j]
                j = j-1
            list_of_documents[j+1] = doc

        return list_of_documents[0:3]

            
    # function which crawls the web given the seed
    def crawl_seed(self,seed):
        toCrawl = [seed]
        crawled = []
        

        while toCrawl and (len(crawled) < 50):
            page = toCrawl.pop(0)
            content = self.get_page(page)

            #print content

            # if the page times out
            if content == "":
#                print 'hi'
                continue

            # index the page
            self.add_page_index(page,content)

            # get all the outgoing links
            outlinks = self.get_all_links(content)

#            print outlinks

            # graph has both the outgoing and incoming links for each node
            if not self.graph.get(page):
                self.graph[page]=[],[]

            for links in outlinks:
                self.graph[page][0].append(links)

            #update for all the incoming links    
            self.update_graph(page,outlinks)

            #update the crawl list
            self.union(outlinks,toCrawl)
            crawled.append(page)

        #compute the rank
        self.rank = self.compute_rank()


    # gets all the links from a page
    def get_all_links(self,content):

        start =0
        result =[]

#        if content == "":
 #           print 'hi'
        while 1:
#            print content[start:]
            content = content[start:]
            url,start = self.gen_next_target(content)

#            if(start == 2478):
 #               print content[start:]

            #print content[start:]
           # print start
            #print url
            if not url:
                break
 #           start = starting
            result.append(url)
        return result

    # used by get links , generates the next link target
    def gen_next_target(self,content):
        start_link = content.find('<a href')

        #print start_link
        #print content[start_link]
        if start_link == -1:
            return None,0

        start_quote = content.find('"',start_link)
        #print content[start_quote:start_quote + 40]
        end_quote = content.find('"',start_quote+1)
        
        #print end_quote
        link = content[start_quote+1:end_quote]

        #print link

       # if(start_link ==2433):
        #    print end_quote
        return link,end_quote

    # updates the incoming link structure of the graph
    def update_graph(self,page,outlinks):

        for link in outlinks:
            if self.graph.get(link):
                self.graph[link][1].append(page)
            else:
                self.graph[link] = [],[]
                self.graph[link][1].append(page)
        
    # computes the page rank for all the pages of the corpus
    def compute_rank(self):

        num_loops = 10 #number of time steps
        prev_rank ={}  #rank of the previous iteration
        damp = 0.8 #dampening fator
        n = len(self.graph) #number of nodes


        # initialize the rank with equi-probability
        for url,links in self.graph.iteritems():
            prev_rank[url] = 1.0/n

        # iterate over a certain number of time steps         
        for i in range(0,num_loops):
            new_rank ={} #rank of the current time step

            # compute the similarity from this time step
            for url,links in self.graph.iteritems():
        
                new_rank[url] = (1.0 - damp)/n # random walk probability
                popularity =0.0

                # obtain the popularity of its neigbours
                for link in links[1]:
                    popularity = popularity + prev_rank[link]/len(self.graph[link][0])
                popularity = damp * popularity
                new_rank[url] = new_rank[url] + popularity

            # replace the previous rank with the current rank value
            for url,val in prev_rank.iteritems():
                prev_rank[url]= new_rank[url]
        return new_rank


    # retrives the contents of a url
    def get_page(self,url):
       print url
       try:
           return urllib2.urlopen(url).read()
       except:
           return ""

    # TODO have to implement a proper indexer
    # builds the index of the search engine
    def add_page_index(self,page,content):

        list_of_words = content.split()
    
        for word in list_of_words:
            #print word
            if self.index.get(word):
                self.index[word].append(page)
            else:
                self.index[word] = []
                self.index[word].append(page)
    

    # gives the union of 2 lists
    def union(self,outlinks,toCrawl):
        for link in outlinks:
            found = 0
            for urls in toCrawl:
               if link == urls:
                   found =1
                   break
            if found ==0:
                toCrawl.append(link)


#test modules
obj = search("http://www.iitm.ac.in")                
a = obj.retrieve("Placements")
print a
