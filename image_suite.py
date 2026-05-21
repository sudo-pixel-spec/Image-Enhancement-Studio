import tkinter as tk
from studio.app import ImageSuite


def main() -> None:
    root = tk.Tk()
    ImageSuite(root)
    root.mainloop()



if __name__ == "__main__":
    main()
