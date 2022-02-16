import pprint
from googleapiclient.discovery import build
import numpy as np
import random

key = "AIzaSyAGmypTtalCS9lLgosvQiBQBIJ3FbviylU"  # TODO: make an environment variable
id = 'e1418010197679c8b'


def get_results(query):
    """
    TODO
    :param query:
    :return:
    """
    service = build("customsearch", "v1",
                    developerKey=key)

    res = service.cse().list(
        q=query,
        cx=id,
    ).execute()

    user_res = list()
    pprint.pprint(res)
    for result in res["items"]:
        if "fileType" in result:
            print("PDF FOUND !!")
            continue

        document = {"title": result["title"],
                    "url": result["formattedUrl"],
                    "summary": result["snippet"]}
        user_res.append(document)

    return user_res


def get_feedback_from_user(user_res):
    """
    TODO
    """
    relevant_docs = list()
    irrelevant_docs = list()

    for doc in user_res:
        print("RESULT 1 \n" + "=" * 20)
        pprint.pprint(doc)
        feedback = random.choice(["Y", "N"]) # input("Relevant? (Y/N)  ")  # TODO: error checking stuff

        if feedback == "Y":
            relevant_docs.append(doc)
        elif feedback == "N":
            irrelevant_docs.append(doc)
        else:
            print("BRUH")
            return

    return relevant_docs, irrelevant_docs


def make_bag_of_words(query_li, relevant_docs, irrelevant_docs):
    bag_of_words = dict()
    idx = 0
    words = query_li + [text_to_list(doc["summary"]) for doc in irrelevant_docs][0] + [text_to_list(doc["summary"]) for doc in relevant_docs][0]
    for word in words:
            if word in bag_of_words:
                bag_of_words[word]["freq"] += 1
            else:
                bag_of_words[word] = {"index": idx,
                                      "freq": 1}
                idx += 1
    return bag_of_words

def clean_word(word):
    return ''.join(ch for ch in word if ch.isalnum()).lower() # TODO: more error checking and get rid of punctuation make sure this works

def text_to_list(text):
    return [clean_word(w) for w in text.split()]

def is_precision_meet(precision, target_value, relevant_docs, irrelevant_docs):
    num_documents = len(relevant_docs) + len(irrelevant_docs)
    precision = len(relevant_docs)/num_documents
    if (precision <= target_value) or (precision != 0):
        return True
    return False


def rocchio_algo(relevant_docs, irrelevant_docs, query_prev, alpha=1, beta=0.75, gamma=0.15):
    num_relevant = len(relevant_docs)
    num_irrelevant = len(irrelevant_docs)

    query_next = (alpha * query_prev) + (beta * (np.sum(relevant_docs))/num_relevant) - gamma * (np.sum(irrelevant_docs))/num_irrelevant
    return query_next



def vectorize_text(list_of_words, bag_of_words):
    """
    :param bag_of_words:
    :param list_of_words:
    :param text:
    :return:
    """
    vec = [0] * len(bag_of_words)
    for term in list_of_words:
        vec[bag_of_words[term]["index"]] += 1
    
    
    return vec

def weight(N, tf, df):
    return (1 + np.log(tf)) * np.log(N/df)

def get_document_matrix(docs, bag_of_words, N):
    m = np.zeros((len(docs), len(bag_of_words)))
    for k in range(len(docs)):
        doc = text_to_list(docs[k]["summary"])
        doc_tf = [0] * len(bag_of_words)
        for term in doc:
            doc_tf[bag_of_words[term]["index"]] += 1
        doc_vec = np.zeros((len(bag_of_words)))
        for word in bag_of_words.values():
            idx = word["index"]
            tf = doc_vec[idx]
            df = word["freq"]
            doc_vec[idx] = weight(N, tf, df)
            m[k] = doc_vec

    return m

def main():
    raw_query = "milky way"
    query = raw_query.lower()
    query_li = raw_query.lower().split()
    user_res = get_results(query)
     # TODO: if less than 10 are returned, we terminate (including the pdf)
    precision = 0
  
    relevant_docs, irrelevant_docs = get_feedback_from_user(user_res)

    if False and is_precision_meet(precision, target_value, relevant_docs, irrelevant_docs): # TODO
        return "DONE"
    else:
        # TODO: should we stop?
        N = len(relevant_docs) + len(irrelevant_docs) # TODO we should figure out how to handle this during an iteration

        bag_of_words = make_bag_of_words(query_li, relevant_docs, irrelevant_docs)
        q_vec = vectorize_text(query_li, bag_of_words)
        relevant_m = get_document_matrix(relevant_docs, bag_of_words, N)
        irrelevant_m = get_document_matrix(irrelevant_docs, bag_of_words, N)
        query_next = rocchio_algo(relevant_m, irrelevant_m, bag_of_words)



if __name__ == '__main__':
    main()
