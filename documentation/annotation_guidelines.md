# Image Annotation Guidelines

## 1. Objective

Create consistent object-level bounding-box annotations for a street-scene image dataset.

## 2. Supported Object Categories

- Person
- Car
- Bus
- Motorcycle
- Bicycle
- Traffic light

## 3. Bounding-Box Rules

1. Draw one bounding box per identifiable object.
2. Include the visible extent of the object.
3. Avoid unnecessary background.
4. Keep coordinates within the original image boundaries.
5. Do not combine multiple objects into one bounding box.
6. Annotate partially visible objects when their category can be confidently identified.

## 4. Occlusion Handling

Occlusion occurs when one object is partially or completely hidden by another.

- Partially visible objects should be annotated using their visible extent.
- Do not extend a bounding box across an occluding object to estimate hidden boundaries.
- Completely invisible objects should not be annotated.
- If the object's category cannot be identified confidently, exclude it and document the uncertainty.

## 5. Difficult Cases

- Overlapping pedestrians: create separate boxes for individually identifiable people.
- Pedestrians behind vehicles: annotate only visible, identifiable portions.
- Partially visible vehicles: annotate when the vehicle category remains clear.
- Small distant objects: annotate only when they can be identified reliably.

## 6. Quality Assurance

Every annotation should undergo:

- Coordinate validation.
- Category validation.
- Duplicate-box checks.
- Human visual inspection.
- Review of occluded and overlapping objects.

## 7. Annotation Format

Bounding boxes use XYXY pixel coordinates:

`[x_min, y_min, x_max, y_max]`

Coordinates refer to the original image dimensions.
