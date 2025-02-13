def main():
    print('Type "en" if you want to translate from French into English, or "fr" if you want to translate from English into French:')
    language = input('').strip()
    
    print('Type the word you want to translate:')
    word = input('').strip()
    
    print(f'You chose "{language}" as the language to translate "{word}" to.')

if __name__ == "__main__":
    main()

