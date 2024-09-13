import os
import pandas as pd

# 현재 작업 디렉터리 경로 설정
directory_path = os.getcwd()
data_directory_path = os.path.join(directory_path, 'labeling')
output_file_path = os.path.join(directory_path, 'combined_output.csv')

# 연속되는 중복을 제거한 리스트 제작
def CollapseRecurringLabels(original_list, dbscan_list):
    result_list = [original_list[0]]
    result_dbscan = [dbscan_list[0]]
    for i in range(1, len(original_list)):
        if original_list[i] != original_list[i - 1]:
            result_list.append(original_list[i])
            result_dbscan.append(dbscan_list[i])
    return result_list, result_dbscan

combined_data = []

# 각 CSV 파일에서 grid_label과 dbscan_output 컬럼 추출 및 중복 제거
for file_name in os.listdir(data_directory_path):
    if file_name.endswith('.csv.csv'):
        file_path = os.path.join(data_directory_path, file_name)
        df = pd.read_csv(file_path)
        
        # 'grid_label'과 'dbscan_output' 칼럼만 추출
        labels = df['grid_label'].tolist()
        dbscan_outputs = df['dbscan output'].tolist()
        
        # 중복 제거
        unique_labels, unique_dbscan_outputs = CollapseRecurringLabels(labels, dbscan_outputs)
        
        # dbscan_output 값을 N 또는 AN으로 변환
        converted_dbscan_outputs = ['N' if output == 1 else 'AN' for output in unique_dbscan_outputs]
        
        # 중복 제거된 결과를 combined_data에 추가
        for label, converted_output in zip(unique_labels, converted_dbscan_outputs):
            combined_data.append({'grid_label': label, 'dbscan_output': converted_output})

# 결과를 데이터프레임으로 변환
combined_df = pd.DataFrame(combined_data)

# 결과를 CSV 파일로 저장
combined_df.to_csv(output_file_path, index=False)

print(f"Combined data has been saved to {output_file_path}")
