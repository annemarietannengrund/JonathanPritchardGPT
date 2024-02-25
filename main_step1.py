from src.JonathanPritchardCrawler import JonathanPritchardCrawler
from dotenv import load_dotenv
from os import environ
load_dotenv()

if __name__ == "__main__":
    source_directory = environ.get('SOURCE_DIRECTORY', 'obsidian')
    app = JonathanPritchardCrawler(source_directory)
    app.main()