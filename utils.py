from PIL import Image
from pdf2image import convert_from_path
import PyPDF2


def create_dir(path):
    """
    Create a directory if it doesn't exist.
    """
    import os
    if not os.path.exists(path):
        os.makedirs(path)


def pdf_to_image(pdf_path, output_path, dpi=300):
    """
    Convert a PDF into a series of images.
    """
    create_dir(output_path)
    list_paths = []
    images = convert_from_path(pdf_path, dpi=dpi)
    for i, image in enumerate(images):
        image.save(f"{output_path}/{i}.png", "PNG")
        list_paths.append(f"{output_path}/{i}.png")
    return list_paths


def pdf_to_text(pdf_path):
    """
    Extract text from a PDF.
    """
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text


def cut_image(image_path, output_path, x, y, width, height):
    """
    Cut a section of an image and save it.
    """
    image = Image.open(image_path)
    section = image.crop((x, y, width, height))
    section.save(output_path)
    return output_path


def image_to_text(image_path: str):
    """
    Extract text from an image.
    """
    import pytesseract
    from PIL import Image

    image = Image.open(image_path).convert("RGB")
    generated_text = pytesseract.image_to_string(image)
    return generated_text


def curate_text(text: str):
    from transformers import pipeline

    fix_spelling = pipeline("text2text-generation", model="oliverguhr/spelling-correction-german-base")
    t = "correct:" + text
    data = fix_spelling(t, max_length=256)
    return data[0]["generated_text"]


