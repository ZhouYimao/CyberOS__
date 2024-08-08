from unittest import result
import requests



# Specify the number of references from the search engine you want to use.
# 8 is usually a good number.
REFERENCE_COUNT = 8

# Specify the default timeout for the search engine. If the search engine
# does not respond within this time, we will return an error.
DEFAULT_SEARCH_ENGINE_TIMEOUT = 5

SEARCHAPI_SEARCH_ENDPOINT = "https://www.searchapi.io/api/v1/search"
SEARCHAPI_KEY="ozPp63ZAbRT3aweiGVXF2XnC"


def Google_search(query: str,result_num: int):
    """
    Search with SearchApi.io and return the contexts.
    """
    '''
    payload = {
        "q": query,
        "engine": "google",
        "num": (
            REFERENCE_COUNT
            if REFERENCE_COUNT % 10 == 0
            else (REFERENCE_COUNT // 10 + 1) * 10
        ),
    }
    '''
    subscription_key = SEARCHAPI_KEY
    payload = {
        "q": query,
        "engine": "google",
        "num": result_num
    }
    headers = {"Authorization": f"Bearer {subscription_key}", "Content-Type": "application/json"}
    
    response = requests.get(
        SEARCHAPI_SEARCH_ENDPOINT,
        headers=headers,
        params=payload,
        timeout=30,
    )

    json_content = response.json()
    
    # convert to the same format as google
    contexts = []
    
    if json_content.get("answer_box"):
        if json_content["answer_box"].get("organic_result"):
            title = json_content["answer_box"].get("organic_result").get("title", "")
            url = json_content["answer_box"].get("organic_result").get("link", "")
        if json_content["answer_box"].get("type") == "population_graph":
            title = json_content["answer_box"].get("place", "")
            url = json_content["answer_box"].get("explore_more_link", "")

        title = json_content["answer_box"].get("title", "")
        url = json_content["answer_box"].get("link")
        snippet =  json_content["answer_box"].get("answer") or json_content["answer_box"].get("snippet")

        if url and snippet:
            contexts.append({
                "name": title,
                "url": url,
                "snippet": snippet
            })

    if json_content.get("knowledge_graph"):
        if json_content["knowledge_graph"].get("source"):
            url = json_content["knowledge_graph"].get("source").get("link", "")

        url = json_content["knowledge_graph"].get("website", "")
        snippet = json_content["knowledge_graph"].get("description")

        if url and snippet:
            contexts.append({
               "name": json_content["knowledge_graph"].get("title", ""),
               "url": url,
               "snippet": snippet
            })

    contexts += [
        {"name": c["title"], "url": c["link"], "snippet": c.get("snippet", "")}
        for c in json_content["organic_results"]
    ]
        
    if json_content.get("related_questions"):
        for question in json_content["related_questions"]:
            if question.get("source"):
                url = question.get("source").get("link", "")
            else:
                url = ""  
                    
            snippet = question.get("answer", "")

            if url and snippet:
                contexts.append({
                    "name": question.get("question", ""),
                    "url": url,
                    "snippet": snippet
                })

    return contexts[:REFERENCE_COUNT]

    
if __name__ == "__main__":
    query = "给我一些WAIC 2024的关键信息"
    result_num = 5
    print(Google_search(query,result_num))
