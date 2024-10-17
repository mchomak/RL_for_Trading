import os

pr_path = os.getcwd()
Path = {
    "data":os.path.join(pr_path, "data"),
    "raw":os.path.join(pr_path, "data", "raw"),

    "models":os.path.join(pr_path, "models"),
    "model_dir": lambda mnum: os.path.join(pr_path, "models", f"model_v{mnum}"),
    "model": lambda mnum, dnum: os.path.join(pr_path, "models", f"model_v{mnum}", f"model_v{mnum}_{dnum}"),
    "reports": lambda mnum, dnum: os.path.join(pr_path, "models", f"model_v{mnum}", f"report_{mnum}_{dnum}.csv"),
    "dataset": lambda mnum, dnum: os.path.join(pr_path, "models", f"model_v{mnum}", f"dataset_{mnum}_{dnum}.csv"),
    "train_data": lambda mnum, dnum: os.path.join(pr_path, "models", f"model_v{mnum}", f"train_{mnum}_{dnum}.csv"),
    "test_data": lambda mnum, dnum: os.path.join(pr_path, "models", f"model_v{mnum}", f"test_{mnum}_{dnum}.csv"),
    "train_log": lambda mnum, dnum: os.path.join(pr_path, "models", f"model_v{mnum}", f"train_log_{mnum}_{dnum}.log"),
    "test_log": lambda mnum, dnum: os.path.join(pr_path, "models", f"model_v{mnum}", f"test_log_{mnum}_{dnum}.log"),
    "save_model": lambda mnum, dnum: os.path.join(pr_path, "models", f"model_v{mnum}", f"model_weight_{mnum}_{dnum}.h5f"),
}
