from ultralytics import YOLO

if __name__ == '__main__':
    # Load a model
	model = YOLO("yolo11n-cls.yaml").load("yolo11n-cls.pt")  # build from YAML and transfer weights
	# Train the model
	model.train(data="datasets", epochs=50, imgsz=320, device=0)
	