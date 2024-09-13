import pandas as pd
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt

# CSV 파일 읽기 (파일 경로를 적절히 변경하세요)
file_path = "C:/Users/yuvnn/Desktop/combined.csv"
data = pd.read_csv(file_path)

# 'lat', 'lng' 열 추출
coordinates = data[['lat', 'lng']]

# DBSCAN 클러스터링 수행
# eps와 min_samples 값은 데이터에 따라 조정이 필요합니다.
db = DBSCAN(eps=0.01, min_samples=700).fit(coordinates)

# 클러스터 라벨 추가
labels = db.labels_

# 결과 시각화
plt.figure(figsize=(10, 6))

# 이상치 (라벨 -1)
outliers = coordinates[labels == -1]
# 정상 데이터 (라벨 -1이 아닌 것)
core_samples = coordinates[labels != -1]

# 정상 데이터는 파란색으로, 이상치는 빨간색으로 표시
plt.scatter(core_samples['lng'], core_samples['lat'], c='blue', marker='o', label='Core Points')
plt.scatter(outliers['lng'], outliers['lat'], c='red', marker='o', label='Outliers')

plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('DBSCAN Clustering of Geographical Data')
plt.legend()
plt.show()
