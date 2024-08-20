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
        if " title:" in title_query:
            title, q = title_query.split(" title:", 1)
            res = service.cse().list(q=q + " intitle:" + title, cx=cx, num=num_results, cr="countryTR").execute()
            results.extend(res.get('items', []))
    return results

def clean_text(text):
    punct = string.punctuation + '‘’“”\t\n\r\x0c'
    text = text.lower().translate(str.maketrans('', '', punct))
    return text

keywords = {
"your keywords"
}

yearly_keyword_counts = {year: Counter({keyword: 0 for keyword in keywords}) for year in range(2014, 2025)}
yearly_keyword_counts['Bilinmeyen'] = Counter({keyword: 0 for keyword in keywords})

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
        year_match = re.search(r'\b(20\d{2})\b', text)
        if year_match:
            year = int(year_match.group(0))
        else:
            year = 'Bilinmeyen'

        if words:
            yearly_keyword_counts[year].update(words)
    except Exception as e:
        print(f"Hata: {e}")
        print(f"URL atlandı: {url}")

save_path = 'your path'
filtered_results_data = [{'Title': r['title'], 'Snippet': r['snippet'], 'Source': r['link']} for r in filtered_results]
df = pd.DataFrame(filtered_results_data)
df['Date'] = df['Snippet'].apply(lambda x: re.search(r'\b(20\d{2})\b', x).group(0) if re.search(r'\b(20\d{2})\b', x) else 'Bilinmeyen')
df_with_dates = df[df['Date'] != 'Bilinmeyen']

excel_file = save_path + 'filtered_results.xlsx'
with pd.ExcelWriter(excel_file) as writer:
    df.to_excel(writer, index=False, sheet_name='Filtered Results')
    pd.DataFrame(yearly_keyword_counts).transpose().to_excel(writer, index=True, sheet_name='Yearly Keyword Counts')

print("Veriler başarıyla Excel dosyasına kaydedildi.")
