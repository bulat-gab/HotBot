import os
from src.launcher import launch

if __name__ == "__main__":
    if not os.path.exists("./sessions"):
        os.mkdir("./sessions")

    launch()