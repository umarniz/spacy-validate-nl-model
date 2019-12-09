from conllu import parse_incr
import spacy

nlp = spacy.load('nl_core_news_sm')
print('Loaded Spacy Model')

data_file = open("datasets/UD_Dutch-LassySmall/nl_lassysmall-ud-test.conllu", "r", encoding="utf-8")

incorrect_sentences = 0
correct_sentences = 0
incorrect_tokens = 0
correct_tokens = 0

def show_percentage():
    sentences_percent = float(correct_sentences) * 100.0/ float(incorrect_sentences + correct_sentences)
    print('\n------- Sentences {0:.2f}% - Incorrect {1} vs correct {2}'.format(sentences_percent, incorrect_sentences, correct_sentences))

    tokens_percent = float(correct_tokens) * 100.0/ float(incorrect_tokens + correct_tokens)
    print('------- Tokens    {0:.2f}% - Incorrect {1} vs correct {2}'.format(tokens_percent, incorrect_tokens, correct_tokens))

for tokenlist in parse_incr(data_file):
    # e.g OrderedDict([('id', 1), ('form', 'Totale'), ('lemma', 'totaal'), ('upostag', 'ADJ'), ('xpostag', 'ADJ|prenom|basis|met-e|stan'), ('feats', OrderedDict([('Degree', 'Pos')])), ('head', 2), ('deprel', 'amod'), ('deps', [('amod', 2)]), ('misc', None)])

    # We create an array of flattened tokens to make sure we use the same data in the ground truth
    # As is available in metdata.text
    flattened_tokens = []

    for token in tokenlist:
        # Lets skip all tokens that are nested (e.g ID 10.1)
        if isinstance(token['id'], int):
            flattened_tokens.append(token)

    # Lets work with sentences that are alteast 3 characters
    tokencount = len(flattened_tokens)
    # if tokencount < 3:
    #     continue

    token_index = 0
    text = tokenlist.metadata['text']

    spacy_tokens = nlp(text)

    has_mistake = False
    for i in range(0, tokencount):
        current_token = flattened_tokens[i]
        
        if len(spacy_tokens) <= i:
            has_mistake = True
            incorrect_tokens += 1

            spacy_text = []
            for token in spacy_tokens:
                spacy_text.append(str(token))

            spacy_tags = []
            for token in spacy_tokens:
                spacy_tags.append(str(token.pos_))

            truth_text = []
            for token in flattened_tokens:
                truth_text.append(str(token['form']))
            
            truth_tags = []
            for token in flattened_tokens:
                truth_tags.append(str(token['upostag']))
            
            print('\nMismatch of tokens. Truth {} Spacy {}'.format(tokencount, len(spacy_tokens)))
            print('Truth ' + '-'.join(truth_text))
            print('Spacy ' + '-'.join(spacy_text))
            print('TruthTags ' + '-'.join(truth_tags))
            print('SpacyTags ' + '-'.join(spacy_tags))
            break

        spacy_token = spacy_tokens[i]

        # If the POS token from spacy doesn't match match the ground truth we consider a mistake

        # NOTE: We are using `in` instead of equals to for string matching because the ground truth 
        # contains SCONJ and CCONJ while spacy only returns CONJ for those tokens
        if str(spacy_token.pos_) not in str(current_token['upostag']):
            has_mistake = True
            # print('Truth {}-{} vs {}-{}'.format(current_token['form'], current_token['upostag'], spacy_token, spacy_token.pos_))
            incorrect_tokens += 1
        else:
            correct_tokens += 1
    
    if has_mistake:
        incorrect_sentences += 1
    else:
        correct_sentences += 1

    if incorrect_sentences % 100 == 0 and incorrect_sentences > 0:
        show_percentage()

show_percentage()

data_file.close()