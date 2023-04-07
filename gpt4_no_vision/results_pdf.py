import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, Table, PageBreak, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import glob
import json
import drawing_grid
import explore_results

styles = getSampleStyleSheet()

def create_image_if_exists(file_path, width, height):
    if os.path.exists(file_path):
        return Image(file_path, width=width, height=height)
    else:
        return None

def generate_task_dict(task_folders):
    '''
    Create dict {task_id: list of task folders with that id}
    '''
    task_results = {}

    for task_folder in task_folders:
        task_id = task_folder[task_folder.index('/') + 1:task_folder.index('.')]

        if task_id not in task_results:
            task_results[task_id] = []
        task_results[task_id].append(task_folder)

    return task_results


def generate_pdf(task_dict):
    pdf_file = "larc_gpt4_results.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []

    for task_id in task_dict:
        task_folder = task_dict[task_id][0]

        # Add heading with task ID
        content.append(Paragraph(f"Task ID: {task_id}", styles["Heading3"]))

        # Add train input and outputs
        data = []
        for i in range(4):
            train_input_path = os.path.join(task_folder, f"train_input_{i}.png")
            train_output_path = os.path.join(task_folder, f"train_output_{i}.png")
            train_input = create_image_if_exists(train_input_path, 100, 100)
            train_output = create_image_if_exists(train_output_path, 100, 100)
            if train_input or train_output:
                data.append([Paragraph("train", styles["Normal"]), train_input or Spacer(1, 1), train_output or Spacer(1, 1)])

        # Add test input
        test_input = create_image_if_exists(os.path.join(task_folder, "test_input.png"), 100, 100)
        data.append([Paragraph("test", styles["Normal"]), test_input, Spacer(1, 1)])

        # transpose data
        data = list(zip(*data))

        # add data to pdf
        example_table = Table(data, colWidths=[100, 100]*4, rowHeights=[20, 100, 100], hAlign='LEFT')
        content.append(example_table)

        # Add GPT-4 generations
        content.append(Paragraph("GPT-4 Generations", styles["Heading3"]))

        target_img = create_image_if_exists(os.path.join(task_folder, "test_output.png"), 100, 100)
        img_path = os.path.join(task_folder, "gpt4_io_only.png")
        io_only_img = create_image_if_exists(img_path, 100, 100)

        # Add row with target img and io_only img
        content.append(Table([["Target", "io_only"], [target_img, io_only_img]],
                             colWidths=[100]*4, rowHeights=[20, 100],
                             hAlign='LEFT'))

        # for each NL description, add row with nl_only and nl_and_io
        gpt4_images = [
            ("gpt4_nl_and_io.png", "nl_and_io"),
            ("gpt4_nl_only.png", "nl_only"),
        ]

        for nl_task_folder in task_dict[task_id]:
            gpt4_data = []
            gpt4_labels = []

            for filename, label in gpt4_images:
                img_path = os.path.join(nl_task_folder, filename)
                img = create_image_if_exists(img_path, 100, 100)
                gpt4_labels.append(Paragraph(label, styles["Normal"]))
                gpt4_data.append(img or Spacer(1, 1))

            # get description dict
            with open(os.path.join(nl_task_folder, "description.txt"), 'r') as f:
                task_description_dict = eval(f.read().strip())

            # add output grid descrption after images with very small font size
            gpt4_data.append(Paragraph(task_description_dict["description_output"],
                                       ParagraphStyle(name="CustomStyle", parent=styles["BodyText"], fontSize=8)))

            table = Table([gpt4_labels, gpt4_data], colWidths=[100, 100, None], rowHeights=[20, 100], hAlign='LEFT')
            # Vertically center the text in the third column, first row ])
            table_style = TableStyle([('VALIGN', (2, 0), (2, 0), 'MIDDLE')])
            table.setStyle(table_style)
            content.append(table)


        # Add a page break between tasks
        content.append(PageBreak())

    print('Building PDF, might take some time...')
    doc.build(content)


def get_task_folders(base_path, pattern):
    task_folders = [folder for folder in glob.glob(os.path.join(base_path, pattern)) if os.path.isdir(folder)]
    return task_folders


def save_all_results():
    with open('results/larc_gpt4.json', 'r') as f:
        larc_gpt4 = json.load(f)

    count = 0
    for task in larc_gpt4:
        count += 1
        print(f"{count}/{len(larc_gpt4)}")

        if explore_results.is_complete(task):
            explore_results.render_task(task)


if __name__ == '__main__':
    # save_all_results()
    base_path = "drawings_tmp"
    folder_pattern = "*.json_*"
    task_folders = get_task_folders(base_path, folder_pattern)
    task_dict = generate_task_dict(task_folders)
    generate_pdf(task_dict)
