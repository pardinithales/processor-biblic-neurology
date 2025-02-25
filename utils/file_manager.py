def save_processed_text(file_path, processed_text):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(processed_text)