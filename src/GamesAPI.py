import sys
from src import GetIDs, GetDeals



def main():
    args = sys.argv
    mode = 1
    if len(args) > 1:
        mode = int(args[1])

    if mode == 1:
        GetIDs.main()
        GetDeals.main()
    elif mode == 2:
        GetIDs.main()
    elif mode == 3:
        GetDeals.main()
    else:
        print("Invalid mode")


if __name__ == "__main__":
    main()