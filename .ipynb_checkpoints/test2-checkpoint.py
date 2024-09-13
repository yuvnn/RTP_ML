from sklearn.cluster import DBSCAN
import numpy as np

# 예제 데이터 생성 (numpy 배열)
data = np.array([[1, 2], [2, 2], [2, 3],
                 [8, 7], [8, 8], [25, 80]])

# DBSCAN 객체 생성 및 클러스터링 수행
dbscan = DBSCAN(eps=3, min_samples=2)
dbscan.fit(data)

# 클러스터 레이블 출력
labels = dbscan.labels_
print(labels)
