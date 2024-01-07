import os
import cv2
import numpy as np


def apply_cutout(image, mask_size):
    h, w, _ = image.shape
    mask = np.ones((h, w, 3), np.uint8)  # Change dtype to uint8
    y1 = np.random.randint(0, h - mask_size)
    y2 = y1 + mask_size
    x1 = np.random.randint(0, w - mask_size)
    x2 = x1 + mask_size
    mask[y1:y2, x1:x2, :] = 0
    image *= mask
    return image


def apply_hide_and_seek(image, num_regions, max_hidden_regions):
    h, w, _ = image.shape
    mask = np.ones((h, w, 3), np.float32)
    for _ in range(np.random.randint(1, max_hidden_regions + 1)):
        y1 = np.random.randint(0, h)
        y2 = np.random.randint(y1 + 1, h + 1)
        x1 = np.random.randint(0, w)
        x2 = np.random.randint(x1 + 1, w + 1)
        mask[y1:y2, x1:x2, :] = 0
    image *= mask
    return image

def apply_grid_mask(image, num_grid_cells):
    h, w, _ = image.shape
    cell_size = h // num_grid_cells
    mask = np.random.choice([0, 1], size=(num_grid_cells, num_grid_cells), p=[0.5, 0.5])
    mask = np.repeat(mask, cell_size, axis=0)
    mask = np.repeat(mask, cell_size, axis=1)
    mask = np.expand_dims(mask, axis=2)
    
    mask = mask.astype(np.uint8)  # Convert the mask to dtype uint8
    
    image *= mask
    return image


def apply_mixup(image1, image2, label1, label2, alpha):
    blended_image = alpha * image1 + (1 - alpha) * image2
    blended_label = alpha * label1 + (1 - alpha) * label2
    return blended_image, blended_label

def apply_cutmix(image1, image2, label1, label2, alpha):
    h, w, _ = image1.shape
    cut_h = int(h * np.sqrt(1 - alpha))
    cut_w = int(w * np.sqrt(1 - alpha))
    y = np.random.randint(0, h - cut_h)
    x = np.random.randint(0, w - cut_w)
    cut_image = image2[y:y + cut_h, x:x + cut_w]
    cut_label = label2
    mixed_image = image1.copy()
    mixed_image[y:y + cut_h, x:x + cut_w] = cut_image
    mixed_label = alpha * label1 + (1 - alpha) * cut_label
    return mixed_image, mixed_label


# Create a new directory for saving augmented images
augmented_image_dir = "augmented_images/"
augmented_labels_dir = "augmented_labels/"
os.makedirs(augmented_image_dir, exist_ok=True)
os.makedirs(augmented_labels_dir, exist_ok=True)

# Paths to your image and label directories
image_dir = "val/images/"
label_dir = "val/labels/"

# List all image files in the directory
image_files = os.listdir(image_dir)
label_files = os.listdir(label_dir)

# Loop through each image and its corresponding label
for image_file in image_files:
    if image_file.endswith(".jpg"):
        image_path = os.path.join(image_dir, image_file)
        label_file = image_file.replace(".jpg", ".txt")
        label_path = os.path.join(label_dir, label_file)

        # Load the image and its corresponding label
        image = cv2.imread(image_path)
        with open(label_path, "r") as f:
            lines = f.readlines()
        annotations = []
        for line in lines:
            parts = line.strip().split()
            class_id = int(parts[0])
            xmin, ymin, xmax, ymax = map(float, parts[1:])
            annotations.append([xmin, ymin, xmax, ymax, class_id])

        # Apply augmentations
        augmented_images = []
        augmented_annotations = []
        for i in range(10):  # Adjust num_augmentations as needed

            # Apply augmentation techniques here
            augmented_image = apply_cutout(image.copy(), 150)


            # ... apply other augmentation techniques ...
            augmented_images.append(augmented_image)
            augmented_annotations.append(annotations)

            # Save the augmented image
            augmented_image_filename = f"{os.path.splitext(image_file)[0]}_augmented_co_{i}.jpg"
            augmented_image_path = os.path.join(augmented_image_dir, augmented_image_filename)
            cv2.imwrite(augmented_image_path, augmented_image)

            # Save the corresponding label (assuming it remains unchanged after augmentation)
            augmented_label_filename = f"{os.path.splitext(label_file)[0]}_augmented_co_{i}.txt"
            augmented_label_path = os.path.join(augmented_labels_dir, augmented_label_filename)
            with open(augmented_label_path, "w") as f:
                for ann in annotations:
                    class_id = ann[4]
                    xmin, ymin, xmax, ymax = map(str, ann[:4])
                    line = f"{class_id} {xmin} {ymin} {xmax} {ymax}\n"
                    f.write(line)
