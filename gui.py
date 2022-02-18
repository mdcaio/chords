import tkinter as tk
import tkinter.font as tkFont
from chords import MAJOR_STR, MINOR_STR, MODAL_TONE, NOTES_B, NOTES_S, Chords, Scale


def get_possible_root_notes():
    roots = []
    for b, d in zip(NOTES_B[:12], NOTES_S[:12]):
        if b == d:
            roots += b
        else:
            roots += [d, b]
    return roots


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.geometry("700x400")
        self.resizable(0, 0)
        self.title("Chords Finder")

        frame = tk.Frame(master=self, bg="white")
        frame.pack(fill=tk.BOTH)
        self.arial = tkFont.Font(family="arial", size=15, weight="normal")
        label = tk.Label(
            master=frame, text="Root note", font=self.arial, background="white"
        )
        label.pack()
        self.root = tk.StringVar(self)
        notes = get_possible_root_notes()
        self.root.set(notes[0])
        self.x = tk.OptionMenu(frame, self.root, notes[0], *notes)
        self.x.config(font=self.arial)
        self.x.pack()

        label = tk.Label(
            master=frame, text="Base scale", font=self.arial, background="white"
        )
        label.pack()
        self.base_scale = tk.StringVar(self)
        possible_bases = [MAJOR_STR, MINOR_STR]
        self.base_scale.set(possible_bases[0])
        self.y = tk.OptionMenu(frame, self.base_scale, *possible_bases)
        self.y.config(font=self.arial)
        self.y.pack()

        label = tk.Label(master=frame, text="Mode", font=self.arial, background="white")
        label.pack()
        self.mode = tk.StringVar(self)
        possible_modes = list(MODAL_TONE.keys())
        self.mode.set(possible_modes[0])
        self.z = tk.OptionMenu(frame, self.mode, *possible_modes)
        self.z.config(font=self.arial)
        self.z.pack()

        self.seventh = tk.IntVar()
        tk.Checkbutton(
            frame,
            text="Sevenths",
            variable=self.seventh,
            font=self.arial,
            background="white",
        ).pack()
        self.seventh.trace("w", self.callback)

        self.t = tk.Text()
        self.t.insert(
            tk.END,
            f"{Scale(self.root.get(), self.base_scale.get(), self.mode.get())}"
            f"\n{Chords(Scale(self.root.get(), self.base_scale.get(), self.mode.get()), self.seventh.get())}",
        )
        self.t.config(font=self.arial)
        self.t.pack()

        self.root.trace("w", self.callback)
        self.base_scale.trace("w", self.callback)
        self.mode.trace("w", self.callback)

    def callback(self, *args):
        self.update_output()

    def update_output(self):
        self.t.delete("1.0", tk.END)
        self.t.insert(
            tk.END,
            f"{Scale(self.root.get(), self.base_scale.get(), self.mode.get())}"
            f"\n{Chords(Scale(self.root.get(), self.base_scale.get(), self.mode.get()), self.seventh.get())}",
        )

if __name__=="__main__":
    App().mainloop()
