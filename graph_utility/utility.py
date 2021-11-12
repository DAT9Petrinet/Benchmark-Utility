import numpy as np


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


# Find test instances that no experiment managed to reduce
def filter_out_no_answers(data_list):
    rows_to_delete = set()
    for index, data in enumerate(data_list):
        # Find all indices where the query has been solved by simplification
        simplification_indices = set((data.index[data['solved by query simplification']]).tolist())

        # Find all rows where we have 'NONE' answer
        answer_indices = set((data.index[data['answer'] == 'NONE']).tolist())

        # Take the union
        combined_indices = answer_indices.union(simplification_indices)

        # Only interested in finding the rows that NO experiment managed to reduce
        # So take intersection
        if index == 0:
            rows_to_delete = combined_indices
        else:
            rows_to_delete = rows_to_delete.intersection(combined_indices)

    # Remove the rows from all data files
    for data in data_list:
        data.drop(rows_to_delete, inplace=True)

    return data_list


def color(t):
    a = np.array([0.5, 0.5, 0.5])
    b = np.array([0.5, 0.5, 0.5])
    c = np.array([1.0, 1.0, 1.0])
    d = np.array([0.0, 0.33, 0.67])

    return a + (b * np.cos(2 * np.pi * (c * t + d)))
