#! python3
# imdb_handling.py : A module containing tools to interact with and retrieve movie infromation from  https://www.IMDB.com

import re, textwrap, sys
import requests, bs4 # Third-Party Modules

MONTHS = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12
}


def main():
    link = search_imdb(get_user_input())
    if not link: quit()
    movie_info = imdb_get_all_info(link)
    line_width = 150
    print(movie_info)
    print('\n' + '=' * line_width)
    print (movie_info['title'].ljust(line_width//3) + movie_info['type'].center(line_width//3) + str(movie_info['date']['Y']).rjust(line_width//3))
    print (("IMDB Rating: " + movie_info['rating']).ljust(line_width//4) + movie_info['parental_rating'].center(line_width//4) +
            str(movie_info['genres']).center(line_width//4) + movie_info['runtime'].rjust(line_width//4))
    print('=' * line_width)
    print('Summary:')
    print(textwrap.fill(movie_info['summary'], line_width))


def get_user_input():                   # Returns a string containing user provided movie/tv title
    if len(sys.argv) > 1:               # Checks if title was provided while calling the program
        return " ".join(sys.argv[1:])       # Returns any command line arguments following the program call as a space seperated string
    else:                               # If the tile wasn't given while calling the program, the program prompts the user for input and returns the result
        return input("Enter the title of the movie or show you want to search for: ")


def search_imdb(title, field='Titles', choice='m'):       # Shows search results for given title and returns the link to user's selection
    # Gets the BeautifulSoup object containing the search results page for given title
    search_soup = get_soup('https://www.imdb.com/find?q={}&s=tt'.format('%20'.join(title.split())))
    # Finds and stores all div containers with the class "findSection" on search page. (Titles, Names, Companies, etc.)
    search_results = search_soup.findAll('div', class_="findSection")

    if search_results:
        results_in_field = None
        for search_field in search_results: # Iterates through search_results until the results section matching field is found
            if search_field.h3.text == field: results_in_field = search_field
            if results_in_field: break
        if results_in_field: requested_search_results = results_in_field.findAll('td',class_='result_text')
        if requested_search_results:
            choices = []
            print("{} results were found for {}".format(len(requested_search_results), title))
            while True:
                if len(choices) < len(requested_search_results) and choice[0].lower() == 'm':
                    for i in range(len(choices), (len(requested_search_results) if len(requested_search_results) - (len(choices) + 5) <= 0 else len(choices) + 5)):
                        choices.append('https://www.imdb.com' + requested_search_results[i].find('a', href=True)['href'])
                        print('({}). {}'.format(i + 1, requested_search_results[i].text))
                if len(choice) < len(requested_search_results): choice = input('\nEnter the number coresponding with your choice, (M)ore for more results, or <Enter> to quit: ')
                else: choice = input('\nEnter the number coresponding with your choice, or <Enter> to quit: ')
                if not choice: return None
                elif choice[0].lower() == 'm' and len(choices) == len(requested_search_results): print("No more results.")
                else:
                    try: return choices[int(choice) - 1]
                    except: pass
    else:
        print("No Results Found")
        return None


def get_soup(link, headers={'User-Agent': 'My User Agent 1.0'}):
    page = requests.get(link, headers=headers)
    page.raise_for_status()
    soup = bs4.BeautifulSoup(page.text, 'lxml')
    return soup


def imdb_go_to_page(imdb_tag, page_type):
    if page_type.lower() == 'trivia':
        if imdb_tag[0:2] == 'tt':
            return "https://www.imdb.com/title/{}/trivia".format(imdb_tag)
        elif imdb_tag[0:2] == 'nm':
            return "https://www.imdb.com/name/{}/bio".format(imdb_tag)
    if page_type.lower() == 'trivia':
        if imdb_tag[0:2] == 'tt':
            return "https://www.imdb.com/title/{}/trivia".format(imdb_tag)
        elif imdb_tag[0:2] == 'nm':
            return "https://www.imdb.com/name/{}/bio".format(imdb_tag)


def imdb_get_all_info(link, movie_dict={}):
    imdb_soup = get_soup(link)

    movie_dict['title'] = imdb_get_title(imdb_soup)
    movie_dict['type'] = imdb_get_type(imdb_soup)
    movie_dict['date'] = imdb_get_date(imdb_soup)
    movie_dict['rating'] = imdb_get_rating(imdb_soup)
    movie_dict['parental_rating'] = imdb_get_parental_rating(imdb_soup)
    movie_dict['genres'] = imdb_get_genres(imdb_soup)
    movie_dict['runtime'] = imdb_get_runtime(imdb_soup)
    movie_dict['summary'] = imdb_get_summary(imdb_soup)

    return movie_dict


def imdb_get_title(imdb_soup):
    title = imdb_soup.find('h1', {"data-testid":"hero-title-block__title"})
    print(title.text.strip())
    return None if not title else title.text.strip()


def imdb_get_parental_rating(imdb_soup):
    subtext = imdb_soup.findAll('span', {"class":"jedhex"})
    if len(subtext) < 2:
        return 'None'
    subtext = subtext[1]
    print(subtext.text.strip())
    return 'None' if not subtext else subtext.text.strip()


def convert_date(date):
    date = date.replace(',', '')
    df = date.split(" ")
    return {
        "M": MONTHS[df[0]],
        "D": int(df[1]),
        "Y": int(df[2])
    }


def imdb_get_date(imdb_soup):
    dateRegex = re.compile(r'''(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)\s+\d{1,2},\s+\d{4}''')
    links = imdb_soup.findAll('a', {"class": "ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"})
    for link in links:
        if dateRegex.search(link.text):
            print(convert_date(dateRegex.search(link.text).group()))
            return convert_date(dateRegex.search(link.text).group())
    return None


def imdb_get_genres(imdb_soup):
    genres = []
    texts = imdb_soup.findAll('a', {"class": "LKJMs"})
    for text in texts:
        genres.append(text.text.strip())
    print(genres)
    return None if len(genres) == 0 else genres


def imdb_get_rating(imdb_soup):
    rating_value = imdb_soup.find('span', {"class": "iTLWoV"})
    print(rating_value.text.strip())
    return None if not rating_value else rating_value.text.strip()


def imdb_get_summary(imdb_soup):
    summary_text = imdb_soup.find('span', {"data-testid":"plot-xl"})
    return None if not summary_text else summary_text.text.strip()


def imdb_get_runtime(imdb_soup):
    rtRegex = re.compile(r'''(\d+h )?\d+m''')
    lis = imdb_soup.findAll('li', {"class": "ipc-inline-list__item"})
    for li in lis:
        if rtRegex.search(li.text):
            print(rtRegex.search(li.text).group())
            return rtRegex.search(li.text).group()
    return None


def imdb_get_type(imdb_soup):
    types = ['TV Series', 'TV Mini Series', 'TV Movie', 'TV Short', 'Short', 'Video', 'Movie']
    type = 'Movie'
    lis = imdb_soup.findAll('li', {"class":"ipc-inline-list__item"})
    for li in lis:
        if li.text.strip() in types:
            if type != 'Movie':
                if 'Short' in type and 'Short' in li.text.strip():
                    continue
                type += " " + li.text.strip()
            else:
                type = li.text.strip()
    print(type)
    return type


if __name__ == '__main__':
    main()
