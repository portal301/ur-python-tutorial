from ultralytics import YOLO

if __name__ == '__main__':
    # Load a model
	model = YOLO("yolo11n.yaml").load("runs/detect/train/weights/best.pt")  # build from YAML and transfer weights
	# Train the model
	results = model("image/ex1.png")
	results[0].show()