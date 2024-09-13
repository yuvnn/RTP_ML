import pandas as pd
import string
import os
import geopy.distance

# 위치(number)를 문자로 바꿔 그리드를 표기하기 위한 함수
def num_to_letter(num):
    '''
    숫자를 알파벳으로 변환하는 함수
    ex) num=0 -> A, num=1 -> B, ..., num=25 -> Z
    '''
    return string.ascii_uppercase[num]

# 경로가 그리드 안에 있는지 확인하는 함수
def is_path_in_grid(south, west, north, east, path_points):
    '''
    주어진 그리드 범위에 경로 포인트가 있는지 확인하는 함수
    '''
    return any(south <= lat <= north and west <= lng <= east for lat, lng in path_points)

# 해당 위치의 그리드를 설정하는 함수
def get_grid_label(lat, lng, final_grids):
    '''
    위도, 경도에 해당하는 그리드 레이블을 반환하는 함수
    '''
    for south, west, north, east, grid_label in final_grids:
        if south <= lat <= north and west <= lng <= east:
            return grid_label
    return None

# 대한민국 대략적인 경계
south_korea_bounds = [33.10, 124.57, 38.60, 131]

# 최소 그리드 크기 (km)
min_size_km = 0.76

# 그리드 생성 함수
def generate_initial_grids(bounds, grid_size=13):
    '''
    대한민국 영역을 초기 그리드로 나누는 함수
    '''
    south, west, north, east = bounds
    lat_step = (north - south) / grid_size
    lon_step = (east - west) / grid_size
    grid_queue = []

    for i in range(grid_size):
        for j in range(grid_size):
            grid_south = south + i * lat_step
            grid_north = south + (i + 1) * lat_step
            grid_west = west + j * lon_step
            grid_east = west + (j + 1) * lon_step
            grid_queue.append((grid_south, grid_west, grid_north, grid_east, num_to_letter(i) + num_to_letter(j)))

    return grid_queue

# 그리드 분할 함수
def subdivide_grids(grid_queue, path_points):
    '''
    그리드를 분할하는 함수
    '''
    final_grids = []
    subdivisions = ['A', 'B', 'C', 'D']

    while grid_queue:
        south, west, north, east, grid_label = grid_queue.pop(0)
        grid_size_km = min(geopy.distance.distance((south, west), (south, east)).km,
                           geopy.distance.distance((south, west), (north, west)).km)
        
        if grid_size_km > min_size_km and is_path_in_grid(south, west, north, east, path_points):
            # 그리드를 4개로 분할
            mid_lat = (south + north) / 2
            mid_lon = (west + east) / 2
            grid_queue.append((south, west, mid_lat, mid_lon, grid_label + 'C'))
            grid_queue.append((mid_lat, west, north, mid_lon, grid_label + 'A'))
            grid_queue.append((south, mid_lon, mid_lat, east, grid_label + 'D'))
            grid_queue.append((mid_lat, mid_lon, north, east, grid_label + 'B'))
        else:
            final_grids.append((south, west, north, east, grid_label))
    
    return final_grids

# 메인 처리 함수
def process_directory(dataset_path, labeled_data_path):
    '''
    주어진 경로의 CSV 파일들을 순회하며 그리드 레이블링을 처리하는 함수
    '''
    # 주어진 경로에 있는 CSV 파일들만 처리
    for filename in os.listdir(dataset_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(dataset_path, filename)
            labeled_data_file = os.path.join(labeled_data_path, filename)
            
            # CSV 파일 로드
            data = pd.read_csv(file_path, encoding='utf-8')
            path_points = data[['lat', 'lng']].values.tolist()

            # 초기 그리드 생성
            grid_queue = generate_initial_grids(south_korea_bounds)
            
            # 그리드 분할 및 최종 그리드 계산
            final_grids = subdivide_grids(grid_queue, path_points)

            # 각 경로 포인트에 그리드 레이블 할당
            data['grid_label'] = data.apply(lambda row: get_grid_label(row['lat'], row['lng'], final_grids), axis=1)
            
            # 결과를 CSV로 저장
            data.to_csv(labeled_data_file, index=False)

# 경로 설정
dataset_path = r"./output/어디쉐어/어디쉐어 dbscan_interpolate"
labeled_data_path = "./output/SL preprocessing/dbs_intrp_output"

# 결과 디렉토리 확인 및 생성
if not os.path.exists(labeled_data_path):
    os.makedirs(labeled_data_path)

# 데이터 처리 시작
process_directory(dataset_path, labeled_data_path)
