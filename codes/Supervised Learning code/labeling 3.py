import pandas as pd
import string
import os
import geopy.distance
import folium

# 대한민국 대략적인 경계
south_korea_bounds = [33.10, 124.57, 38.60, 131]

# 최소 그리드 크기 (km)
min_size_km = 0.76

# 위치(number)를 문자로 바꿔 그리드를 표기하기 위한 함수
def num_to_letter(num):
    return string.ascii_uppercase[num]

# 경로가 그리드 안에 있는지 확인하는 함수
def is_path_in_grid(south, west, north, east, path_points):
    return any(south <= lat <= north and west <= lng <= east for lat, lng in path_points)

# 해당 위치의 그리드를 설정하는 함수
def get_grid_label(lat, lng, final_grids):
    for south, west, north, east, grid_label in final_grids:
        if south <= lat <= north and west <= lng <= east:
            return grid_label
    return None

# 그리드 생성 함수
def generate_initial_grids(bounds, grid_size=13):
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
    final_grids = []
    subdivisions = ['A', 'B', 'C', 'D']

    while grid_queue:
        south, west, north, east, grid_label = grid_queue.pop(0)
        grid_size_km = min(geopy.distance.distance((south, west), (south, east)).km,
                           geopy.distance.distance((south, west), (north, west)).km)
        
        if grid_size_km > min_size_km and is_path_in_grid(south, west, north, east, path_points):
            mid_lat = (south + north) / 2
            mid_lon = (west + east) / 2
            grid_queue.append((south, west, mid_lat, mid_lon, grid_label + 'C'))
            grid_queue.append((mid_lat, west, north, mid_lon, grid_label + 'A'))
            grid_queue.append((south, mid_lon, mid_lat, east, grid_label + 'D'))
            grid_queue.append((mid_lat, mid_lon, north, east, grid_label + 'B'))
        else:
            final_grids.append((south, west, north, east, grid_label))
    
    return final_grids

# 단일 파일 처리 함수
def process_single_file(file_path, output_path, output_html_path):
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
    data.to_csv(output_path, index=False)
    
    # 시각화 및 HTML 파일 저장
    visualize_path_with_grids(data, final_grids, output_html_path)

# 지도에 경로와 그리드 레이블을 시각화하는 함수
def visualize_path_with_grids(data, final_grids, output_html_path):
    # 지도 생성
    m = folium.Map(location=[(south_korea_bounds[0] + south_korea_bounds[2]) / 2,
                             (south_korea_bounds[1] + south_korea_bounds[3]) / 2],
                   zoom_start=7)

    # 경로 포인트 지도에 추가
    points = data[['lat', 'lng']].values.tolist()
    folium.PolyLine(points, color='red', weight=2.5, opacity=1).add_to(m)

    # 그리드 시각화
    for south, west, north, east, grid_label in final_grids:
        folium.Rectangle(
            bounds=[[south, west], [north, east]],
            color='#0000FF',
            fill=True,
            fill_opacity=0.1
        ).add_to(m)
        
        # 그리드 중앙에 레이블 추가
        folium.Marker(
            location=[(south + north) / 2, (west + east) / 2],
            icon=folium.DivIcon(html=f'<div style="font-size: 8pt; color: yellow;">{grid_label}</div>')
        ).add_to(m)

    # 지도를 HTML 파일로 저장
    m.save(output_html_path)

# 경로 설정
dataset_path = r"C:\Users\NetDB\Desktop\RTP2\IF\anomaly_score.csv"
labeled_data_path = os.path.join(os.path.dirname(dataset_path))

# 결과 디렉토리 확인 및 생성
if not os.path.exists(labeled_data_path):
    os.makedirs(labeled_data_path)

# 처리할 파일 경로 설정
output_file_path = os.path.join(labeled_data_path, 'anomaly_score_labeled.csv')
output_html_path = os.path.join(labeled_data_path, 'anomaly_score_map.html')

# 단일 파일 처리 시작
process_single_file(dataset_path, output_file_path, output_html_path)

