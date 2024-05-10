from pathlib import Path
from bs4 import BeautifulSoup
import typing
import pandas as pd
import requests
import json

"""
All functions pertinent to extracting the online data from candidate social links.
"""

# loads data from candidate csv and filters to a particular county
def data_load(file_path: Path, county_filter: str = 'Montgomery County') -> pd.DataFrame:
    candidate_df = pd.read_csv(file_path)
    # create a bool column to help filter the results to only the active candidates
    candidate_df['Active'] = candidate_df['Candidate Status'].apply(lambda stat: False if stat.__contains__('Removed') else True)
    return candidate_df[(candidate_df['Candidate Residential Jurisdiction'] == county_filter) & (candidate_df['Active'] == True)][['Office Name', 'Contest Run By District Name and Number',
       'Candidate Ballot Last Name and Suffix',
       'Candidate First Name and Middle Name', 'Additional Information',  
       'Office Political Party', 'Email', 'Website']]

# returns the url for the first result corresponding to the search term
def google_search(search_term: str, num: int = 1) -> str:
    x = requests.get(f'https://www.googleapis.com/customsearch/v1?key=**&cx=363e2e664898f419b&q={search_term}&num={num}')
    return x.json()['items'][0]['formattedUrl']

def consolidate_source_website(candidate_data: pd.DataFrame):
    candidate_source = []
    for index, row in candidate_data.iterrows():
        if not pd.isna(row['Website']):
            candidate_source.append(row['Website'])
        else:
            candidate_name = row['Candidate First Name and Middle Name'] + ' ' + row['Candidate Ballot Last Name and Suffix']
            print(candidate_name)
            candidate_source.append(google_search(candidate_name))
    print('Websites collected.')
    candidate_data['Site'] = candidate_source
    return candidate_data

def scrape_sources(source_list: Union[list[str], pd.Series[str]]):
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}
    for src in source_list:
        try:
            soup = BeautifulSoup(requests.get(src + 'issues', headers=headers).content, 'html5lib')
        except requests.ConnectionError as e:
            print(e)
            soup = BeautifulSoup(requests.get(src, headers=headers).content, 'html5lib')
        

if __name__ == '__main__':
    candidate_file = Path.cwd().joinpath('data\gen_cand_lists_2024_1_ALL.csv')
    print(consolidate_source_website(data_load(candidate_file)))
