from hstest.stage_test import StageTest
from hstest.test_case import TestCase
from hstest.check_result import CheckResult
import requests
from bs4 import BeautifulSoup
from itertools import chain
import sys
import re


if sys.platform.startswith("win"):
    import _locale
    # pylint: disable=protected-access
    _locale._getdefaultlocale = (lambda *args: ['en_US', 'utf8'])

CheckResult.correct = lambda: CheckResult(True, '')
CheckResult.wrong = lambda feedback: CheckResult(False, feedback)


class TranslatorTest(StageTest):
    def generate(self):
        return [
            TestCase(stdin='fr\nhello\n', attach="fr\nhello"),
            TestCase(stdin='fr\nliberty\n', attach="fr\nliberty"),
            TestCase(stdin='fr\nbridge\n', attach="fr\nbridge"),
            TestCase(stdin='en\ngens\n', attach="en\ngens"),
        ]

    def check(self, reply, attach):
        language, word = attach.split("\n")

        if '200 OK' not in reply:
            return CheckResult.wrong("There isn't internet connection identifier.")

        reply = reply[reply.index("200 OK"):]
        if "translation" not in reply.lower():
            return CheckResult.wrong("Your program should output the word \"Translations\" "
                                     "before printing the translations of the word.\n"
                                     "Also, this word should follow the internet connection identifier.")

        translations = reply[reply.lower().index("translation"):].strip().split("\n")
        translations = [line for line in translations if line]
        if len(translations) != 3:
            return CheckResult.wrong("An incorrect number of lines found in your output's section with translations. \n"
                                     "There should be exactly 3 lines in it: one, containing the word \"Translations\", "
                                     "one for the translations and one for examples.")

        translations, examples = translations[-2].lower(), translations[-1].lower()
        true_translations, true_examples = get_results(language, word)
        if true_translations == "Connection error":
            return CheckResult.wrong("Connection error occurred while connecting to the context.reverso.net\n"
                                     "Please, try again a bit later.")

        translations_intersection = [True for true_transl in true_translations if true_transl.lower() in translations]
        if not translations_intersection:
            return CheckResult.wrong("The correct translations of the word are not found. \n"
                                     "Make sure you output them in the right format: \n"
                                     "your program should output a list with translations of the given word.")
        examples_intersection = [True for true_example in true_examples if true_example.lower() in examples]

        if not examples_intersection:
            return CheckResult.wrong("The correct examples for the word are not found. \n"
                                     "Make sure you output them in the right format: \n"
                                     "your program should output a list with examples for the given word. \n"
                                     "Your program should output the example sentences both in the source and target language.")

        return CheckResult.correct()


def clean_string(string_list):
    out_string = []
    for string in string_list:
        string = re.sub('\n', '', string)
        string = re.sub(' {2,}', ' ', string)
        string = re.sub('^ ', '', string)
        if string != '':
            out_string.append(string)
    return out_string


def get_results(language, word):

    if language == "en":
        lang_to, lang_from = "english", "french"
    else:
        lang_to, lang_from = "french", "english"
    url = f"https://context.reverso.net/translation/{lang_from}-{lang_to}/{word}"
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': user_agent})
    except requests.exceptions.ReadTimeout:
        return "Connection error", "Connection error"
    except requests.exceptions.ConnectionError:
            return "Connection error", "Connection error"

    raw_contents = BeautifulSoup(response.content, 'html.parser')
    # translate words
    translations = raw_contents.find_all('span', {'class': 'display-term'})
    # example sentences
    sentences_src, sentences_target = \
        raw_contents.find_all('div', {"class": "src ltr"}), raw_contents.find_all('div', {"class": ["trg ltr", "trg rtl arabic", "trg rtl"]})

    translations = set([translation.get_text().strip() for translation in translations])
    sentences = set([sentence.get_text().strip() for sentence in
                    list(chain(*[sentence_pair for sentence_pair in zip(sentences_src, sentences_target)]))])

    return translations, sentences


if __name__ == '__main__':
    TranslatorTest('translator.translator').run_tests()
