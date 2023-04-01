import csv
import pandas as pd
import json

# read larc_csv/build.csv as a pandas dataframe
build_df = pd.read_csv('larc_csv/build.csv')
# get all the entries where 'is_success' is True
build_df = build_df[build_df['is_success'] == True]
success_builds = build_df['build_id'].tolist()

# read larc_csv/join.csv as a pandas dataframe
join_df = pd.read_csv('larc_csv/join.csv')
# get the entries in join_df where 'build_id' is in success_builds
join_df = join_df[join_df['build_id'].isin(success_builds)]

# read larc_csv/description.csv as a pandas dataframe
description_df = pd.read_csv('larc_csv/description.csv')
# read larc_csv/task.csv as a pandas dataframe
task_df = pd.read_csv('larc_csv/task.csv')

successful_tasks = []

seen_task_discription = set()

# for each row in the join_df dataframe
# grab task_df['task_id'] and description_df['description_id'] and put them together
# in a list called successful_tasks
for index, row in join_df.iterrows():
    task_id = row['task_id']
    description_id = row['description_id']

    # certain task/description has multiple successful builds
    # we only want to add it once
    seen_key = str(task_id) + str(description_id)
    if seen_key in seen_task_discription:
        continue
    seen_task_discription.add(seen_key)

    # get the description from description_df
    description = description_df[description_df['description_id'] == description_id]
    desc = {'description_input': description['description_input'].tolist()[0],
            'description_output_grid_size': description['description_output_grid_size'].tolist()[0],
            'description_output': description['description_output'].tolist()[0]}
    assert description['is_verified'].tolist()[0] == True

    task = task_df[task_df['task_id'] == task_id]
    # get the task json name
    json_name = task['task_name'].tolist()[0]
    # open the json file at larc_csv/training/json_name
    with open('larc_csv/training/' + json_name) as json_file:
        problem = json.load(json_file)
        successful_tasks.append({'name': json_name, 'description': desc, 'problem': problem})

print (len(successful_tasks))
print (successful_tasks[:4])

# dump the successful_tasks list to a json file, name it 'successful_tasks_with_desciptor.json'
with open('successful_tasks_with_desciptor.json', 'w') as outfile:
    json.dump(successful_tasks, outfile)

