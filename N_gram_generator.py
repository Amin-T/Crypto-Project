import spacy

nlp = spacy.load('en_core_web_sm')

def NgramGenerator(text, N):
    """
    This function generates N-grams from SpaCy tokens in a text. The function makes sure
    that the n-grams does not include any punctuations.

    text: String object to be tokenized.
    N: Number of words in n-grams, as a list og integers.
    """
    doc = nlp(text)
    N_grams = []

    for n in N:
        for t in doc[:-n+1]:
            
            # Make sure the n-gram does not start with punct or stopword
            if not (t.is_space or t.is_stop or t.is_punct):
                start = t.i
                end = t.i
                while (end-start < n-1):

                    # Make sure n-gram does not include any punct
                    if doc[end+1].is_punct:
                        break
                    else:
                        end += 1

                ngram = doc[start:end+1]
                if len(ngram)>=n:
                    N_grams.append((ngram))
        
    N_grams = list(set(N_grams))

    return N_grams