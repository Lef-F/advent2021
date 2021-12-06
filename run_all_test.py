import subprocess as s
import os


def main():
    nbs = sorted(os.listdir("solutions/"))
    nbs = [nb for nb in nbs if not "nbconvert" in nb]
    for nb in nbs:
        print("*" * 10, nb, "*" * 10)
        s.check_call(
            ["jupyter", "nbconvert", "--to", "notebook", "--execute", f"solutions/{nb}"]
        )

    nb_leftovers = os.listdir("solutions/")
    nb_leftovers = [nb for nb in nb_leftovers if "nbconvert" in nb]
    for leftover in nb_leftovers:
        print(f"Cleaning up solutions/{leftover}")
        os.remove(f"solutions/{leftover}")


if __name__ == "__main__":
    print("Running all notebooks for testing purposes.")
    main()
