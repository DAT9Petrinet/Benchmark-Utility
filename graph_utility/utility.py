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
    df = infer_simplification_from_prev_size_0_rows(df)
    return df


def sanitise_df_list(datalist):
    return [sanitise_df(df) for df in datalist]


def rename_index_to_test_name(df, test_names):
    new_indices = dict()
    for index, name in enumerate(test_names):
        new_indices[index] = name
    df = df.rename(index=new_indices)

    return df


def make_derived_jable(csvs, exp_names):
    needed_columns = ['model name', 'query index', 'answer', 'verification time', 'verification memory',
                      'prev place count', 'post place count',
                      'prev transition count', 'post transition count', 'reduce time', 'state space size',
                      'solved by query simplification']

    for data in csvs:
        data.set_index(["model name", "query index"], inplace=True)
        columns_to_drop = [column for column in data.columns if column not in needed_columns]
        data.drop(columns_to_drop, axis=1, inplace=True)

    for i, csv in enumerate(csvs):
        csv.rename(columns={col: f"{exp_names[i]}@{col}" for col in csv.columns}, inplace=True)
    jable = pd.concat(csvs, axis=1)
    jable.sort_index(level=0, inplace=True)

    for exp_name in exp_names:
        jable[f'{exp_name}@total time'] = jable.apply(
            lambda row: row[f'{exp_name}@reduce time'] + row[f'{exp_name}@verification time'], axis=1)

    # Create reduced sizes and prev/post sizes
    for exp_name in exp_names:
        for time in ['prev', 'post']:
            jable[f'{exp_name}@{time} size'] = jable[f'{exp_name}@{time} place count'] + jable[
                f'{exp_name}@{time} transition count']
        jable[f'{exp_name}@reduced size'] = (jable[f'{exp_name}@post size'] - jable[
            f'{exp_name}@prev size'])
    return jable


def get_pre_size(row):
    return row['prev place count'] + row['prev transition count']


def get_post_size(row):
    return row['post place count'] + row['post transition count']


def get_reduced_size(row):
    if row['prev place count'] > 0:
        pre_size = get_pre_size(row)
        post_size = get_post_size(row)
        return ((post_size / pre_size) * 100) if post_size > 0 and (
                (post_size / pre_size) * 100) > 0 else np.nan
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


def row_indicate_simplification_jable(row, test_name):
    return (row[f'{test_name}@post size'] == 0.0 and row[f'{test_name}@prev size'] > 0) or row[
        f'{test_name}@solved by query simplification']


def row_indicate_simplification(row):
    return (get_post_size(row) == 0.0 and get_pre_size(row) > 0) or row['solved by query simplification']


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


def largest_x_by_prev_size_jable(jable, x, test_name):
    n = int(jable.shape[0] * x)

    res_df = jable.sort_values(by=[f'{test_name}@prev size'])

    return res_df.tail(n)


def remove_errors_df(df):
    return df[df['answer'] != 'ERR']


def remove_errors_datalist(data_list):
    for data in data_list:
        data.drop(data[data['answer'] == 'ERR'].index, inplace=True)
    return data_list


def rename_test_name_for_paper_presentation(test_names):
    new_test_names = {}
    for test_name in test_names:
        if test_name in ['fixedbase-i', 'fixedbase']:
            new_test_name = f"(base)⃰"
            #if "-i" in test_name:
             #   new_test_name += "-inhib"
        elif test_name == "origbase":
            new_test_name = test_name
        elif test_name == "TAPAAL":
            new_test_name = test_name
        elif test_name == "with-M-as-E":
            new_test_name = "(A⃰.B⃰.C⃰.D⃰.M⃰.F⃰.G⃰.I⃰)⃰"
        elif test_name == "only-M-then-E":
            new_test_name = f"(M⃰.E⃰)⃰"
        elif test_name == "only-QRE-then-AB":
            new_test_name = f"((Q⃰.R⃰.E⃰)⃰.(A⃰.B⃰))⃰"
        elif test_name in ["with-M-as-E-NO", "with-MasE-NO-i"]:
            new_test_name = "(A⃰.B⃰.C⃰.D⃰.M⃰.F⃰.G⃰.I⃰.N⃰.O⃰)⃰"
        elif test_name == "with-MasE-NOP-i":
            new_test_name = "(A⃰.B⃰.C⃰.D⃰.M⃰.F⃰.G⃰.I⃰.N⃰.O⃰.P⃰)⃰"
        elif test_name == "with-LMNOPQR-i-run1":
            new_test_name = '(base.L⃰.M⃰.N⃰.O⃰.P⃰.Q⃰.R⃰)⃰-run1'
        elif test_name == "fixedbase-i-run1":
            new_test_name = f"(base)⃰-run1"
        else:
            splits = test_name.split('-')
            if len(splits) > 0:
                rules = ""
                split_rules = list(splits)[1:]

                appendage = ""
                for i, split in enumerate(split_rules):
                    if i == len(split_rules) - 1 and split in ['DFS', 'inhib', 'DSF', 'i']:
                        if split == 'DFS':
                            appendage += f"-{split}"
                        else:
                            continue
                    if split.isalpha():
                        if len(split) > 0:
                            for i, subrule in enumerate(split):
                                rules += f"{subrule}⃰"
                                if i != len(split) - 1:
                                    rules += "."
            if "with" in test_name and (len(rules) > 0 or len(appendage) > 0):
                new_test_name = f"(base.{rules})⃰{appendage}"
            else:
                starred = [f"{rule}⃰" for rule in list(test_name)]
                new_test_name = ""
                for i, star in enumerate(starred):
                    if (i != len(starred) - 1):
                        new_test_name += f"{star}."
                    else:
                        new_test_name += f"{star}"
                new_test_name = f"({new_test_name})⃰"

        new_test_names[test_name] = new_test_name
    return new_test_names


'''
def split_into_all_with_without(df):
    columns_with = [test_name for test_name in df.T.columns if
                    ("with" in test_name) or ("base-rules" in test_name)]
    columns_not_with = [test_name for test_name in df.T.columns if
                        "with" not in test_name or ("base-rules" in test_name)]

    columns_to_be_removed_by_with = [column for column in df.T.columns if column not in columns_with]
    columns_to_be_removed_by_without = [column for column in df.T.columns if column not in columns_not_with]

    df_without = df.drop(columns_to_be_removed_by_without)
    df_with = df.drop(columns_to_be_removed_by_with)

    return [df, df_with, df_without]'''
