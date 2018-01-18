def write_to_file(text, file_name):
    with open(file_name, "w", encoding = 'utf8') as text_file:
        text_file.write(text)
