import numpy as np
from scipy import stats


def diebold_mariano_test(actual, pred1, pred2, h=1):
    # actual: 真实值
    # pred1: OLS预测值 (基准)
    # pred2: Random Forest预测值 (挑战者)

    e1 = np.array(actual) - np.array(pred1)
    e2 = np.array(actual) - np.array(pred2)

    d = e1 ** 2 - e2 ** 2  # Loss differential

    d_mean = np.mean(d)
    d_var = np.var(d, ddof=1)

    # DM statistic calculation
    dm_stat = d_mean / np.sqrt(d_var / len(d))

    # p-value (two-tailed)
    p_value = 2 * (1 - stats.norm.cdf(abs(dm_stat)))

    return dm_stat, p_value

# 示例调用
# dm, p = diebold_mariano_test(y_test, y_pred_ols, y_pred_rf)
# print(f"DM Stat: {dm}, P-value: {p}")