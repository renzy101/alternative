from bs4 import BeautifulSoup
import requests
import lxml


def matching_words(string_1, string_2):
    count = 0
    string_1 = string_1.split()

    for word in string_1:
        if word in string_2:
            count += 1
    return count

def good_match(string, num_matching_words):
    string = string.split()
    str_len = len(string)
    if str_len > 0:
        percent =(float(num_matching_words)*100/float(str_len))
        if percent >= 50:
            return True
    return False

def get_data(url):
    try:
        result = requests.get(url)
        soup = BeautifulSoup(result.text, "lxml")
        images = []
        itemTitle = ""
        title = soup.title.string
        for i in soup.find_all("img", alt=True):
            alt = i['alt']
            src = i['src']
            c = matching_words(title,alt)
            if good_match(alt, c):
                #print 'alt: {} \nsrc: {} \ntitle: {} \nmatching: {}'.format(alt, src, title, c)
                if src not in images and src[-4:]==".jpg" and "sprite" not in src:
                    #print 'alt: {} \nsrc: {} \ntitle: {} \nmatching: {}'.format(alt, src, title, c)
                    images.append(src)
                if not itemTitle:
                    itemTitle = title
        if not images:
            for img in soup.findAll("img", src=True):
                src= img['src']
                if "sprite" not in img["src"] and src[-4:]==".jpg":
                    images.append(img["src"])
    except requests.exceptions.RequestException as e:
        return {}

    return {"title": itemTitle, "images": images}
