pose = [0.30, -0.20, 0.25, 0.0, 3.14, 0.0]


# TODO: pose의 z에 dz를 더해서 돌려주는 함수 만들기
def move_up(pose, dz):
    pose[2] = pose[2] + dz
    return pose


print(move_up(pose, 0.05))
