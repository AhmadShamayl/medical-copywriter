import re

def clean_text (text: str) -> str:
    #normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    #remove page headers and footers
    text = re.sub(r'Page \d+', '', text, flags = re.IGNORECASE)
    text = re.sub(r'NCBI Bookeshelf,*?\n' , '', text, flags = re.IGNORECASE)

    # fix hyphenated words at line breaks
    text = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', text)

    #remove inline citations like [1], (Smith et al., 2020)
    text = re.sub(r'\[\d+(,\s*\d+)*\]', '', text)
    text = re.sub(r'\(\d+(,\s*\d+)*\)', '', text)

    # Stansdadize quotes and dashes
    text = text.replace('“', '"').replace('”', '"').replace("‘", "'").replace("’", "'")
    text = text.replace('—', '-').replace('–', '-')

    # removing special characters except basic punctuation
    text = re.sub(r'[^a-zA-Z0-9.,;:!?\'"()\-\s/%+]', '', text)

    return text
 
