"""
Main script to extract data from PDFs.
"""
import os.path
from glob import glob
from collections import defaultdict
import pandas as pd
from tqdm import tqdm
from utils import (pdf_to_image, cut_image, image_to_text,
                   correct_text, extract_check_box, convert_data_model)
from config import sub_images_coordinates


def main(pdf_path: str, local_tmp_image_dir: str) -> pd.DataFrame:
    """
    Convert a PDF into a series of images and extract text from it.
    """

    image_paths = pdf_to_image(pdf_path, output_path=local_tmp_image_dir)
    # create the sub images containing the data to extract
    data_extracted = defaultdict(dict)
    for image_path in image_paths:
        for page, coordinate_data in sub_images_coordinates.items():
            if page not in data_extracted:
                data_extracted[page] = {}
            if page in image_path:
                for name, data in coordinate_data.items():
                    data_extracted[page][name] = {"image_path": "", "data_extracted": ""}
                    sub_image_path = cut_image(
                        image_path=image_path,
                        output_path=os.path.join(local_tmp_image_dir, f"./{page}_{name}.png"),
                        x=data["coordinates"][0],
                        y=data["coordinates"][1],
                        width=data["coordinates"][2],
                        height=data["coordinates"][3]
                    )
                    data_extracted[page][name]["image_path"] = sub_image_path
                    data_point_extracted = str(image_to_text(sub_image_path)) \
                        if data["art"] == "text" \
                        else extract_check_box(sub_image_path)
                    # implement check for language or handwriting
                    if not isinstance(data_point_extracted, bool):
                        if len(data_point_extracted) > 1:
                            data_point_extracted = correct_text(data_point_extracted)
                        else:
                            data_point_extracted = "No text found"

                    data_extracted[page][name]["data_extracted"] = data_point_extracted
    # convert data to pandas dataframe
    data_converted = []
    for page, data in data_extracted.items():
        for name, values in data.items():
            data_converted.append([page, name, values["data_extracted"]])
    data_extracted_df = pd.DataFrame(data_converted, columns=["page", "name", "data"])
    data_extracted_df["document_path"] = pdf_path
    # delete the temporary folder
    image_to_delete = glob(f"{local_tmp_image_dir}/*.png")
    for image_path in image_to_delete:
        os.remove(image_path)
    os.rmdir(local_tmp_image_dir)

    return data_extracted_df


if __name__ == "__main__":
    PDF_DIR_PATH = "/Users/levecq/private_repository/extract_data_pdf_proveg/data/"
    LIST_FILE_PATHS = glob(f"{PDF_DIR_PATH}/*.pdf")
    extract_data_dfs = [main(pdf_path=LIST_PATH, local_tmp_image_dir="./tmp")
                        for LIST_PATH in tqdm(LIST_FILE_PATHS,
                                              desc=f"Extracting data from PDFs in {PDF_DIR_PATH}...")
                        ]
    df = pd.concat(extract_data_dfs)
    df = convert_data_model(df)
    df.to_csv("extracted_data.csv", index=False)
