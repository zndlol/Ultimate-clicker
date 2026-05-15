import tkinter as tk
import keyboard
import mouse
import threading
import time
import os
from PIL import Image, ImageDraw, ImageTk
import tempfile

TOGGLE_HOTKEY = "f7"
BG = "#f8f9fa"       
CARD = "#ffffff"     
BORDER = "#dee2e6"   
TEXT = "#212529"     
MUTED = "#6c757d"    
PRIMARY = "#1a1d23"  
ACCENT = "#4c6ef5"   
KEY_BG = "#ffffff"

state = {
    "key": "space", 
    "scan": 57, 
    "interval": 1000, 
    "running": False, 
    "count": 0, 
    "stop": False, 
    "mode": "keyboard",
    "is_capturing": False
}
keys = []

def validate_number(p):
    return p == "" or p.isdigit()

def round_rect(c, x1, y1, x2, y2, r=5, **kw):
    pts = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r, x2,y2-r, x2,y2, x2-r,y2, x1+r,y2, x1,y2, x1,y2-r, x1,y1+r, x1,y1]
    return c.create_polygon(pts, smooth=True, **kw)

def set_window_icon():
    try:
        temp_icon_path = os.path.join(tempfile.gettempdir(), "keyboard_clicker_icon.ico")
        
        if not os.path.exists(temp_icon_path):
            img = Image.new('RGBA', (64, 64), (44, 62, 80, 255))
            draw = ImageDraw.Draw(img)
            
            for row in range(4):
                for col in range(6):
                    x = 8 + col * 8
                    y = 12 + row * 8
                    draw.rectangle([x, y, x+6, y+6], fill='#ecf0f1', outline='#95a5a6')
            
            draw.rectangle([12, 44, 52, 50], fill='#ecf0f1', outline='#95a5a6')
            img.save(temp_icon_path, format='ICO')
        
        root.iconbitmap(temp_icon_path)
    except:
        root.title("⌨️ Ultimate clicker v1.1")

def paint_ui(pressed=False):
    for (canv, rid, tid, label, sc) in keys:
        is_active = (state["mode"] == "keyboard") and ((sc == state["scan"]) or label.lower() == state["key"].lower())
        if is_active:
            color = "#e9ecef" if pressed else "#dee2e6"
            canv.itemconfig(rid, fill=color, outline=ACCENT)
        else:
            canv.itemconfig(rid, fill=KEY_BG, outline=BORDER)
    try:
        m_canv.itemconfig(m_left, fill="#e9ecef" if (state["mode"] == "left" and pressed) else ("#dee2e6" if state["mode"] == "left" else KEY_BG))
        m_canv.itemconfig(m_right, fill="#e9ecef" if (state["mode"] == "right" and pressed) else ("#dee2e6" if state["mode"] == "right" else KEY_BG))
    except: 
        pass

def clicker_loop():
    while not state["stop"]:
        if state["running"]:
            try:
                if state["mode"] == "keyboard": 
                    keyboard.press_and_release(state["key"])
                else: 
                    mouse.click(state["mode"])
            except: 
                pass
            state["count"] += 1
            if not state["stop"]:
                root.after(0, lambda: count_lbl.config(text=str(state["count"])))
                root.after(0, lambda: paint_ui(True))
                root.after(70, lambda: paint_ui(False))
            time.sleep(max(0.01, state["interval"]/1000))
        else: 
            time.sleep(0.05)

def toggle():
    if state["is_capturing"]: 
        return
    val = interval_var.get()
    state["interval"] = int(val) if val.isdigit() and val != "" else 1000
    state["running"] = not state["running"]
    update_status()

def update_status():
    if state["running"]:
        status_lbl.config(text="● Running", fg="#2b8a3e")
        toggle_btn.config(text="Stop", bg="#fa5252")
    else:
        status_lbl.config(text="○ Stopped", fg=MUTED)
        toggle_btn.config(text=f"Start ({TOGGLE_HOTKEY.upper()})", bg=PRIMARY)
    paint_ui()

def start_capture(event=None):
    if state["running"] or state["is_capturing"]: 
        return
    state["is_capturing"] = True
    
    key_entry.config(state="normal", highlightbackground=ACCENT)
    key_var.set("...")
    key_entry.config(state="readonly")
    
    def listen():
        captured = {"type": None, "value": None, "scan": None}
        stop_event = threading.Event()
        
        m_h = None
        k_h = None

        def release_hooks():
            nonlocal m_h, k_h
            if m_h: 
                mouse.unhook(m_h)
            if k_h: 
                keyboard.unhook(k_h)

        def on_mouse(e):
            if not stop_event.is_set() and isinstance(e, mouse.ButtonEvent) and e.event_type == 'down':
                captured["type"] = "mouse"
                captured["value"] = e.button
                release_hooks()
                stop_event.set()

        def on_key(e):
            if not stop_event.is_set() and e.event_type == 'down' and e.name != TOGGLE_HOTKEY:
                captured["type"] = "keyboard"
                captured["value"] = e.name
                captured["scan"] = e.scan_code
                release_hooks()
                stop_event.set()
        
        m_h = mouse.hook(on_mouse)
        k_h = keyboard.on_press(on_key)
        
        stop_event.wait()
        
        state["mode"] = captured["value"] if captured["type"] == "mouse" else "keyboard"
        state["key"] = captured["value"] if captured["type"] == "keyboard" else ""
        if captured["scan"]: 
            state["scan"] = captured["scan"]
        
        d_name = state["key"].upper() if len(state["key"]) == 1 else state["key"].capitalize()
        if state["mode"] == "left": 
            d_name = "LMB"
        elif state["mode"] == "right": 
            d_name = "RMB"
        
        def finalize():
            key_entry.config(state="normal")
            key_var.set(d_name)
            key_entry.config(state="readonly", highlightbackground=BORDER)
            state["is_capturing"] = False
            paint_ui()
            
        root.after(0, finalize)
        
    threading.Thread(target=listen, daemon=True).start()

root = tk.Tk()
root.title("Ultimate Clicker by zndlol")
root.geometry("620x500") 
root.configure(bg=BG)
root.resizable(False, False)

set_window_icon()

vcmd = (root.register(validate_number), '%P')

tk.Label(root, text="Ultimate clicker", bg=BG, fg=TEXT, font=("Arial", 18, "bold")).pack(pady=(15,2))
tk.Label(root, text=f"Click the field to assign • {TOGGLE_HOTKEY.upper()} to toggle", bg=BG, fg=MUTED, font=("Arial", 8)).pack(pady=(0,10))

card = tk.Frame(root, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
card.pack(padx=20, fill="x")

inputs = tk.Frame(card, bg=CARD)
inputs.pack(padx=10, pady=10, fill="x")

c1 = tk.Frame(inputs, bg=CARD)
c1.pack(side="left", expand=True, fill="x")
tk.Label(c1, text="Key / Button", bg=CARD, fg=TEXT, font=("Arial", 8, "bold")).pack(anchor="w")
key_var = tk.StringVar(value="Space")
key_entry = tk.Entry(c1, textvariable=key_var, state="readonly", bg=BG, fg=TEXT, font=("Arial", 9), 
                     relief="flat", highlightthickness=1, highlightbackground=BORDER, readonlybackground=BG, cursor="hand2")
key_entry.pack(fill="x", pady=2, ipady=4)
key_entry.bind("<Button-1>", start_capture)

c2 = tk.Frame(inputs, bg=CARD)
c2.pack(side="left", padx=(10,0))
tk.Label(c2, text="Interval (ms)", bg=CARD, fg=TEXT, font=("Arial", 8, "bold")).pack(anchor="w")
interval_var = tk.StringVar(value="1000")
int_entry = tk.Entry(c2, textvariable=interval_var, width=10, bg=BG, fg=TEXT, font=("Arial", 9), 
                     relief="flat", highlightthickness=1, highlightbackground=BORDER,
                     validate='key', validatecommand=vcmd)
int_entry.pack(pady=2, ipady=4)

status_bar = tk.Frame(card, bg="#f1f3f5", pady=8, padx=10)
status_bar.pack(fill="x")
status_lbl = tk.Label(status_bar, text="○ Stopped", bg="#f1f3f5", fg=MUTED, font=("Arial", 9, "bold"))
status_lbl.pack(side="left")
count_lbl = tk.Label(status_bar, text="0", bg="#f1f3f5", fg=TEXT, font=("Arial", 10, "bold"))
count_lbl.pack(side="left", padx=30)
toggle_btn = tk.Button(status_bar, text=f"Start ({TOGGLE_HOTKEY.upper()})", command=toggle, bg=PRIMARY, fg="white", font=("Arial", 9, "bold"), relief="flat", padx=20)
toggle_btn.pack(side="right")

kb_card = tk.Frame(root, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
kb_card.pack(padx=20, pady=10, fill="x")
viz_frame = tk.Frame(kb_card, bg=CARD)
viz_frame.pack(pady=10, padx=10)

ROWS = [
    [("`",1,41),("1",1,2),("2",1,3),("3",1,4),("4",1,5),("5",1,6),("6",1,7),("7",1,8),("8",1,9),("9",1,10),("0",1,11),("-",1,12),("=",1,13)],
    [("TAB",1.4,15),("Q",1,16),("W",1,17),("E",1,18),("R",1,19),("T",1,20),("Y",1,21),("U",1,22),("I",1,23),("O",1,24),("P",1,25),("[",1,26),("]",1,27)],
    [("CAPS",1.7,58),("A",1,30),("S",1,31),("D",1,32),("F",1,33),("G",1,34),("H",1,35),("J",1,36),("K",1,37),("L",1,38),(";",1,39),("'",1,40),("ENT",1.5,28)],
    [("SHFT",2.1,42),("Z",1,44),("X",1,45),("C",1,46),("V",1,47),("B",1,48),("N",1,49),("M",1,50),(",",1,51),(".",1,52),("/",1,53),("SHFT",1.7,54)],
    [("CTRL",1.2,29),("ALT",1.1,56),("Space",6.0,57),("ALT",1.1,56),("CTRL",1.2,29)]
]

kb_wrap = tk.Frame(viz_frame, bg=CARD)
kb_wrap.pack(side="left")

for row in ROWS:
    line = tk.Frame(kb_wrap, bg=CARD)
    line.pack(pady=1)
    for (label, w, sc) in row:
        width = int(28 * w) - 2
        c = tk.Canvas(line, width=width, height=28, bg=CARD, highlightthickness=0)
        rid = round_rect(c, 1, 1, width-1, 27, r=4, fill=KEY_BG, outline=BORDER)
        c.create_text(width/2, 14, text=label, fill=MUTED, font=("Arial", 6, "bold"))
        c.pack(side="left", padx=1)
        keys.append((c, rid, 0, label, sc))

m_frame = tk.Frame(viz_frame, bg=CARD, padx=15)
m_frame.pack(side="left")
m_canv = tk.Canvas(m_frame, width=50, height=80, bg=CARD, highlightthickness=0)
m_canv.pack()
round_rect(m_canv, 2, 2, 48, 78, r=15, fill=CARD, outline=BORDER, width=1)
m_left = round_rect(m_canv, 6, 6, 23, 35, r=5, fill=KEY_BG, outline=BORDER)
m_right = round_rect(m_canv, 26, 6, 43, 35, r=5, fill=KEY_BG, outline=BORDER)

keyboard.add_hotkey(TOGGLE_HOTKEY, toggle)
threading.Thread(target=clicker_loop, daemon=True).start()

root.protocol("WM_DELETE_WINDOW", lambda: (state.update({"stop":True}), root.destroy(), os._exit(0)))
root.mainloop()