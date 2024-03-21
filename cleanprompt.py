import spacy
import re

class PromptCleaner:
    '''A class to anonymize and deanonymize text using regular expressions and NER'''

    def __init__(self, model="en_core_web_lg"):
        self.nlp = spacy.load(model)
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?(?:\(\d{2,4}\)|\d{2,4})[-.\s]?\d{2,4}[-.\s]?\d{2,4}(?:[-.\s]?\d{1,4})?'
        self.url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        self.counters = {"EMAIL": 1, "PHONE": 1, "URL": 1, "ADDITIONAL": 1}
        self.found_items = {"EMAIL": {}, "PHONE": {}, "URL": {}, "ADDITIONAL": {}}

    def find_and_tag(self, pattern, tag, text):
        '''
        Find and tag all occurrences of a pattern in the entire text.
        Returns a dictionary of original matched string to unique tags.
        '''
        replacements = {}
        for match in re.finditer(pattern, text):
            original = match.group()
            if original not in self.found_items[tag]:
                self.found_items[tag][original] = f"[{tag}-{self.counters[tag]}]"
                self.counters[tag] += 1
            replacements[original] = self.found_items[tag][original][1:-1]  # Store without brackets for replacement map
        return replacements

    def find_and_tag_additional(self, pattern):
        '''
        return a dictionary of additional_text string to unique tags
        '''
        replacements = {}
        # for additional text provided by user:
        for text_to_find in pattern:
            if text_to_find not in self.found_items['ADDITIONAL']:
                self.found_items['ADDITIONAL'][text_to_find] = f"[{'ADDITIONAL'}-{self.counters['ADDITIONAL']}]"
                self.counters['ADDITIONAL'] += 1
            replacements[text_to_find] = self.found_items['ADDITIONAL'][text_to_find][1:-1]

        return replacements


    def replace_regex(self, text):
        '''
        Find emails, phones, urls, and additional_texts in the text and replaces them with unique tags.
        Returns the whole text with replaced tags and a mapping of original strings to unique tags.
        '''
        replacements = {}
        replacements.update(self.find_and_tag(self.email_pattern, "EMAIL", text))
        replacements.update(self.find_and_tag(self.phone_pattern, "PHONE", text))
        replacements.update(self.find_and_tag(self.url_pattern, "URL", text))

        # Replace all found items with their tags
        for original_string, unique_tag in replacements.items():
            text = text.replace(original_string, f"[{unique_tag}]")

        return text, replacements

    def replace_ner(self, text):
        doc = self.nlp(text)
        replacements = {}
        unique_entities = {}
        entity_counts = {}

        # Identify all entities and their unique tags
        for ent in doc.ents:
            if ent.text not in unique_entities:
                if ent.label_ not in entity_counts:
                    entity_counts[ent.label_] = 0
                entity_counts[ent.label_] += 1
                unique_tag = f'{ent.label_}-{entity_counts[ent.label_]}'
                unique_entities[ent.text] = unique_tag
                replacements[(ent.start_char, ent.end_char)] = unique_tag
            else:
                unique_tag = unique_entities[ent.text]
                replacements[(ent.start_char, ent.end_char)] = unique_tag

        # Apply replacements in reverse order to avoid offset issues
        for (start_char, end_char), unique_tag in sorted(replacements.items(), key=lambda x: x[0][0], reverse=True):
            text = text[:start_char] + f'[{unique_tag}]' + text[end_char:]

        return text, unique_entities

    def replace_custom(self, text, additional_texts=[]):
        '''
        Find emails, phones, urls, and additional_texts in the text and replaces them with unique tags.
        Returns the whole text with replaced tags and a mapping of original strings to unique tags.
        '''
        replacements = {}
        if additional_texts:
            replacements.update(self.find_and_tag_additional(additional_texts))

        # Replace all found items with their tags
        for original_string, unique_tag in replacements.items():
            if unique_tag.split('-')[0] != 'ADDITIONAL':
                raise ValueError("unique_tag must be of type ADDITIONAL") # raise error if unique_tag is not 'ADDITIONAL'
            text = text.replace(original_string, f"[{unique_tag}]")

        return text, replacements

    def add_color(self, text, mapping):
        '''Add color to the tagged entities in the text for better visualization'''
        for tag in mapping.values():
            colored_tag = f"{Colors.OKGREEN}[{tag}]{Colors.ENDC}"  # Using green color
            escaped_tag = re.escape(f'[{tag}]')
            text = re.sub(escaped_tag, colored_tag, text) # replace the excaped tag with colored tag
        return text

    def revert_text(self, text, mapping, color=True):
        '''Revert the text back to its original form with mapping'''
        for entity, indexed_tag in mapping.items():
            if color:
                entity = f"{Colors.OKGREEN}{entity}{Colors.ENDC}" # Green color for reverted entity
            text = text.replace(f'[{indexed_tag}]', entity) # deanonymization happens here
        return text

class Colors:
    PURPLE = '\033[95m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

def get_multiline_input(instruction):
    '''Get multiline input from the user until they type END on a new line and press enter.'''
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}{instruction}{Colors.ENDC}")
    lines = []
    while True:
        try:
            line = input()
            if line.strip().lower() == 'end':
                break
            lines.append(line)
        except EOFError:
            print("\nEOF signal detected, ending input.")  # Optional
            break
    return '\n'.join(lines)


def get_additional_text_to_hide():
    '''Get additional text to hide if user has any.'''
    response = input(f"{Colors.BOLD}{Colors.OKCYAN}Do you have additional text to hide? (yes/no): {Colors.ENDC}").strip().lower()
    if response in ['yes', 'y']:
        additional_text = input(f"{Colors.BOLD}{Colors.OKCYAN}Enter the text you want to hide, separated by commas: {Colors.ENDC}")
        return [text.strip() for text in additional_text.split(',') if text.strip()]
    return []

if __name__ == "__main__":
    cleaner = PromptCleaner()

    instruction_initial = "Welcome to CleanPrompt! Enter/paste your text. Type 'END' on a new line and press enter to submit:"
    text = get_multiline_input(instruction_initial) # get text from user which potentially includes sensitive info
    replaced_text, regex_mapping = cleaner.replace_regex(text)
    replaced_text, entity_mapping = cleaner.replace_ner(replaced_text)
    combined_mapping = {**regex_mapping, **entity_mapping}
    removed_info_summary = ', '.join(list(combined_mapping.keys()))
    print(f"{Colors.BOLD}{Colors.PURPLE}\nRemoved sensitive information: {removed_info_summary}{Colors.ENDC}")
    colored_anonymized_text = cleaner.add_color(replaced_text, combined_mapping)
    print(f"{Colors.BOLD}{Colors.OKCYAN}\nUse the following anonymized text:\n{Colors.ENDC}{colored_anonymized_text}")
    
    # list of additional text to hide provided by the user (empty list if no additional text):
    additional_text_to_hide = get_additional_text_to_hide()
    
    if additional_text_to_hide:
        # basically the same steps as above but with additional text included:
        replaced_text, regex_mapping = cleaner.replace_custom(text)
        replaced_text, entity_mapping = cleaner.replace_ner(replaced_text)
        replaced_text, additional_mapping = cleaner.replace_custom(replaced_text, additional_text_to_hide)
        combined_mapping = {**regex_mapping, **entity_mapping, **additional_mapping}
        removed_info_summary = ', '.join(list(combined_mapping.keys()))
        print(f"{Colors.BOLD}{Colors.PURPLE}\nRemoved sensitive information: {removed_info_summary}{Colors.ENDC}")
        colored_anonymized_text = cleaner.add_color(replaced_text, combined_mapping)
        print(f"{Colors.BOLD}{Colors.OKCYAN}\nUse the following anonymized text:\n{Colors.ENDC}{colored_anonymized_text}")

    instruction_final = "Enter/paste the response from your LLM. Type 'END' on a new line and press enter to submit:"
    LLM_text = get_multiline_input(instruction_final)
    deanonymized_text = cleaner.revert_text(LLM_text, combined_mapping, color=True)
    print(f"{Colors.BOLD}{Colors.OKCYAN}\nPrivate information restored:{Colors.ENDC}\n{deanonymized_text}\n")
