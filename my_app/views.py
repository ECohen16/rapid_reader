from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import get_object_or_404
from my_app.models import Article, Text, Reader, ArticleSource
import urllib.request as ul #url.request lib for handling the url
from bs4 import BeautifulSoup #bs for parsing the page
from bs4.diagnose import diagnose
import requests
from datetime import datetime as dt

#returns the text for a single NYT article based on the article's url
def ny_times_get_text(url):
    p = requests.get(url).content
    soup = BeautifulSoup(p)
    paragraphs = soup.select("p.story-body-text.story-content")
    text = str()
    for paragraph in paragraphs:
        text += paragraph.text
    #text=text.encode('ascii', 'ignore')
    return str(text)

#creates list of articles from front page of NYT
def ny_times_front_scrape():
    nytimes = 'http://www.nytimes.com/'
    url_response=ul.urlopen(nytimes,timeout=5)
    soup = BeautifulSoup(url_response)
    stories = soup.find_all(class_='story-heading')

    #Stores the article tiles and urls in a list of tuples
    #Save all the articles on the first page
    front_page = list()
    for s in range(0,len(stories)):
        links = stories[s].find_all('a')
        for a in range(0,len(links)):
            try:
                url = links[a].get('href')
                title = links[a].get_text()
                new_title = str()
                if title:
                    for character in title:
                        if 48 <= ord(character) <= 57 or 65 <= ord(character) <= 90 or 97 <= ord(character) <= 122:
                            new_title = new_title + character
                        else:
                            new_title = new_title + '_'
                else:
                    continue
                #Store articles in list
                front_page.append((url,new_title))
            except:
                continue

    article_content = list()
    for i in range(0,12):
        try:
            full_text = ny_times_get_text(front_page[i][0])
            if len(full_text) >0:
                #url, title, full_text
                article_content.append((front_page[i][0], front_page[i][1], full_text))
            else:
                continue
        except:
            continue
    return article_content

def home(request):
    #collect article tuples from front page of NYT
    raw_article_list = ny_times_front_scrape()
    article_list = list()
    article_times = list()
    reading_levels = list()
    #create and save Article objects from informal list of tuples
    for article in raw_article_list:
        try:
            #add article object to the new list
            new = Article(name=article[1],short_source="New York Times",url_address = article[0],date_added = dt.now())
            article_list.append(new)
            try:
                #test to see if this particle Article object has already been stored in the database
                Article.objects.all().get(name = article[1])
            except:
                #if it's not there yet, save it to the database and create an associated Text object
                new.save()
                new.text_set.create(article_identifier = new, article_text = article[2])
                text = Text.objects.get(article_identifier = new).article_text
                reading_time = time_calc(text,500)
                grade_level = reading_level(text)
                article_times.append(reading_time)
                reading_levels.append(grade_level)
            else:
                #if it's already there, don't recreate it
                article2 = Article.objects.all().get(name = article[1])
                text = Text.objects.get(article_identifier = article2).article_text
                reading_time = time_calc(text,500)
                grade_level = reading_level(text)
                article_times.append(reading_time)
                reading_levels.append(grade_level)
        except:
            continue
    context = dict()
    context['article_list'] = article_list #list of article objects for "recommended articles"
    context['source_list'] = ArticleSource.objects.all() #list of sources for dropdown menu in search
    context['article_times'] = article_times
    context['reading_levels'] = reading_levels
    return render(request,'home.html',context)

def loggedIn(request):
    context = dict()
    the_user = request.user
    try:
        reader = Reader.objects.get(user=the_user)
    except:
        reader = None
    context['reader'] = reader
    context['source_list'] = ArticleSource.objects.all() #list of sources for dropdown menu in search
    return render(request,'loggedIn.html',context)


#takes string from scraped webpage and cleans a particular common error:
#sometimes the end of a sentence is not followed by a space:
#e.g., "This is the end of a sentence.This is the beginning of another.
def clean_messy_string(argument):
    list_argument = argument.split()
    new_list = list()
    for item in list_argument:
        if item.find('.') == -1:
            new_list.append(item)
        else:
            if item.find('.') == len(item) -1:
                new_list.append(item)
            else:
                temp_string = item.split('.')
                new_list.append(temp_string[0]+'.')
                new_list.append(temp_string[1])
    new_string = str()
    for word in range(0,len(new_list)):
        if word < len(new_list) - 1:
            new_string = new_string + new_list[word] + ' '
        else:
            new_string = new_string + new_list[word]
    return(new_string)

def readerPage(request, article_id):
    article = get_object_or_404(Article, name = article_id) #retrieve article with name passed to URL
    text = Text.objects.get(article_identifier = article).article_text #put the text of that article into a string
    clean_text = clean_messy_string(text) #clean the scraped text with function above
    context = dict()
    context['text'] = clean_text
    return render(request, 'readerPage.html', context)

from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
def register(request):
    context = dict()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/login")
    else:
        form = UserCreationForm()
    context['form'] = form
    return render(request, "registration/register.html", context)

#Execute the api search
def nyt_search_api(keywords, key='c5cfb480e2ef2dccb5fd5bf8bfa32de3:7:72454473'):
    import json
    import requests

    #Get rid of blank spaces
    keywords = keywords.replace(' ','+')

    try:
        url = 'http://api.nytimes.com/svc/search/v2/articlesearch.json?q='+keywords+'&api-key='+key
        r = requests.get(url)
        return r.json()['response']['docs']
    except:
        return 'No results'

#Pull article text and return as results tuple
def pull_search_content(keywords,source,no_results):
    article_content = list()
    #check if it's NYT
    if source == 'New York Times':
        article_results = nyt_search_api(keywords)
        for i in range(0,no_results):
            try:
                url = article_results[i]['web_url']
                title = article_results[i]['headline']['main']
                full_text = ny_times_get_text(url)
                new_title = str()
                if title:
                    for character in title:
                        if 48 <= ord(character) <= 57 or 65 <= ord(character) <= 90 or 97 <= ord(character) <= 122:
                            new_title = new_title + character
                        else:
                            new_title = new_title + '_'
                else:
                    continue
                if full_text:
                    article_content.append((url,new_title,full_text))
            except:
                continue
        return article_content
    #check if it's The Guardian
    elif source == 'The Guardian':
        article_results = guardian_search_api(keywords)
        for i in range(0,no_results):
            try:
                url = article_results[i][0]
                title = article_results[i][1]
                full_text = article_results[i][2]
                new_title = str()
                if title:
                    for character in title:
                        if 48 <= ord(character) <= 57 or 65 <= ord(character) <= 90 or 97 <= ord(character) <= 122:
                            new_title = new_title + character
                        else:
                            new_title = new_title + '_'
                else:
                    continue
                if full_text:
                    article_content.append((url,new_title,full_text))
            except:
                continue
        return article_content
    else:
        pass

#calculates the estimated reading time of an article
def time_calc(text,speed):
    text = clean_messy_string(text)
    text_list = text.split()
    word_count = len(text_list)
    pace1 = word_count//speed
    pace2 = int((word_count/speed - pace1)*60)
    if pace2 < 10:
        pace2 = '0'+str(pace2)
    else:
        pace2 = str(pace2)
    return(str(pace1)+':'+pace2)

#Calculates the estimated grade-reading level using the Flesch�Kincaid grade level algo and NLTK
#1. Fix the periods
#2. Count the sentences
#3. Count the words
#4. Count the syllables



def vowel_check(char):
    vowel_str = 'aeiouyAEIOUY'
    return char in vowel_str


def syllable_count(word):
    import re
    """Uses an ad-hoc approach for counting syllables in a word"""
    # Count the vowels in the word
    # Subtract one vowel from every dipthong
    count = len(re.findall(r'([aeiouyAEIOUY]+)', word))
    # Subtract any silent vowels
    if len(word) > 2:
        try:
            if word[-1] == 'e' and not vowel_check(word[-2]) and vowel_check(word[-3]):
                count = count - 1
        except:
            pass
    return count

def reading_level(full_text):
    #Clean the full_text
    full_text_clean = ""
    for char in full_text:
        if char == ".":
            full_text_clean += ". "
        else:
            full_text_clean += char

    #Language features
    import nltk
    words = nltk.word_tokenize(full_text_clean)

    n_sents = len(nltk.sent_tokenize(full_text_clean))
    n_words = len(nltk.word_tokenize(full_text_clean))

    #Count the syllables
    n_syll = 0
    for word in words:
        n_syll += syllable_count(word)

    #Calculate the reading level
    #https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests

    grade_level = -15.59 + 0.39*(n_words/n_sents) + 11.8*(n_syll/n_words)
    return round(grade_level,1)


def resultsPage(request,search_id):
    search_terms = request.GET.get('text_field')
    source_used = str()
    if request.GET.get('Article_Search') == 'The':
        source_used = 'The Guardian'
    elif request.GET.get('Article_Search') == 'New':
        source_used = 'New York Times'
    raw_matched_articles = pull_search_content(search_terms,source_used,10) #pick out those that match the user's search terms
    matched_articles = list()
    article_times = list()
    reading_levels = list()
    for article in raw_matched_articles:
        try:
            Article.objects.all().get(name = article[1]) #see if the article is already save to the database
        except:
            #if it isn't, add it along with an associated Text object
            new = Article(name=article[1],short_source=source_used,url_address = article[0],date_added = dt.now())
            new.save()
            new.text_set.create(article_identifier = new, article_text = article[2])
            #calculate the reading time for each article
            text = Text.objects.get(article_identifier = new).article_text
            reading_time = time_calc(text,500)
            grade_level = reading_level(text)
            matched_articles.append(new)
            article_times.append(reading_time)
            reading_levels.append(grade_level)
        else:
            # if it is, just add it to the list
            article2 = Article.objects.all().get(name = article[1])
            text = Text.objects.get(article_identifier = article2).article_text
            reading_time = time_calc(text,500)
            grade_level = reading_level(text)
            matched_articles.append(Article.objects.all().get(name = article[1]))
            article_times.append(reading_time)
            reading_levels.append(grade_level)
    context = dict()
    context['matched_articles'] = matched_articles
    context['article_times'] = article_times
    context['reading_levels'] = reading_levels
    context['source_list'] = ArticleSource.objects.all() #list of sources for dropdown menu in search
    return render(request, 'resultsPage.html', context)

from html.parser import HTMLParser
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def guardian_search_api(keywords):
    api_url = 'http://content.guardianapis.com/search'
    payload = {
        'api-key': 'h5hf6xj9f42zxerd9khtvazu',
        'type': 'article',
        'show-fields': 'all',
        'page-size': 10,
        'q': keywords

    }
    response = requests.get(api_url, params=payload)
    data = response.json() # convert json to python-readable format
    data_list = data['response']['results']
    results = list()
    for article in range(0,len(data_list)):
        url = data_list[article]['webUrl']
        name = data_list[article]['fields']['headline']
        text = strip_tags(data_list[article]['fields']['body'])
        results.append((url,name,text))
    return results