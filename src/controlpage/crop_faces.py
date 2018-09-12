import os
import sys
import glob
import face_recognition
from skimage import io

""" 
insert input directory and output directory
python python crop_faces.py "./images/full" "./images/test"
"""


def crop_image(img, area, padding=0):
    """
    Crop image to relevant area
    """
    (x, y, w, h) = area
    assert w > 50 and h > 50, "Area too small to crop!"

    padding_px = round(padding * w)
    x1 = x - padding_px
    y1 = y - round(2.6*padding_px)  # extra padding to the top, to see some space above the head
    x2 = x + w + padding_px
    y2 = y + h + round(2*padding_px)
    height, width, channels = img.shape
    # The padding is necessary since the OpenCV face detector creates the bounding box around the face and not the head
    cropped_image = img[max(0, y1):min(height, y2), max(0, x1):min(width, x2)]
    return cropped_image


def crop_images(input_dir, output_dir):
    if output_dir is None:
        output_dir = input_dir

    if not os.path.exists(output_dir):
        os.system("mkdir {}".format(output_dir))

    print("Reading images from '{}'".format(input_dir))
    print("Writing images to '{}'".format(output_dir))

    # load all the images of people to recognize into the database
    for filename in glob.glob(os.path.join(input_dir, '*.JPG')):
        print("Processing image: {}".format(filename))
        # load image
        image_rgb = face_recognition.load_image_file(filename)

        # run the face detection model to find face locations
        try:
            face_location = face_recognition.face_locations(image_rgb)[0]
            (top, right, bottom, left) = face_location
            area = (left, top, bottom-top, right-left)
            cropped_image = crop_image(image_rgb, area, padding=0.25)
        except Exception as e:
            print("Error during cropping to face. Using original image.")
            print(e)
            cropped_image = image_rgb

        name, ext = os.path.splitext(os.path.basename(filename))
        filename_out = os.path.join(output_dir, '{}{}'.format(name, ext))
        io.imsave(filename_out, cropped_image)


if __name__ == '__main__':
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    crop_images(input_dir, output_dir)