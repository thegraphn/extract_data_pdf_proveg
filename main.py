from glob import glob
import pandas as pd
from collections import defaultdict

from tqdm import tqdm

from utils import pdf_to_image, cut_image, image_to_text, curate_text, extract_check_box, convert_data_model
from config import sub_images_coordinates


def main(pdf_path: str) -> pd.DataFrame:
    """
    Convert a PDF into a series of images and extract text from it.
    """
    IMAGES_DIR = "./images"
    image_paths = pdf_to_image(pdf_path, output_path=IMAGES_DIR)
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
                                               x=data["coordinates"][0],
                                               y=data["coordinates"][1],
                                               width=data["coordinates"][2],
                                               height=data["coordinates"][3])
                    data_extracted[page][name]["image_path"] = sub_image_path
                    data_point_extracted = str(image_to_text(sub_image_path)) if data["art"] == "text" \
                        else extract_check_box(sub_image_path)
                    # implement check for language or handwriting
                    if type(data_point_extracted) is not bool:
                        if len(data_point_extracted) > 1:
                            data_point_extracted = curate_text(data_point_extracted)
                        else:
                            data_point_extracted = "No text found"

                    data_extracted[page][name]["data_extracted"] = data_point_extracted
    # convert data to pandas dataframe

    data_converted = []
    for page, data in data_extracted.items():
        for name, values in data.items():
            data_converted.append([page, name, values["data_extracted"]])
    data_extracted_df = pd.DataFrame(data_converted, columns=["page", "name", "data"])
    return data_extracted_df


if __name__ == "__main__":
    PDF_DIR_PATH = "/Users/levecq/private_repository/extract_data_pdf_proveg/data/"
    LIST_FILE_PATHS = glob(f"{PDF_DIR_PATH}/*.pdf")
    extract_data_dfs = [main(pdf_path=LIST_PATH)
                        for LIST_PATH in tqdm(LIST_FILE_PATHS,
                                              desc="Extracting data from PDFs")
                        ]
    df = pd.concat(extract_data_dfs)
    convert_data_model(df)
