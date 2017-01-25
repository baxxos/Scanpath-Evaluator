import json
from os import listdir, path


class User:
    DATASET_FOLDER = 'datasets'

    def __init__(self, user_id):
        self.user_id = user_id

    def get_data_tree_json(self):
        datasets = listdir(path.join(self.DATASET_FOLDER))
        data_tree = []

        # Simulates primary keys of datasets and their tasks
        seq_dataset = 0
        seq_task = 0

        for dataset_folder in datasets:
            seq_dataset += 1

            data_tree.append({
                'label': dataset_folder,
                'id': seq_dataset,
                'children': []
            })

            # Load tasks owned by current dataset
            tasks = listdir(path.join(self.DATASET_FOLDER, dataset_folder))

            for task_folder in tasks:
                seq_task += 1

                data_tree[len(data_tree) - 1]['children'].append({
                    'label': task_folder,
                    'id': seq_task
                })

        return json.dumps(data_tree)
