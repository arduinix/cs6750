def one_way_anova(data, group_col, value_col):
    """
    Perform a one-way ANOVA test on the provided data.

    Parameters:
    - data: DataFrame containing the data.
    - group_col: The column name for the grouping variable.
    - value_col: The column name for the dependent variable.

    Returns:
    - F-statistic and p-value from the ANOVA test.
    """
    groups = [group[value_col].values for name, group in data.groupby(group_col)]
    return f_oneway(*groups)