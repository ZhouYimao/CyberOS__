from unstructured.partition.html import partition_html
from cleaning import clean_text
elements = partition_html(url='https://www.apple.com/')
full_text = ''
for el in elements:
    text = clean_text(el.text)
    full_text += (text + ' ')
print(full_text)
