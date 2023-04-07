import matplotlib.pyplot as plt
import numpy as np

def get_gpt4_response_grid(gpt4_response):
    try:
        # parse the content between [[ and ]] for the grid, inclusive
        gpt4_response_grid = gpt4_response[gpt4_response.find("[[")+2:gpt4_response.find("]]")]
        # put the [[ and ]] back in, eval it into array
        gpt4_response_grid = eval("[[" + gpt4_response_grid + "]]")

        # pad inner lists to all be the same length
        max_len = max([len(row) for row in gpt4_response_grid])
        gpt4_response_grid = [row + [0] * (max_len - len(row)) for row in gpt4_response_grid]

        # if elements arent ints, return None
        for row in gpt4_response_grid:
            for element in row:
                if not isinstance(element, int):
                    return None

        return gpt4_response_grid
    except:
        return None

def display_grid(grid, save_name=None):
    grid = np.array(grid)
    # Example colors
    colors = ['#000', '#0074D9', '#FF4136', '#2ECC40', '#FFDC00', '#AAAAAA', '#F012BE', '#FF851B', '#7FDBFF', '#870C25', '#FAFAFA']

    # Define color map for the numbers 0-9 using the colors from the previous example
    cmap = plt.cm.colors.ListedColormap(colors[:11])

    # Display the grid as an image with the defined color map
    plt.imshow(grid, cmap=cmap, interpolation='nearest')

    # ensure the color map is from 0 to 10
    plt.clim(0, 11)

    if save_name is not None:
        plt.savefig(save_name)
        # make sure to close the plot to save memory
        plt.close()

    else:
        # Display the plot
        plt.show()

if __name__ == '__main__':
    import json
    task_id = 0

    # open the json in results/np_only_task_with_answers_164.json
    with open('results/nl_only_task_with_answers_164.json') as json_file:
        task_with_answers = json.load(json_file)

    for task_id, task in enumerate(task_with_answers):
        try:
            task_name = task['name']
            task_name = task_name.replace(".json", "")
            # get the input grid
            input_grid = task['problem']['test'][0]['input']
            # get the output grid
            output_grid = task['problem']['test'][0]['output']
            # get the gpt-4 response
            gpt4_response = task['gpt-4-response']
            # parse the content between [[ and ]] for the grid, inclusive
            gpt4_response_grid = gpt4_response[gpt4_response.find("[[")+2:gpt4_response.find("]]")]
            # put the [[ and ]] back in, eval it into array
            gpt4_response_grid = eval("[[" + gpt4_response_grid + "]]")
            # render these three grids, and save to the /drawings folder with the right names
            display_grid(input_grid, save_name=f"drawings/{task_id}_{task_name}_input_grid_" + ".png")
            display_grid(output_grid, save_name=f"drawings/{task_id}_{task_name}_output_grid_" + ".png")
            display_grid(gpt4_response_grid, save_name=f"drawings/{task_id}_{task_name}_gpt4_response_grid_" + ".png")
            # print (task)
        except:
            print ("error on task ", task_name)
            continue
