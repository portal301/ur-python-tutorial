from ultralytics import YOLO

if __name__ == "__main__":
	#가중치가 pretrain된 yolo11n 모델을 불러옵니다.
	#model = YOLO("yolo11n.pt")
	
	#비어있는 yolo11n 모델을 생성합니다.
	model = YOLO("yolo11n.yaml") 

	#비어있는 yolo11n 모델을 생성한 후, 모델을 불러옵니다.
	#model = YOLO("yolo11n.yaml").load("yolo11n.pt") 

	results=model(source="image/dog.png",save=True)
	results[0].show()  # Display results