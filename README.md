# JonathanPritchardGPT 

This is based on the official ollama.ai example of a [local privateGPT implementation](https://github.com/ollama/ollama/tree/main/examples/langchain-python-rag-privategpt).

As base data for the model to consume a hundred blog posts of [Jonathan Pritchard](https://www.jonathanpritchard.me).

The data is scraped with a custom scraper that converts html pages to obsidian compatible markdown files.

## PrivateGPT with Llama 2 uncensored

https://github.com/jmorganca/ollama/assets/3325447/20cf8ec6-ff25-42c6-bdd8-9be594e3ce1b

> Note: this example is a slightly modified version of PrivateGPT. All credit for PrivateGPT goes to Iván Martínez who is the creator of it, and you can find his GitHub repo [here](https://github.com/imartinez/privateGPT).
> Note: this example is a slightly modified version of Ollama.ai [langchain-python-rag](https://github.com/ollama/ollama/tree/main/examples/langchain-python-rag-privategpt), all credits for this got to them..

### have python installed
for windows ..
Download a python version around 3.10:
- https://www.python.org/downloads/
- restart your machine, probably
- press your `windows key`
- type `cmd.exe`
- press enter
- enter command `python3.exe --version`

that should respond with whatever you have installed.


### Setup

Set up a virtual environment (optional)(Recommended!:
(do this in this directory where the this file is)
```
python3 -m venv .venv
# activate the environment
source .venv/bin/activate
# on windows try
activate
# or
.venv/bin/activate.bat
```

Then your command line has a `(.venv)` in front of it.

Install the Python dependencies:

```shell
pip install -r requirements.txt
```

Pull the model you'd like to use:

```
ollama pull llama2-uncensored
```

### Environment env file 
I actively use a module to force loading environment variables from an `.env` file present, please use the `template.env` and rename/copy it to `.env` and customize your custom inputs.

havent changed that from the original...
- EMBEDDINGS_MODEL_NAME 
- MODEL_N_CTX
- TARGET_SOURCE_CHUNKS

now listen up:
- MODEL (the model you want to use `ollama list`, pull model before using `ollama pull <name>`)
- PERSIST_DIRECTORY (database directory for the model created during ingest)
- SOURCE_DIRECTORY (used as target for the scraper and as source for the ingester)
- OBSIDIAN_LOADER regular loaders or obsidian loader
  - 0 - use the script with custom file loader ([ingest.py](ingest.py))
  - 1 - use the script with the [obsidian loader](https://python.langchain.com/docs/integrations/document_loaders/obsidian)

### Scrape blog data

Scrapes Jonathans blog and other pages there, downloads images used and converts content to obsidian compatible markdown.

you supply the script with a base directory, it will automatically create 3 default sub folders.
- assets (Downloaded images used on the page for local display)
- categories (Approach to bundle blog posts in categories)
- pages (The converted post)

(nice to watch the graph in obsidian grow as it scrapes data in)

```shell
python main_step1.py
```

### Ingesting files

```shell
python main_step2.py
```

### Ask questions

```shell
python main_step3.py
```

### Try a different model:

```
ollama pull llama2:13b
MODEL=llama2:13b python privateGPT.py
```

## Adding more files

Put any and all your files into the `obsidian` directory

The supported extensions are:

- `.csv`: CSV,
- `.docx`: Word Document,
- `.doc`: Word Document,
- `.enex`: EverNote,
- `.eml`: Email,
- `.epub`: EPub,
- `.html`: HTML File,
- `.md`: Markdown,
- `.msg`: Outlook Message,
- `.odt`: Open Document Text,
- `.pdf`: Portable Document Format (PDF),
- `.pptx` : PowerPoint Document,
- `.ppt` : PowerPoint Document,
- `.txt`: Text file (UTF-8),

## Customization

### Prime your ollama model with a system prompt

i supplied a [model file template](custom_model_template.txt).

just enter in your command line: `ollama create <new_model_name> -f custom_model_template.txt`

more infos here:
- https://github.com/ollama/ollama/blob/main/docs/modelfile.md
- https://www.youtube.com/watch?v=0ou51l-MLCo

### I want to index MY obsidian Vault!
you can do that, its save!
best define another `PERSIST_DIRECTORY` in your env, point the `SOURCE_DIRECTORY` to your own vault.

it will only read and not modify your vault!

### I want to start over, is the stuff save to delete?

- The `PERSIST_DIRECTORY` can be safely deleted!
- The automatic created folders within `obsidian` can be safely deleted (`assets`,`categories`,`pages`)!

### Make me chat with it in obsidian
nah, not interested.
there are 3 ollama plugins for obsidian which all failed on various levels of implementation.
you can chat with it over the command line, if you think its uncool, dim the lights, close the door, place a basecap on backwards and yell "HACK THE PLANET".

you can then feel cooler.

## Issues

### LLM's
its the usual issues with LLM's, they suck as soon as their tokens are all used.
it might respond to questions with `i dont know shit bout that`, 
if you ask again with the addition of `You have access to a vector database filled with hundreds of blog posts from jonathan pritchard.` and suddenly it will at least try.

you can try to feed it less documents, but that's only bringing you a little bit further.
the issues persists as long as context windows of the models are just some 10k, 50k, 100k.

### Wordpress/HTML

due to wordpress customization and `css class warfare`, some issues with the markdowns persists.
- youtube (links, embeddings) is cropped out of the article (might change)
- inline article links are unfollowed (service descriptions and authorship)
- wordpress inline tag usage in some articles creating false categories (tag-*) but should be tags instead

### No Tests

yeah. provide some if you like.
