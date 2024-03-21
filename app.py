from flask import Flask, render_template, request, session
import os
from cleanprompt import PromptCleaner
from cryptography.fernet import Fernet

# Utility for encryption and decryption
class SessionCrypto:
    def __init__(self, key):
        self.cipher_suite = Fernet(key)
    
    def encrypt(self, data):
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt(self, data):
        return self.cipher_suite.decrypt(data.encode()).decode()

cleaner = PromptCleaner()

app = Flask(__name__)
app.secret_key = os.urandom(24) # used for signing the session cookie

fernet_key = Fernet.generate_key() # Generate a key for Fernet, used for encryption/decryption
session_crypto = SessionCrypto(fernet_key)

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'GET':
        session.pop('encrypted_replacements', None)

    original_text = ""
    processed_text = ""
    llm_response = ""
    reverted_text = ""
    mappings = {}

    if request.method == 'POST':
        if 'process_text' in request.form:
            original_text = request.form['text']
            additional_words = request.form.get('additional_words', '')
            additional_texts = [word.strip() for word in additional_words.split(',') if word.strip()]
            
            processed_text, custom_replacements = cleaner.replace_custom(original_text, additional_texts)
            processed_text, entity_replacements = cleaner.replace_ner(processed_text)
            replacements = {**custom_replacements, **entity_replacements}
            
            # Encrypt replacements before storing in session
            encrypted_replacements = session_crypto.encrypt(str(replacements))
            session['encrypted_replacements'] = encrypted_replacements

        elif 'revert_text' in request.form:
            llm_response = request.form['llm_response']
            original_text = request.form.get('original_text', '')
            processed_text = request.form.get('processed_text', '')
            encrypted_replacements = session.get('encrypted_replacements', '')
            if encrypted_replacements:
                # Decrypt replacements when accessing
                decrypted_replacements = session_crypto.decrypt(encrypted_replacements)
                replacements = eval(decrypted_replacements) # string becomes a dict
            else:
                replacements = {}
            reverted_text = cleaner.revert_text(llm_response, replacements, False)

    encrypted_replacements = session.get('encrypted_replacements', '')
    if encrypted_replacements:
        decrypted_replacements = session_crypto.decrypt(encrypted_replacements)
        mappings = eval(decrypted_replacements) # string becomes a dict
    else:
        mappings = {}

    return render_template('index.html',
                           original_text=original_text,
                           processed_text=processed_text,
                           mappings=mappings,
                           llm_response=llm_response,
                           reverted_text=reverted_text
                           )

@app.route('/reset')
def reset():
    session.pop('encrypted_replacements', None)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False)
