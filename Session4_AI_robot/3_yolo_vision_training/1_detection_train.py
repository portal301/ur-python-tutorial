from ultralytics import YOLO

if __name__ == "__main__":
	# Load a pretrained YOLO11n model
	model = YOLO("yolo11n.yaml").load("yolo11n.pt")

	model.train(data="datasets/detection/data.yaml", epochs=3, imgsz=640, device=0)

	results=model(source="eval_image.png",save=True)
	results[0].show()  # Display results

	path = model.export(format="onnx")  # Returns the path to the exported model