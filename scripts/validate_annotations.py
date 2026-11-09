
import json
import os
from collections import Counter

JSON_PATH = "annotations/annotations.json"
IMAGE_PATH = "images/original/nairobi_street.jpg"

ALLOWED_CLASSES = {
    "person",
    "car",
    "bus",
    "motorcycle",
    "bicycle",
    "traffic_light"
}


def validate():
    if not os.path.exists(JSON_PATH):
        print("ERROR: Annotation JSON not found.")
        return

    if not os.path.exists(IMAGE_PATH):
        print("ERROR: Original image not found.")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    width = data["image_width"]
    height = data["image_height"]
    annotations = data["annotations"]

    errors = []
    warnings = []
    ids = set()
    boxes = set()
    categories = Counter()

    for index, item in enumerate(annotations, start=1):
        annotation_id = item.get("id")
        category = item.get("category")
        bbox = item.get("bbox")

        if annotation_id in ids:
            errors.append(f"Annotation {index}: Duplicate ID.")

        ids.add(annotation_id)

        if category not in ALLOWED_CLASSES:
            errors.append(
                f"Annotation {index}: Unknown category {category}."
            )
        else:
            categories[category] += 1

        if not isinstance(bbox, list) or len(bbox) != 4:
            errors.append(
                f"Annotation {index}: Invalid bounding box format."
            )
            continue

        if not all(isinstance(v, (int, float)) for v in bbox):
            errors.append(
                f"Annotation {index}: Coordinates must be numeric."
            )
            continue

        x1, y1, x2, y2 = bbox

        if not (0 <= x1 < x2 <= width):
            errors.append(
                f"Annotation {index}: Invalid horizontal coordinates."
            )

        if not (0 <= y1 < y2 <= height):
            errors.append(
                f"Annotation {index}: Invalid vertical coordinates."
            )

        if (x2 - x1) < 5 or (y2 - y1) < 5:
            errors.append(
                f"Annotation {index}: Bounding box is too small."
            )

        box_key = tuple(bbox)

        if box_key in boxes:
            warnings.append(
                f"Annotation {index}: Duplicate bounding box."
            )

        boxes.add(box_key)

    print("\n========== ANNOTATION QA REPORT ==========")
    print("Image:", data.get("image"))
    print(f"Dimensions: {width} x {height}")
    print("Total annotations:", len(annotations))

    print("\nCATEGORY DISTRIBUTION")

    for category, count in sorted(categories.items()):
        print(f"{category}: {count}")

    print("\nVALIDATION RESULTS")
    print("Errors:", len(errors))
    print("Warnings:", len(warnings))

    if errors:
        print("\nERROR DETAILS")
        for error in errors:
            print("-", error)

    if warnings:
        print("\nWARNING DETAILS")
        for warning in warnings:
            print("-", warning)

    if not errors:
        print("\nSTRUCTURAL VALIDATION: PASSED")
    else:
        print("\nSTRUCTURAL VALIDATION: FAILED")

    print("\nNote: Automated checks cannot verify visual")
    print("accuracy. Human review is still required.")

    print("==========================================\n")


if __name__ == "__main__":
    validate()
