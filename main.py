from conllu import parse_incr
import spacy

# Load the spacy model
nlp = spacy.load('nl_core_news_sm')
print('Loaded Spacy Model')

test_file = open("UD_Dutch-LassySmall/nl_lassysmall-ud-test.conllu", "r", encoding="utf-8")

incorrect_sentences = 0
correct_sentences = 0
incorrect_tokens = 0
correct_tokens = 0

def show_percentage():
    sentences_percent = float(correct_sentences) * 100.0/ float(incorrect_sentences + correct_sentences)
    print('\n------- Sentences {0:.2f}% - Incorrect {1} vs correct {2}'.format(sentences_percent, incorrect_sentences, correct_sentences))

    tokens_percent = float(correct_tokens) * 100.0/ float(incorrect_tokens + correct_tokens)
    print('------- Tokens    {0:.2f}% - Incorrect {1} vs correct {2}'.format(tokens_percent, incorrect_tokens, correct_tokens))

for tokenlist in parse_incr(test_file):
    # We create an array of flattened tokens to make sure we use the same data in the ground truth as is available in metadata.text
    # We do this because the ground truth contains nested tokens that don't exist in the metadata text file
    flattened_tokens = []

    for token in tokenlist:
        # Lets skip all tokens that are nested (e.g ID 10.1)
        if isinstance(token['id'], int):
            flattened_tokens.append(token)

    # Parse the text in metadata object with Spacy
    metdata_text = tokenlist.metadata['text']
    spacy_tokens = nlp(metdata_text)

    truth_token_count = len(flattened_tokens)
    spacy_token_count = len(spacy_tokens)
    
    token_index = 0

    has_mistake = False
    for i in range(0, truth_token_count):
        
        # For some sentences, spacy parses different number of tokens then the ground truth
        # e.g not understanding the . in the end of a sentence is a punctuation and not part of the last word
        # For these cases we have a special case to debug more information in the terminal
        if len(spacy_tokens) <= i:
            has_mistake = True
            incorrect_tokens += 1

            spacy_token_words = []
            for token in spacy_tokens:
                spacy_token_words.append(str(token))

            spacy_token_tags = []
            for token in spacy_tokens:
                spacy_token_tags.append(str(token.pos_))

            truth_token_words = []
            for token in flattened_tokens:
                truth_token_words.append(str(token['form']))
            
            truth_token_tags = []
            for token in flattened_tokens:
                truth_token_tags.append(str(token['upostag']))
            
            print('\nMismatch of parsed # of tokens. Truth had {} tokens but Spacy parsed the text into {} tokens'.format(truth_token_count, len(spacy_tokens)))
            print('Truth ' + '-'.join(truth_token_words))
            print('Spacy ' + '-'.join(spacy_token_words))
            print('TruthTags ' + '-'.join(truth_token_tags))
            print('SpacyTags ' + '-'.join(spacy_token_tags))
            break

        truth_token = flattened_tokens[i]
        spacy_token = spacy_tokens[i]
        
        spacy_pos_tag = str(spacy_token.pos_)
        truth_pos_tag = str(truth_token['upostag'])

        # If the POS token from spacy doesn't match match the ground truth we consider a mistake
        # NOTE: We are using `in` instead of '=' for string matching because the ground truth 
        # contains SCONJ and CCONJ while spacy only returns CONJ for those tokens
        if spacy_pos_tag not in truth_pos_tag:
            has_mistake = True
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

test_file.close()