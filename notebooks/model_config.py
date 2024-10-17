import os

pr_path = os.getcwd()
os.chdir("..")
pr_path = os.getcwd()

Path = {
    "data":os.path.join(pr_path, "data"),
    "raw":os.path.join(pr_path, "data", "raw"),
    "processed":os.path.join(pr_path, "data", "processed"),
    "dataset": lambda dnum, scaler, col_cnt, tkn_cnt, timeframe: os.path.join(pr_path, "data", "processed", f"dataset_{dnum}D_{scaler}_{col_cnt}cols_{tkn_cnt}tkn_{timeframe}t.csv"),

    "models":os.path.join(pr_path, "results", "models"),
    "model_save": lambda mnum, dnum: os.path.join(pr_path, "results", "models", f"model_{mnum}V_{dnum}D"),

    "plots": lambda mnum, dnum, name: os.path.join(pr_path, "results", "plots", f"plot_{mnum}V_{dnum}D_{name}.html"),

    "reports": lambda mnum, dnum, name: os.path.join(pr_path, "results", "reports", f"report_{mnum}V_{dnum}D_{name}.csv"),

    "train_log": lambda mnum, dnum: os.path.join(pr_path, "results", "logs", f"train_log_{mnum}V_{dnum}D.log"),
    "test_log": lambda mnum, dnum: os.path.join(pr_path, "results", "logs", f"test_log_{mnum}V_{dnum}D.log"),
}
