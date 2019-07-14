#! python3
# imdb_handling.py : A module containing tools to interact with and retrieve movie infromation from  https://www.IMDB.com

import re, textwrap, sys
import requests, bs4 # Third-Party Modules

def main():
    link = search_imdb(get_user_input())
    if not link: quit()
    movie_info = imdb_get_all_info(link)
    line_width = 150
    print('\n' + '=' * line_width)
    print (movie_info['title'].ljust(line_width//3) + movie_info['type'].center(line_width//3) +  movie_info['date'].rjust(line_width//3))
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
    title = imdb_soup.find('div', class_='title_wrapper')
    if title:
        title = title.h1
        if title.span: title.span.decompose()
    return None if not title else title.text

def imdb_get_parental_rating(imdb_soup):
    subtext = imdb_soup.find('div', class_='subtext')
    return None if not subtext else subtext.text.split('|')[0].strip()

def imdb_get_date(imdb_soup):
    date_regex = re.compile(r'''\d(\d)? \w* \d{4}''')
    tv_series_date_regex = re.compile(r'''(\(\d{4}–( )?(\d\d\d\d)?\))''')
    info = imdb_soup.find('a', title='See more release dates')
    if info:
        if date_regex.search(info.text):
            return date_regex.search(info.text).group()
        elif tv_series_date_regex.search(info.text):
            return tv_series_date_regex.search(info.text).group()
    return None

def imdb_get_genres(imdb_soup):
    genre_text = imdb_soup.find('div', class_='subtext')
    return None if not genre_text else genre_text.text.split('|')[2].strip().replace(', \n', ' ').split()

def imdb_get_rating(imdb_soup):
    rating_value = imdb_soup.find('span', itemprop='ratingValue')
    return None if not rating_value else rating_value.text.strip()

def imdb_get_summary(imdb_soup):
    summary_text = imdb_soup.find('div', class_='summary_text')
    if summary_text.find('a', href=True):
        full_summary_soup = get_soup('http://www.imdb.com' + summary_text.find('a', href=True)['href'])
        summary_text = full_summary_soup.find('ul', id='plot-summaries-content').li.p
    return None if not summary_text else summary_text.text.strip()

def imdb_get_runtime(imdb_soup):
    runtime_text = imdb_soup.find('time', datetime=True)
    return None if not runtime_text else runtime_text.text.strip()

def imdb_get_type(imdb_soup):
    types = ['TV Series', 'TV Movie', 'Video', 'Short']
    result_info_text = imdb_soup.find('a', title='See more release dates')
    if result_info_text:
        for type in types:
            if type in result_info_text.text: return type
        if 'Episode aired' in result_info_text.text: return 'TV Episode'
        else: return 'Movie'
    return None


if __name__ == '__main__':
    main()
