import json

# open results/nl_only_task_with_gpt4.json
with open('results/larc_gpt4_newer.json') as json_file:
    results = json.load(json_file)

def grab_output(gpt4_response):
    try:
        # parse the content between [[ and ]] for the grid, inclusive, 
        # there might be multiple grids, but we only care about the LAST one
        gpt4_response_grid = gpt4_response.split("[[")[-1]
        gpt4_response_grid = gpt4_response_grid.split("]]")[0]
        gpt4_response_grid = eval("[[" + gpt4_response_grid + "]]")
        return gpt4_response_grid
    except:
        return None
    
def summarize(task):
    task_name = task['name']
    task_name = task_name.replace(".json", "")
    # get the input grid
    input_grid = task['problem']['test'][0]['input']
    # get the output grid
    output_grid = task['problem']['test'][0]['output']
    # get the gpt-4 response
    gpt4_response = task['gpt4']
    ret = {}
    for k in gpt4_response:
        correct = str(output_grid) == str(grab_output(gpt4_response[k]))
        ret[k] = correct
    return ret


if __name__ == '__main__':

    # check all the tasks that we were able to get a response for
    set_correct = {}
    all_tasks = set()
    for i, task in enumerate(results):
        task_name = task['name']
        task_response = summarize(task)
        if len(task_response) < 5:
            print (f"task {task_name} has less than 5 responses ", task_response)
            continue

        all_tasks.add(task_name)
        for k in task_response:
            if k not in set_correct:
                set_correct[k] = set()
            if task_response[k]:
                set_correct[k].add(task_name)

    print ("all tasks: ", len(all_tasks))
    for k in set_correct:
        print (k, len(set_correct[k]), len(set_correct[k])/len(all_tasks))
