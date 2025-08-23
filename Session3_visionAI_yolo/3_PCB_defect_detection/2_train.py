from ultralytics import YOLO

if __name__ == '__main__':
    # Load a model
	model = YOLO("yolo11n.yaml").load("yolo11n.pt")  # build from YAML and transfer weights
	# Train the model
	model.train(data="datasets/data.yaml", epochs=100, imgsz=640, device='cuda')
	#model.train(data="datasets/data.yaml", epochs=3, imgsz=640, device='cpu')
	# Test the model
	results = model("datasets/images/test/04_spur_19.jpg")
	results[0].show()