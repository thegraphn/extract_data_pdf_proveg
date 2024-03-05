from collections import defaultdict
from utils import pdf_to_image, cut_image, image_to_text, curate_text, extract_check_box
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
                                               x=data["coordinates"][0],
                                               y=data["coordinates"][1],
                                               width=data["coordinates"][2],
                                               height=data["coordinates"][3])
                    data_extracted[page][name]["image_path"] = sub_image_path
                    data_point_extracted = str(image_to_text(sub_image_path)) if data["art"] == "text"\
                        else extract_check_box(sub_image_path)
                    # implement check for language or handwriting
                    if type(data_point_extracted) is not bool:
                        if len(data_point_extracted) > 1:
                            data_point_extracted = curate_text(data_point_extracted)
                        else:
                            data_point_extracted = "No text found"

                    data_extracted[page][name]["data_extracted"] = data_point_extracted

    print(data_extracted)
    # convert data to pandas dataframe
    import pandas as pd
    data_converted = []
    for page, data in data_extracted.items():
        for name, values in data.items():
            data_converted.append([page, name, values["data_extracted"]])
    df = pd.DataFrame(data_converted, columns=["page", "name", "data"])
    df.to_csv(csv_output_path, index=False)
    print(df)


if __name__ == "__main__":
    PDF_PATH = "/Users/levecq/private_repository/extract_data_pdf_proveg/data/muster-prufformular.pdf"
    main(pdf_path=PDF_PATH, csv_output_path="output.csv")
