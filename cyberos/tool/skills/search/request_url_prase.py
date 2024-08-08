import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from googlesearch import search
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

TOTAL_TIMEOUT = 6  # Overall timeout for all operations
NUM_SEARCH = 10  # Number of links to parse from Google
SEARCH_TIME_LIMIT = 3  # Max seconds to request website sources before skipping to the next URL

def fetch_webpage(url, timeout):
    """Fetch the content of a webpage given a URL and a timeout."""
    start = time.time()
    sys.settrace(trace_function_factory(start))
    try:
        print(f"Fetching link: {url}")
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        paragraphs = soup.find_all('p')
        page_text = ' '.join([para.get_text() for para in paragraphs])
        return url, page_text
    except (requests.exceptions.RequestException, TimeoutError) as e:
        print(f"Error fetching {url}: {e}")
    finally:
        sys.settrace(None)
    return url, None

def google_parse_webpages(query, num_search=NUM_SEARCH, search_time_limit=SEARCH_TIME_LIMIT):
    """Perform a Google search and parse the content of the top results."""
    urls = search(query, num_results=num_search)
    max_workers = os.cpu_count() or 1  # Fallback to 1 if os.cpu_count() returns None
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(fetch_webpage, url, search_time_limit): url for url in urls}
        return {url: page_text for future in as_completed(future_to_url) if (url := future.result()[0]) and (page_text := future.result()[1])}

def trace_function_factory(start):
    """Create a trace function to timeout request"""
    def trace_function(frame, event, arg):
        if time.time() - start > TOTAL_TIMEOUT:
            raise TimeoutError('website fetching timed out')
        return trace_function
    return trace_function

def test():
    query = '巴黎奥运会各国奖牌情况怎么样？'
    search_dic = google_parse_webpages(query)
    print(search_dic)

if __name__ == "__main__":
    test()
