from ultralytics import YOLO

if __name__ == "__main__":
	#epochs중 가장 뛰어난 성능의 가중치 불러오기
	model = YOLO("weights/obb/best.pt")
	results=model(source="eval_image.png",save=True)
	results[0].show()  # Display results	
	print(results[0].obb)