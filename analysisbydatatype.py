from bs4 import BeautifulSoup
from googleapiclient.discovery import build
import requests
import pandas as pd
from nltk.corpus import stopwords
from nltk import word_tokenize
import string
from collections import Counter
import re

api_key = "custom search api"
cx = "programmable search engine"

def google_search(query, num_results=10):
    service = build("customsearch", "v1", developerKey=api_key)
    results = []
    for title_query in query.split('\n'):
        title, q = title_query.split(" title:")
        res = service.cse().list(q=q + " intitle:" + title, cx=cx, num=num_results, cr="countryTR").execute()
        results.extend(res['items'])
    return results

def clean_text(text):
    punct = string.punctuation + '‘’“”\t\n\r\x0c'
    text = text.lower().translate(str.maketrans('', '', punct))
    return text

keywords = {
"your keywords"
}
content_type_keyword_counts = {'Haber': Counter({keyword: 0 for keyword in keywords}),
                               'Makale': Counter({keyword: 0 for keyword in keywords}),
                               'Bilinmeyen': Counter({keyword: 0 for keyword in keywords})}

search_terms = [
"your search items"
]
stop_words = set(stopwords.words('turkish'))

filtered_results = []
for term in search_terms:
    results = google_search(term)
    filtered_results.extend(results)

for result in filtered_results:
    url = result['link']
    try:
        response = requests.get(url, verify=True)
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        text = clean_text(text)
        tokens = word_tokenize(text)
        phrases = [' '.join(tokens[i:i+2]) for i in range(len(tokens) - 1)]
        words = [word for word in tokens + phrases if word in keywords]

        content_type = 'Bilinmeyen'
        if 'makale' in url.lower() or 'makale' in result['snippet'].lower() or 'makale' in result['title'].lower() or '.pdf' in url.lower():
            content_type = 'Makale'
        elif 'haber' in url.lower() or 'haber' in result['snippet'].lower() or 'haber' in result['title'].lower():
            content_type = 'Haber'

        if words:
            content_type_keyword_counts[content_type].update(words)
    except Exception as e:
        print(f"Hata: {e}")
        print(f"URL atlandı: {url}")

save_path = 'your path'
filtered_results_data = [{'Title': r['title'], 'Snippet': r['snippet'], 'Source': r['link']} for r in filtered_results]
df = pd.DataFrame(filtered_results_data)

excel_file = save_path + 'filtered_results.xlsx'
with pd.ExcelWriter(excel_file) as writer:
    df.to_excel(writer, index=False, sheet_name='Filtered Results')

    content_type_counts_df = pd.DataFrame.from_dict(content_type_keyword_counts, orient='index').transpose()
    content_type_counts_df.to_excel(writer, index=True, sheet_name='Content Type Keyword Counts')

print("Veriler başarıyla Excel dosyasına kaydedildi.")
