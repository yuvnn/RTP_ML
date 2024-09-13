import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.mixture import GaussianMixture
from scipy.interpolate import interp1d

# CSV 파일에서 경로 데이터를 추출하는 함수
def extract_lat_lng_from_csv(directory):
    all_lat_lng_lists = []
    
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            filepath = os.path.join(directory, filename)
            df = pd.read_csv(filepath)
            lat_lng_list = [(row['lat'], row['lng']) for index, row in df.iterrows()]
            all_lat_lng_lists.append(lat_lng_list)
    
    return all_lat_lng_lists

# 경로 데이터를 보간하여 동일한 길이로 만드는 함수
def interpolate_path(path, num_points=10):
    latitudes = [point[0] for point in path]
    longitudes = [point[1] for point in path]
    distances = np.linspace(0, 1, len(path))
    interp_lat = interp1d(distances, latitudes, kind='linear')
    interp_lon = interp1d(distances, longitudes, kind='linear')
    new_distances = np.linspace(0, 1, num_points)
    new_latitudes = interp_lat(new_distances)
    new_longitudes = interp_lon(new_distances)
    return np.column_stack((new_latitudes, new_longitudes)).flatten()

# 경로 데이터를 읽어오는 경로 설정
directory_path = "C:/Users/ohsan/Documents/연구실/01 rtp/___ecfd1086a6934ae08b555b3ae880d31e" 
lat_lng_values = extract_lat_lng_from_csv(directory_path)

# 보간된 경로 벡터들
path_vectors = np.array([interpolate_path(path) for path in lat_lng_values])

# GMM 학습
gmm = GaussianMixture(n_components=2, covariance_type='full')
gmm.fit(path_vectors)

# 로그 가능도 계산
log_likelihoods = gmm.score_samples(path_vectors)

# 로그 가능도의 평균 계산
mean_log_likelihood = np.mean(log_likelihoods)

print(f"Mean Log Likelihood: {mean_log_likelihood}")

# 이상치 판단
threshold = mean_log_likelihood - 2 * np.std(log_likelihoods)  # 평균 - 2표준편차: 약 95%의 데이터 포인트
outliers = log_likelihoods < threshold

# 이상 경로 출력
def print_anomalies(paths, outliers):
    for i, is_outlier in enumerate(outliers):
        if is_outlier:
            print(f"Anomalous Path {i+1}: {paths[i]}")

print("이상경로\n")
print_anomalies(lat_lng_values, outliers)

# 시각화
fig, ax = plt.subplots()
for i, path in enumerate(lat_lng_values):
    latitudes = [point[1] for point in path]
    longitudes = [point[0] for point in path]
    if outliers[i]:
        ax.plot(latitudes, longitudes, 'r', marker='o', label='Outlier' if i == 0 else "")
    else:
        ax.plot(latitudes, longitudes, 'b', marker='o', label='Normal' if i == 0 else "")

# 레이블 추가
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title('User Paths with Outlier Detection')
ax.legend()
plt.show()
