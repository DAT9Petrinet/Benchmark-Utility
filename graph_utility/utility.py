import pandas as pd


def common_answers(data_list):
    rows_to_delete = set()
    for index, data in enumerate(data_list):
        # Find all rows where we have 'NONE' answer
        answer_indices = set((data.index[data['answer'] == 'NONE']).tolist())

        # Add to rows that we want to delete
        if index == 0:
            rows_to_delete = answer_indices
        else:
            rows_to_delete = rows_to_delete.union(answer_indices)

    # Delete all the rows
    for data in data_list:
        data.drop(rows_to_delete, inplace=True)

    return data_list

