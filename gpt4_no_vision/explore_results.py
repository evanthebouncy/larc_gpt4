from drawing_grid import *
import json
import os

def render_task(task):
    # make the drawings_tmp folder if it doesn't exist
    if not os.path.exists('drawings_tmp'):
        os.mkdir('drawings_tmp')
    # draw all the grids for the task into the right folder
    name = task['name']
    desc_hash = str(hash(str(task['description'])))
    folder_name = name + '_' + desc_hash
    # make a folder in /drawings_tmp with this name
    if not os.path.exists(f'drawings_tmp/{folder_name}', ):
        os.mkdir(f'drawings_tmp/{folder_name}')

    # draw the training input-output
    for example_id in range(len(task['problem']['train'])):
        train_input = task['problem']['train'][example_id]['input']
        train_output = task['problem']['train'][example_id]['output']
        display_grid(train_input, f'drawings_tmp/{folder_name}/train_input_{example_id}')
        display_grid(train_output, f'drawings_tmp/{folder_name}/train_output_{example_id}')

    # draw the test input-output
    test_input = task['problem']['test'][0]['input']
    test_output = task['problem']['test'][0]['output']
    display_grid(test_input, f'drawings_tmp/{folder_name}/test_input')
    display_grid(test_output, f'drawings_tmp/{folder_name}/test_output')

    # 'draw' the description
    description = str(task['description'])
    with open(f'drawings_tmp/{folder_name}/description.txt', 'w') as f:
        f.write(description)

    # for the results in 'gpt4' / ['nl_only', 'nl_and_io', 'io_only', 'nothing']
    gpt4_results = task['gpt4']
    for result in gpt4_results:
        grid = get_gpt4_response_grid(gpt4_results[result])
        if grid is not None:
            display_grid(grid, f'drawings_tmp/{folder_name}/gpt4_{result}')

# filter the task
def make_filter(filter_condition):
    def filter(task):
        gpt4_results = task['gpt4']
        for filter_key in filter_condition:
            if filter_key not in gpt4_results:
                return False
            gpt4_grid = get_gpt4_response_grid(gpt4_results[filter_key])
            output_grid = task['problem']['test'][0]['output']
            success = str(gpt4_grid) == str(output_grid)
            if filter_condition[filter_key] and not success:
                return False
            if not filter_condition[filter_key] and success:
                return False
        return True
    return filter

def is_complete(task):
    gpt4_results = task['gpt4']
    return len (gpt4_results) == 4

if __name__ == '__main__':
    with open('results/larc_gpt4.json', 'r') as f:
        larc_gpt4 = json.load(f)

    all_tasks = set()
    filtered_tasks = set()

    filter_condition = {'nl_only': True, 'nl_and_io': True, 'io_only': True, 'nothing': True}
    filter_condition = {'nl_only': True, 'nl_and_io': True, 'io_only': True}

    for task in larc_gpt4:

        # this is optional
        if not is_complete(task):
            continue

        all_tasks.add(task['name'])
        if make_filter(filter_condition)(task):
            filtered_tasks.add(task['name'])
            render_task(task)

    print ("all tasks: ", len(all_tasks))
    print ("filtered tasks: ", len(filtered_tasks))
