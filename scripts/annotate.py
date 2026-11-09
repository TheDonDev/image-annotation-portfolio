
import cv2
import json
import os
from datetime import datetime

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

IMAGE_PATH = "images/original/nairobi_street.jpg"
OUTPUT_IMAGE = "images/annotated/nairobi_street_annotated.jpg"
OUTPUT_JSON = "annotations/annotations.json"

CLASSES = {
    ord("1"): "person",
    ord("2"): "car",
    ord("3"): "bus",
    ord("4"): "motorcycle",
    ord("5"): "bicycle",
    ord("6"): "traffic_light"
}

WINDOW = "Image Annotation Tool"

# --------------------------------------------------
# LOAD ORIGINAL IMAGE
# --------------------------------------------------

image = cv2.imread(IMAGE_PATH)

if image is None:
    raise FileNotFoundError(
        f"Cannot load image: {IMAGE_PATH}"
    )

height, width = image.shape[:2]

# Resize for display while preserving original coordinates.
scale = min(1000 / width, 700 / height, 1.0)

display_width = int(width * scale)
display_height = int(height * scale)

# --------------------------------------------------
# LOAD EXISTING ANNOTATIONS
# --------------------------------------------------

if os.path.exists(OUTPUT_JSON):

    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        existing_data = json.load(f)

    # Confirm that annotations belong to this image.
    if existing_data.get("image") != os.path.basename(IMAGE_PATH):
        raise ValueError(
            "The existing annotation file belongs to a different image."
        )

    if (
        existing_data.get("image_width") != width
        or existing_data.get("image_height") != height
    ):
        raise ValueError(
            "Existing annotation dimensions do not match the original image."
        )

    annotations = existing_data.get("annotations", [])

    print(
        f"\nSuccessfully loaded {len(annotations)} existing annotations."
    )

else:
    annotations = []
    print("\nNo existing annotations found. Starting a new project.")

# --------------------------------------------------
# VALIDATE EXISTING ANNOTATION IDs
# --------------------------------------------------

existing_ids = [
    item.get("id") for item in annotations
]

if (
    any(not isinstance(item_id, int) or isinstance(item_id, bool)
        for item_id in existing_ids)
    or len(existing_ids) != len(set(existing_ids))
):
    raise ValueError(
        "Existing annotation IDs are invalid or duplicated. "
        "Please inspect your JSON file before continuing."
    )

# --------------------------------------------------
# DRAWING STATE
# --------------------------------------------------

drawing = False
start_point = None
pending_box = None

# --------------------------------------------------
# SAVE ANNOTATIONS
# --------------------------------------------------

def save_annotations():

    os.makedirs("annotations", exist_ok=True)
    os.makedirs("images/annotated", exist_ok=True)

    data = {
        "image": os.path.basename(IMAGE_PATH),
        "image_width": width,
        "image_height": height,
        "annotation_format": "xyxy_pixel_coordinates",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "annotations": annotations
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    # Create annotated image from original image.
    result = image.copy()

    for item in annotations:

        x1, y1, x2, y2 = item["bbox"]

        cv2.rectangle(
            result,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            5
        )

        cv2.putText(
            result,
            f'{item["category"]} #{item["id"]}',
            (x1, max(y1 - 12, 30)),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 255, 0),
            3
        )

    success = cv2.imwrite(OUTPUT_IMAGE, result)

    if not success:
        raise IOError(
            f"Could not save annotated image: {OUTPUT_IMAGE}"
        )

    print(
        f"Saved successfully: {len(annotations)} annotations."
    )

# --------------------------------------------------
# REDRAW ANNOTATION WINDOW
# --------------------------------------------------

def redraw():

    canvas = image.copy()

    # Draw all existing annotations.
    for item in annotations:

        x1, y1, x2, y2 = item["bbox"]

        cv2.rectangle(
            canvas,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            4
        )

        cv2.putText(
            canvas,
            f'{item["category"]} #{item["id"]}',
            (x1, max(y1 - 10, 25)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

    # Draw the pending annotation in blue.
    if pending_box is not None:

        x1, y1, x2, y2 = pending_box

        cv2.rectangle(
            canvas,
            (x1, y1),
            (x2, y2),
            (255, 0, 0),
            4
        )

    display = cv2.resize(
        canvas,
        (display_width, display_height)
    )

    instructions = (
        "Draw box | 1-6: label | U: undo | S: save | Q: quit"
    )

    cv2.putText(
        display,
        instructions,
        (10, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 0, 255),
        2
    )

    cv2.imshow(WINDOW, display)

# --------------------------------------------------
# MOUSE CALLBACK
# --------------------------------------------------

def mouse_callback(event, x, y, flags, param):

    global drawing, start_point, pending_box

    if event == cv2.EVENT_LBUTTONDOWN:

        if pending_box is not None:
            print(
                "Label or cancel the previous box first."
            )
            return

        drawing = True
        start_point = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE and drawing:

        redraw()

        preview = cv2.resize(
            image.copy(),
            (display_width, display_height)
        )

        cv2.rectangle(
            preview,
            start_point,
            (x, y),
            (255, 0, 0),
            2
        )

        cv2.imshow(WINDOW, preview)

    elif event == cv2.EVENT_LBUTTONUP and drawing:

        drawing = False

        x1 = min(start_point[0], x)
        y1 = min(start_point[1], y)

        x2 = max(start_point[0], x)
        y2 = max(start_point[1], y)

        # Reject extremely small boxes on the display.
        if x2 - x1 < 3 or y2 - y1 < 3:

            print("Box too small. Try again.")
            redraw()
            return

        # Convert display coordinates to original image coordinates.
        x1 = round(x1 / scale)
        y1 = round(y1 / scale)

        x2 = round(x2 / scale)
        y2 = round(y2 / scale)

        # Keep coordinates within image boundaries.
        pending_box = [
            max(0, min(x1, width - 1)),
            max(0, min(y1, height - 1)),
            max(0, min(x2, width - 1)),
            max(0, min(y2, height - 1))
        ]

        # Check box dimensions in original pixels.
        if (
            pending_box[2] - pending_box[0] < 5
            or pending_box[3] - pending_box[1] < 5
        ):

            print("Box too small in original image. Try again.")
            pending_box = None
            redraw()
            return

        print("\nBounding box created:", pending_box)

        print(
            "Press the corresponding number in the IMAGE WINDOW "
            "to assign a category."
        )

        redraw()

# --------------------------------------------------
# MAIN ANNOTATION FUNCTION
# --------------------------------------------------

def main():

    global pending_box

    cv2.namedWindow(
        WINDOW,
        cv2.WINDOW_AUTOSIZE
    )

    cv2.setMouseCallback(
        WINDOW,
        mouse_callback
    )

    print("\n========== IMAGE ANNOTATION TOOL ==========")

    print(f"Image dimensions: {width} x {height}")

    print(f"Existing annotations: {len(annotations)}")

    print("\nCATEGORIES")

    print("1 = person")
    print("2 = car")
    print("3 = bus")
    print("4 = motorcycle")
    print("5 = bicycle")
    print("6 = traffic_light")

    print("\nCONTROLS")

    print("Draw a box using your mouse.")
    print("Press 1-6 in the IMAGE WINDOW to assign a label.")
    print("U = undo the last annotation.")
    print("S = save annotations.")
    print("Q = save and quit.")
    print("ESC = cancel the pending box.")

    print("\nAnnotations autosave after every label.")

    print("===========================================\n")

    # Display all previously saved annotations.
    redraw()

    while True:

        key = cv2.waitKey(20) & 0xFF

        # ------------------------------------------
        # ASSIGN CATEGORY
        # ------------------------------------------

        if key in CLASSES and pending_box is not None:

            category = CLASSES[key]

            next_id = max(
                (item["id"] for item in annotations),
                default=0
            ) + 1

            new_annotation = {
                "id": next_id,
                "category": category,
                "bbox": pending_box
            }

            annotations.append(new_annotation)

            print(
                f"Added annotation #{next_id}: "
                f"{category} {pending_box}"
            )

            pending_box = None

            save_annotations()
            redraw()

        # ------------------------------------------
        # UNDO LAST ANNOTATION
        # ------------------------------------------

        elif key == ord("u"):

            if pending_box is not None:

                pending_box = None

                print("Pending box cancelled.")

            elif annotations:

                removed = annotations.pop()

                print(
                    f"Removed annotation #{removed['id']}: "
                    f"{removed['category']}"
                )

                save_annotations()

            else:

                print("There are no annotations to undo.")

            redraw()

        # ------------------------------------------
        # SAVE
        # ------------------------------------------

        elif key == ord("s"):

            save_annotations()

        # ------------------------------------------
        # CANCEL PENDING BOX
        # ------------------------------------------

        elif key == 27:

            pending_box = None

            print("Pending box cancelled.")

            redraw()

        # ------------------------------------------
        # SAVE AND QUIT
        # ------------------------------------------

        elif key == ord("q"):

            save_annotations()

            print("\nAnnotation session completed.")

            break

    cv2.destroyAllWindows()


# --------------------------------------------------
# RUN PROGRAM
# --------------------------------------------------

if __name__ == "__main__":

    main()
