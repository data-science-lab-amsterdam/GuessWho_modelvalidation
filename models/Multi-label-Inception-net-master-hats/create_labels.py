import glob
import os

# Link to directories; 
labels_dir = "image_labels_dir" # where we want labels
image_dir = "image_files/" # Where we have images

# Find the categories
categories = glob.glob(image_dir+"*")
categories = [x.replace(image_dir,'') for x in categories]
print("Categories are: ", categories)

# Create folder if it doesnt exist
if not os.path.exists(labels_dir):
	os.makedirs(labels_dir)

# per category make text file with same name of file + ".png.txt" and write category
for category in categories:
	image_names = glob.glob(image_dir+category+"/*")
	image_names = [x.replace(image_dir+category+"/",'') for x in image_names]
	print("Total in this category are: {} {}".format(len(image_names), category))

	# For every image in this category create a text file
	for image in image_names:
		filepath = os.path.join(labels_dir, image)
		try:
			f = open(filepath+".txt", 'w')
			f.write(category)
			f.close()
		except:
			print("Path is Incorrect")