
pick and place - v7 2025-08-04 2:25am
==============================

This dataset was exported via roboflow.com on August 3, 2025 at 5:25 PM GMT

Roboflow is an end-to-end computer vision platform that helps you
* collaborate with your team on computer vision projects
* collect & organize images
* understand and search unstructured image data
* annotate, and create datasets
* export, train, and deploy computer vision models
* use active learning to improve your dataset over time

For state of the art Computer Vision training notebooks you can use with this dataset,
visit https://github.com/roboflow/notebooks

To find over 100k other datasets and pre-trained models, visit https://universe.roboflow.com

The dataset includes 256 images.
Objects are annotated in YOLOv8 Oriented Object Detection format.

The following pre-processing was applied to each image:
* Resize to 1024x1024 (Fill (with center crop))

The following augmentation was applied to create 3 versions of each source image:
* Equal probability of one of the following 90-degree rotations: none, clockwise, counter-clockwise, upside-down
* Random rotation of between -10 and +10 degrees
* Random brigthness adjustment of between -25 and +25 percent


