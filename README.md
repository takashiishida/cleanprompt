# CleanPrompt

Anonymizes sensitive information in text prompts before sending them to LLM-chat applications. Instead of trying to keep up with the frequently changing privacy policies and worrying that personal data will be stored and possibly used in future model training, CleanPrompt aims to ensure that personal information isn't shared with these platforms in the first place.

**Features**
- Anonymizes emails, phone numbers, URLs, names, organizations, and other entities with regular expressions and named entity recognition.
- Supports adding custom text patterns to anonymize.
- Enables deanonymization: After the user communicates with an LLM, the user can revert the text (still containing placeholders) back to its original form.
- CLI tool and web interface.

## Using CLI

To use the CLI tool, install Spacy and download the model:

```bash
pip install spacy
python -m spacy download en_core_web_lg
```

To start the CLI tool, run:

```bash
python cleanprompt.py
```

Follow the instructions in the terminal to anonymize and deanonymize text.

## Using Web Interface

Alternatively, you can use the web app.
After installing Spacy and the model, install flask and cryptography (to enable encryption for the data stored in Flask session cookies):

```bash
pip install flask
pip install cryptography
```

Then run by:

```bash
flask run
```

Open a web browser and navigate to `http://127.0.0.1:5000` to access the web interface.

## Demo
We will anonymize the initial paragraphs from KonMari's Wikipedia page, treating the content as confidential for the sake of the demo. CleanPrompt will replace specific details like names, birthdates, book titles, and award names with placeholders. It will also prompt us to conceal additional text; we'll opt to hide mentions of "Tidying Up" and "organizing", which are strongly related to KonMari. This process allows us to engage in a discussion with LLMs without revealing private information. Here, we'll ask for a bullet-pointed summary. After receiving it, we can replace the placeholders with the original information by pasting the summary back into the terminal or web interface.

![Demo of using CleanPrompt](demo.gif)
