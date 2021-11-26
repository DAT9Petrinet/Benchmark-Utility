import numpy as np
import pandas as pd


def remove_rows_with_no_answers_or_query_simplification(data_list):
    for data in data_list:
        # Remove rows where query simplification has been used, or where there isn't an answer
        data.drop(data[(data['solved by query simplification'] == True) | (
                data['solved by query simplification'] == 'ERR') | (data.answer == 'NONE')].index, inplace=True)
    return data_list


def filter_out_tests_that_had_none_answer_in_any_experiment(data_list):
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
def filter_out_test_instances_that_were_not_reduced_by_any(data_list):
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


def remove_no_red(data_list, test_names):
    for test_index, name in enumerate(test_names):
        if 'no-red' in name:
            data_list.pop(test_index)
            test_names.pop(test_index)
    return data_list, test_names


def color(t):
    a = np.array([0.5, 0.5, 0.5])
    b = np.array([0.5, 0.5, 0.5])
    c = np.array([1.0, 1.0, 1.0])
    d = np.array([0.0, 0.33, 0.67])

    return a + (b * np.cos(2 * np.pi * (c * t + d)))


def sanitise_df(df):
    df = infer_errors(df)
    return infer_simplification_from_prev_size_0_rows(df)


def sanitise_df_list(datalist):
    sanitised_datalist = []
    for df in datalist:
        sanitised_datalist.append(sanitise_df(df))
    return sanitised_datalist


def rename_index_to_test_name(df, test_names):
    new_indices = dict()
    for index, name in enumerate(test_names):
        new_indices[index] = name
    df = df.rename(index=new_indices)

    return df


def split_into_all_with_without(df):
    columns_with = [test_name for test_name in df.T.columns if
                    ("with" in test_name) or ("base-rules" in test_name)]
    columns_not_with = [test_name for test_name in df.T.columns if
                        "with" not in test_name or ("base-rules" in test_name)]

    columns_to_be_removed_by_with = [column for column in df.T.columns if column not in columns_with]
    columns_to_be_removed_by_without = [column for column in df.T.columns if column not in columns_not_with]

    df_without = df.drop(columns_to_be_removed_by_without)
    df_with = df.drop(columns_to_be_removed_by_with)

    return [df, df_with, df_without]


def make_derived_jable(csvs, exp_names):
    needed_columns = ['model name', 'query index', 'answer', 'verification time', 'verification memory',
                      'prev place count', 'post place count',
                      'prev transition count', 'post transition count', 'reduce time', 'state space size']
    # line_columns = ['verification time', 'verification memory', 'reduce time', 'state space size']

    for data in csvs:
        data.set_index(["model name", "query index"], inplace=True)
        columns_to_drop = [column for column in data.columns if column not in needed_columns]
        data.drop(columns_to_drop, axis=1, inplace=True)

    for i, csv in enumerate(csvs):
        csv.rename(columns={col: f"{exp_names[i]}@{col}" for col in csv.columns}, inplace=True)
    everything = pd.concat(csvs, axis=1)
    everything.sort_index(level=0, inplace=True)

    # Get smallest value from the line columns
    # todo rewrite to get second smallest
    '''for column in line_columns:
        columns = [experiment_column + '@' + column for experiment_column in exp_names]
        everything[f'min {column}'] = everything[columns].min(axis=1)'''

    for exp_name in exp_names:
        everything[f'{exp_name}@total time'] = everything.apply(
            lambda row: row[f'{exp_name}@reduce time'] + row[f'{exp_name}@verification time'], axis=1)

    # Create reduced sizes and prev/post sizes
    for exp_name in exp_names:
        for time in ['prev', 'post']:
            everything[f'{exp_name}@{time} size'] = everything[f'{exp_name}@{time} place count'] + everything[
                f'{exp_name}@{time} transition count']
        everything[f'{exp_name}@reduced size'] = - (everything[f'{exp_name}@prev size'] - everything[
            f'{exp_name}@post size'])

    # Unique answer
    answer_columns = [experiment_column + '@' + 'answer' for experiment_column in exp_names]
    everything['unique answers'] = everything[answer_columns].apply(
        lambda row: row.index[row != 'NONE'][0].split("@", 1)[0] if 'NONE' in (row.value_counts().index) and
                                                                    row.value_counts()[
                                                                        'NONE'] == len(exp_names) - 1 else np.nan,
        axis=1)

    return everything


def get_pre_size(row):
    return row['prev place count'] + row['prev transition count']


def get_post_size(row):
    return row['post place count'] + row['post transition count']


def get_reduced_size(row):
    if row['prev place count'] > 0:
        pre_size = get_pre_size(row)
        post_size = get_post_size(row)
        return ((post_size / pre_size) * 100) if post_size > 0 else np.nan
    else:
        return np.nan


def get_total_time(row):
    return row['reduce time'] + row['verification time']


def remove_prev_size_0_rows(df):
    df = df[(df['prev place count'] + df['prev transition count']) > 0]
    return df


def all_columns_indicate_error(row):
    columns_with_0_indicating_error = ['verification time', 'verification memory', 'reduce time',
                                       'state space size']
    error = False
    if get_pre_size(row) == 0.0 and get_post_size(row) == 0.0:
        for column in columns_with_0_indicating_error:
            if row[column] != 0.0:
                break
            error = True

    return error


def infer_errors(df):
    def row_with_err(row):
        row['answer'] = 'ERR'
        row['solved by query simplification'] = 'ERR'
        return row

    df = df.apply(lambda row: row_with_err(row) if all_columns_indicate_error(row) else row, axis=1)
    return df


def number_of_errors(df):
    return pd.DataFrame(df.apply(lambda row: 1 if all_columns_indicate_error(row) else 0, axis=1))[0].sum()


def infer_simplification_from_prev_size_0_rows(df):
    df['answer'] = df.apply(
        lambda row: 'TRUE' if (get_post_size(row) == 0.0 and get_pre_size(row) > 0) else row['answer'], axis=1)
    df['solved by query simplification'] = df.apply(
        lambda row: True if (get_post_size(row) == 0.0 and get_pre_size(row) > 0) else row[
            'solved by query simplification'], axis=1)
    return df


def second_smallest_in_list(list):
    return sorted(list)[1]


def second_largest_in_list(list):
    return sorted(list)[-2]


def unique_answers_comparison(df, experiment_to_compare_against, test_names):
    res = pd.DataFrame()
    for test in test_names:
        temp = df.apply(lambda row: 1 if ((row[experiment_to_compare_against + '@answer'] == 'NONE') and (
                row[test + '@answer'] != 'NONE')) else 0, axis=1)
        res[test] = [temp.sum()]
    return res.T[0]


def zero_padding(series, metric, test_names):
    if metric != 'unique answers':
        metric_columns = [experiment_column + '@' + metric for experiment_column in test_names]
    else:
        metric_columns = test_names

    for test_name in metric_columns:
        if test_name not in series or (test_name == 'no-red' and metric in ['reduce time', 'reduced size']):
            series[test_name] = 0
    return series


def largest_x_jable(df, x, metric, test_names):
    n = int(df.shape[0] * x)

    metric_columns = [experiment_column + '@' + metric for experiment_column in test_names]
    res_df = pd.DataFrame()
    if metric in ['verification time', 'verification memory']:
        for column in metric_columns:
            res_df[column] = df[(df[(column.split("@", 1)[0]) + '@answer'] != 'NONE')][column]
            res_df[column] = res_df[np.isfinite(res_df[column])][column]
    else:
        for column in metric_columns:
            res_df[column] = df[np.isfinite(df[column])][column]

    res_df = pd.DataFrame({x: res_df[x].sort_values().values for x in res_df[metric_columns].columns.values})

    return res_df.tail(n)


def remove_errors_df(df):
    return df[df['answer'] != 'ERR']


def remove_errors_datalist(data_list):
    for data in data_list:
        data.drop(data[data['answer'] == 'ERR'].index, inplace=True)
    return data_list
