import os
import pandas as pd

# 파일 경로 설정
data_directory_path = "./output/SL preprocessing/dbs_intrp_output"

# 결합된 데이터프레임을 저장할 리스트 초기화
combined_data = []

# 연속되는 중복을 제거한 리스트 제작
def CollapseRecurringLabels(original_list):
    result_list = [original_list[0]]  
    for i in range(1, len(original_list)):
        if original_list[i] != original_list[i - 1]:
            result_list.append(original_list[i])
    return result_list

# 모든 파일에 대해 경로 처리
for file_name in os.listdir(data_directory_path):
    if file_name.endswith('.csv'):
        file_path = os.path.join(data_directory_path, file_name)
        df = pd.read_csv(file_path)
        
        # 연속되는 중복 제거
        labels = df['grid_label'].tolist()
        unique_labels = CollapseRecurringLabels(labels)
        
        # output 값에 따라 N 또는 AN 결정
        output_values = df['output'].tolist()
        if all(output == 'N' for output in output_values):
            F1_value = 'N'
        else:
            F1_value = 'AN'
        
        # 결합된 데이터 리스트에 추가
        combined_data.append({'F1': F1_value, 'grid_path': unique_labels })

# 리스트를 데이터프레임으로 변환
combined_dataframe = pd.DataFrame(combined_data)

# 최종 데이터프레임 CSV로 저장
output_file_path = r".\output\SL preprocessing\dbs_intrp_fin2.csv"
combined_dataframe.to_csv(output_file_path, index=False)

# 결과 출력
print(combined_dataframe)
