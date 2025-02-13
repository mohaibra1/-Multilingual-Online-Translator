import requests
from bs4 import BeautifulSoup


def get_translations_and_examples(language, word):
    url = f'https://context.reverso.net/translation/{"english-french" if language == "fr" else "french-english"}/{word}'
    headers = {'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 Chrome/93.0.4577.82 Safari/537.36'}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Error: Unable to retrieve data.")
        return

    print(f'{response.status_code} OK')

    soup = BeautifulSoup(response.text, 'html.parser')
    translations = [t.text.strip() for t in soup.select('.display-term')]
    examples = [e.text.strip() for e in soup.select('.example .text')]

    print("Translations")
    print(translations)
    print(examples)

    # for i in range(0, len(examples), 2):
    #     print(f'{examples[i]}\n{examples[i + 1]}')


def main():
    print(
        'Type "en" if you want to translate from French into English, or "fr" if you want to translate from English into French:')
    language = input('').strip()

    print('Type the word you want to translate:')
    word = input('').strip()

    print(f'You chose "{language}" as the language to translate "{word}".')
    get_translations_and_examples(language, word)


if __name__ == "__main__":
    main()
