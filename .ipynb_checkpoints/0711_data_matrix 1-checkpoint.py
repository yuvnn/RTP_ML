import os
import pandas as pd

#전처리 결과

#파일 경로
directory_path=os.getcwd()
data_directory_path = os.path.join(directory_path, 'labeling', '___ecfd1086a6934ae08b555b3ae880d31e')
grid_count_path = os.path.join(directory_path, 'grid_count_by_id')

# 디렉터리가 존재하지 않으면 생성
if not os.path.exists(grid_count_path):
    os.makedirs(grid_count_path)

# 연속되는 중복을 제거한 리스트 제작
def CollapseRecurringLabels(original_list):

    # Initialize the result list with the first element of the original list
    result_list = [original_list[0]]  

    for i in range(1, len(original_list)):
        if original_list[i] != original_list[i - 1]:
            result_list.append(original_list[i])

    return result_list


frequency_dict = {}     #그리드에 따른 횟수를 나타낸 딕셔너리
grid_path=[]            #한 사람의 모든 이동경로 리스트
#한 사람의 이동경로에서 그리드의 횟수를 카운팅
for file_name in os.listdir(data_directory_path):
    if file_name.endswith('.csv'):
        file_path = os.path.join(data_directory_path, file_name)
        df = pd.read_csv(file_path)

        #읽어온 데이터프레임에서 연속되는 중복 제거
        labels = df['grid_label'].tolist()
        unique_labels = CollapseRecurringLabels(labels)
        grid_path.append(unique_labels)

        #중복이 제거된 grid만 포함한 데이터프레임 생성.
        df_remove_duplicate = pd.DataFrame(unique_labels, columns=['grid_label'])
        
        #중복이 제거된 레이블을 카운트        
        label_counts = df_remove_duplicate['grid_label'].value_counts().to_dict()
        
        #빈도수 업데이트
        for key, value in label_counts.items():
            if key in frequency_dict:
                frequency_dict[key]+=value
            else:
                frequency_dict[key]=value

#그리드를 카운트한 csv 파일 생성
frequency_dataframe=pd.DataFrame(columns=['grid_label','count'])
rows = [{'grid_label': key, 'count': value} for key, value in frequency_dict.items()]
frequency_dataframe=pd.concat([frequency_dataframe, pd.DataFrame(rows)], ignore_index=True)
frequency_dataframe.to_csv(f'{grid_count_path}/___ecfd1086a6934ae08b555b3ae880d31e.csv')   

#이동경로에 N/AN 칼럼을 추가한 csv 파일 생성
F1_dataframe=pd.DataFrame(columns=['F1', 'grid_path'])
for i in range(len(grid_path)):
    grid_count=[]
    for path in grid_path[i]:
        grid_count.append(frequency_dict[path])
    if min(grid_count)>=3:
        F1_dataframe.loc[len(F1_dataframe)]=['N', grid_path[len(F1_dataframe)]]
    else:
        F1_dataframe.loc[len(F1_dataframe)]=['AN', grid_path[len(F1_dataframe)]]
print(F1_dataframe)

#최종 전처리 csv 파일 생성
F1_dataframe.to_csv(f'{directory_path}/preprocessing.csv')
