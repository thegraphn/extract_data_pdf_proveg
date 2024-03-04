from collections import defaultdict

from utils import pdf_to_image, cut_image, image_to_text, curate_text
from config import sub_images_coordinates


def main(pdf_path: str, csv_output_path: str):
    """
    Convert a PDF into a series of images and extract text from it.
    """
    IMAGES_DIR = "./images"
    image_paths = pdf_to_image(pdf_path, output_path=IMAGES_DIR)
    print(image_paths)
    # create the sub images containing the data to extract
    data_extracted = defaultdict(dict)
    for image_path in image_paths:
        for page, coordinate_data in sub_images_coordinates.items():
            if page not in data_extracted:
                data_extracted[page] = {}
            if page in image_path:
                for name, data in coordinate_data.items():
                    data_extracted[page][name] = {"image_path": "", "data_extracted": ""}
                    sub_image_path = cut_image(image_path=image_path,
                                               output_path=f"./{page}_{name}.png",
                                               x=data["coordiates"][0],
                                               y=data["coordiates"][1],
                                               width=data["coordiates"][2],
                                               height=data["coordiates"][3])
                    data_extracted[page][name]["image_path"] = sub_image_path
                    generated_text = str(image_to_text(sub_image_path))
                    if len(generated_text) > 1:
                        text = curate_text(generated_text)
                    else:
                        text = "No text found"
                    data_extracted[page][name]["data_extracted"] = text

    print(data_extracted)
if __name__ == "__main__":
    PDF_PATH = "/Users/levecq/private_repository/extract_data_pdf_proveg/data/muster-prufformular.pdf"
    main(pdf_path=PDF_PATH, csv_output_path="output.csv")
