import pprint

import cv2
import pdfplumber
from PIL import Image
from fpdf import FPDF


def merge_overlapping_boxes(boxes):
    """
    Merge overlapping bounding boxes into one that contains all overlapping boxes.
    This version uses a more relaxed criteria for overlap, considering any intersection.

    Parameters:
    boxes (list of tuples): List of bounding boxes represented as (x1, y1, x2, y2)

    Returns:
    list of tuples: List of merged bounding boxes
    """
    if not boxes:
        return []

    # Initialize merged_boxes with the first box
    merged_boxes = [boxes[0]]

    for current_box in boxes[1:]:
        x1, y1, x2, y2 = current_box
        merged = False

        # Iterate through existing merged_boxes to find potential overlaps
        for i, (prev_x1, prev_y1, prev_x2, prev_y2) in enumerate(merged_boxes):

            # Check for overlapping boxes using relaxed criteria
            if (x1 < prev_x2 and x2 > prev_x1) and (y1 < prev_y2 and y2 > prev_y1):
                # Merge boxes
                new_box = (
                    min(x1, prev_x1),
                    min(y1, prev_y1),
                    max(x2, prev_x2),
                    max(y2, prev_y2)
                )
                merged_boxes[i] = new_box
                merged = True
                break

        # If current_box didn't merge with any, add it to merged_boxes
        if not merged:
            merged_boxes.append(current_box)

    return merged_boxes


def extract_tables_from_pdf(pdf_path):
    table_settings = {
        "vertical_strategy": "text",
        "horizontal_strategy": "text",
        "snap_tolerance": 4,
    }

    table_data = {}  # Dictionary to store tables from each page
    with pdfplumber.open(pdf_path) as pdf:
        cropped_image_filenames = []

        for i, page in enumerate(pdf.pages):
            if i + 1 == 32:
                im = page.to_image(resolution=300)
                page_file_name = f"pg{i + 1}.png"
                im.save(page_file_name)

                # Load image (you'd convert your PDF page to an image first)
                image = cv2.imread(page_file_name)

                # Convert to grayscale and use edge detection
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 50, 150)

                # Find contours
                contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                bounding_boxes = []
                min_area = 5000
                # Filter and draw rectangles
                for contour in contours:
                    approx = cv2.approxPolyDP(contour, 0.05 * cv2.arcLength(contour, True), True)
                    if len(approx) == 4:  # Rectangle has 4 corners
                        area = cv2.contourArea(contour)
                        if area >= min_area:
                            x, y, w, h = cv2.boundingRect(contour)
                            bounding_boxes.append((x, y, x + w, y + h))

                bounding_boxes = merge_overlapping_boxes(bounding_boxes)

                pprint.pprint(bounding_boxes)
                print("---" * 20)
                for bbox_index, bbox in enumerate(bounding_boxes):
                    pprint.pprint(bbox)
                    x1, y1, x2, y2 = bbox
                    cropped_image = image[y1:y2, x1:x2]

                    # Convert the OpenCV image to PIL format for displaying
                    cropped_image_pil = Image.fromarray(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
                    cropped_image_path = f"pg{i + 1}_{bbox_index + 1}.png"
                    cropped_image_pil.save(cropped_image_path)

                    # Convert the OpenCV image to PIL format for displaying
                    cropped_image_pil = Image.fromarray(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
                    cropped_image_path = f"pg{i + 1}_bbox_{bbox_index + 1}.png"
                    cropped_image_pil.save(cropped_image_path)

                    cropped_image_filenames.append(cropped_image_path)

                print(f"total boxes: {len(bounding_boxes)}")

        create_pdf_from_images(cropped_image_filenames, "pdf_with_cropped_images.pdf")

        # # Attempt to extract a table from the current page
        # table_finder = page.debug_tablefinder(table_settings)
        # tables = table_finder.tables
        # j = 0
        #
        # for table in tables:
        #     j += 1
        #     bbox = table.bbox  # This should give you the bounding box
        #     cropped_page = page.crop(bbox)
        #
        #     cropped_table_finder = cropped_page.debug_tablefinder(table_settings)
        #     cropped_table = cropped_page.extract_table(table_settings)
        #
        #     im = cropped_page.to_image(resolution=300).debug_tablefinder(tf=cropped_table_finder)
        #     im.save(f"debug_table_pg{i+1}_{j}.png")
        #
        #     if cropped_table:
        #         # Convert the cropped_table into a DataFrame for easier manipulation
        #         df = pd.DataFrame(cropped_table[1:], columns=cropped_table[0])
        #         # Store the DataFrame in the dictionary
        #         table_data[f"Page_{i + 1}_{j}"] = df
        #
        #         # Print the DataFrame in a text format suitable for further NLP processing
        #         print(f"Table {j} found on Page {i + 1}:")
        #         print(df.to_string(index=False))
        #         print("---" * 20)
        # print(f"total tables: {len(tables)}")
    return table_data


def create_pdf_from_images(image_paths, output_pdf_path):
    pdf = FPDF()
    for image_path in image_paths:
        pdf.add_page()
        pdf.oversized_images = "DOWNSCALE"
        pdf.image(image_path, x=0, y=0, keep_aspect_ratio=True)
    pdf.output(output_pdf_path)
