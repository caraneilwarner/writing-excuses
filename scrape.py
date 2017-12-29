# pylint: disable=unused-variable,bare-except
""" Module contains functions for scraping the Writing Excuses website to
produce markdown files for each writing prompt, organized by season.
"""
import os
import re
import requests

from bs4 import BeautifulSoup

SEASONS = range(7,13) # There were no prompts before Season 7
SEASON_URL_FORMAT = 'http://www.writingexcuses.com/category/season/season-%s'

def scrape_all_seasons():
    """Scrape all seasons"""
    for season in SEASONS:
        scrape_season(season)

def scrape_season(season):
    """Scrape season page. Retrieve list of articles. Produce markdown files for
    each article. Also produce an index of the markdown files.
    """
    season_label = str(season)
    season = str(season) if season >= 10 else '0' + str(season)
    season_dir = 'episodes/season-%s' % season
    os.mkdir(season_dir, 0777)

    # Season Index
    index = open('indeces/season-%s.md' % season, 'a')
    index.write('# Writing Excuses Season %s \n\n' % season_label)

    # Checklist for use in Pull Request body
    checklist = open('checklists/season-%s' % season, 'a')
    checklist.write('# Writing Excuses Season %s \n\n' % season_label)

    url = SEASON_URL_FORMAT % season
    soup = BeautifulSoup(requests.get(url).text)

    for article in soup.find_all('article'):
        (title, href, prompt) = extract_article_information(article)
        fname = '%s/%s' % (season_dir, re.sub(r'\W+', '-', title))
        # Fill article markdown file
        md = open(fname, 'w+')
        md.write('# %s \n\n' % title)
        md.write('Listen [here](%s). \n\n' % href)
        md.write('**Prompt:** %s' % prompt)
        md.close()
        # Add article to season index and checklist
        index.write('* [%s](/%s) \n' % (title, fname))
        checklist.write('- [ ] %s \n' % title)

    index.close()


def extract_article_information(article):
    """Extract link, title, href, and writing prompt from BeautifulSoup obj."""
    link = article.find('header').find('a')
    title = re.sub('Writing Excuses ', '', link.get('title').encode('utf-8'))
    href = link.get('href').encode('utf-8')
    try:
        prompt = article.find('div', 'wx_writeprompt').text.encode('utf-8')
    except:
        prompt = 'There was a problem retrieving this prompt.'

    return (title, href, prompt)
