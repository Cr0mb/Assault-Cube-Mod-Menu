import os
import pymem
import pymem.process
import logging
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import threading

logging.basicConfig(filename='ac_client_hack.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

process_name = "ac_client.exe"
base_address = 0x400000
local_entity_pointer_offset = 0x17E0A8

offset_health = 0xEC
offset_current_ammo = 0x140
offset_magazine_ammo = 0x11C
offset_pistol_current_ammo = 0x12C
offset_pistol_magazine_ammo = 0x108
offset_grenade_ammo = 0x144
offset_kevlar = 0xF0
offset_name = 0x205

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_local_entity_address(pm):
    try:
        module = pymem.process.module_from_name(pm.process_handle, process_name)
        base = module.lpBaseOfDll
        local_entity_addr = pm.read_int(base + local_entity_pointer_offset)
        return local_entity_addr
    except pymem.exception.MemoryReadError as e:
        logging.error(f"Memory read error: {e}")
        raise

def change_value(pm, local_entity_addr, offset, value, value_type):
    try:
        if value_type == 'int':
            pm.write_int(local_entity_addr + offset, value)
        elif value_type == 'float':
            pm.write_float(local_entity_addr + offset, value)
        logging.info(f"Value at offset {hex(offset)} set to: {value}")
    except pymem.exception.MemoryWriteError as e:
        logging.error(f"Failed to write value at offset {hex(offset)}: {e}")
        messagebox.showerror("Error", f"Failed to write value at offset {hex(offset)}: {e}")

def change_name(pm, local_entity_addr, new_name):
    try:
        pm.write_string(local_entity_addr + offset_name, new_name)
        logging.info(f"Name set to: {new_name}")
    except pymem.exception.MemoryWriteError as e:
        logging.error(f"Failed to write name: {e}")
        messagebox.showerror("Error", f"Failed to write name: {e}")

def update_value(event, pm, local_entity_addr, offset, value_type, entry):
    try:
        new_value = entry.get()
        if value_type == 'int':
            new_value = int(new_value)
        elif value_type == 'float':
            new_value = float(new_value)
        elif value_type == 'string':
            change_name(pm, local_entity_addr, new_value)
            entry.delete(0, tk.END)
            entry.insert(0, new_value)
            return
        
        change_value(pm, local_entity_addr, offset, new_value, value_type)
        current_value = pm.read_int(local_entity_addr + offset) if value_type == 'int' else ""
        entry.delete(0, tk.END)
        entry.insert(0, str(current_value))
    except ValueError:
        messagebox.showerror("Error", "Invalid input. Please enter a valid number.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def toggle_god_mode(pm, local_entity_addr, god_mode_button, god_mode_var):
    if god_mode_var.get() == 0:
        change_value(pm, local_entity_addr, offset_health, 9999, 'int')
        change_value(pm, local_entity_addr, offset_kevlar, 9999, 'int')
        god_mode_button.config(text="God Mode On", bg='#4CAF50', activebackground='#388E3C')
        god_mode_var.set(1)
    else:
        change_value(pm, local_entity_addr, offset_health, 100, 'int')
        change_value(pm, local_entity_addr, offset_kevlar, 0, 'int')
        god_mode_button.config(text="God Mode Off", bg='#FF5722', activebackground='#E64A19')
        god_mode_var.set(0)

def toggle_unlimited_ammo(pm, local_entity_addr, unlimited_ammo_button, unlimited_ammo_var):
    if unlimited_ammo_var.get() == 0:
        change_value(pm, local_entity_addr, offset_current_ammo, 9999, 'int')
        change_value(pm, local_entity_addr, offset_magazine_ammo, 9999, 'int')
        change_value(pm, local_entity_addr, offset_pistol_current_ammo, 9999, 'int')
        change_value(pm, local_entity_addr, offset_pistol_magazine_ammo, 9999, 'int')
        change_value(pm, local_entity_addr, offset_grenade_ammo, 9999, 'int')
        unlimited_ammo_button.config(text="Unlimited Ammo On", bg='#4CAF50', activebackground='#388E3C')
        unlimited_ammo_var.set(1)
    else:
        change_value(pm, local_entity_addr, offset_current_ammo, 100, 'int')
        change_value(pm, local_entity_addr, offset_magazine_ammo, 100, 'int')
        change_value(pm, local_entity_addr, offset_pistol_current_ammo, 100, 'int')
        change_value(pm, local_entity_addr, offset_pistol_magazine_ammo, 100, 'int')
        change_value(pm, local_entity_addr, offset_grenade_ammo, 0, 'int')
        unlimited_ammo_button.config(text="Unlimited Ammo Off", bg='#FF5722', activebackground='#E64A19')
        unlimited_ammo_var.set(0)

def monitor_values(pm, local_entity_addr, god_mode_button, god_mode_var, unlimited_ammo_button, unlimited_ammo_var):
    while True:
        try:
            if god_mode_var.get() == 1:
                if pm.read_int(local_entity_addr + offset_health) != 9999:
                    change_value(pm, local_entity_addr, offset_health, 9999, 'int')
                if pm.read_int(local_entity_addr + offset_kevlar) != 9999:
                    change_value(pm, local_entity_addr, offset_kevlar, 9999, 'int')
            if unlimited_ammo_var.get() == 1:
                if pm.read_int(local_entity_addr + offset_current_ammo) != 9999:
                    change_value(pm, local_entity_addr, offset_current_ammo, 9999, 'int')
                if pm.read_int(local_entity_addr + offset_magazine_ammo) != 9999:
                    change_value(pm, local_entity_addr, offset_magazine_ammo, 9999, 'int')
                if pm.read_int(local_entity_addr + offset_pistol_current_ammo) != 9999:
                    change_value(pm, local_entity_addr, offset_pistol_current_ammo, 9999, 'int')
                if pm.read_int(local_entity_addr + offset_pistol_magazine_ammo) != 9999:
                    change_value(pm, local_entity_addr, offset_pistol_magazine_ammo, 9999, 'int')
                if pm.read_int(local_entity_addr + offset_grenade_ammo) != 9999:
                    change_value(pm, local_entity_addr, offset_grenade_ammo, 9999, 'int')
        except pymem.exception.MemoryReadError as e:
            logging.error(f"Memory read error during monitoring: {e}")
        except pymem.exception.MemoryWriteError as e:
            logging.error(f"Memory write error during monitoring: {e}")

def exit_application(root):
    root.destroy()
    os._exit(0)

def main():
    try:
        pm = pymem.Pymem(process_name)
        local_entity_addr = get_local_entity_address(pm)
        
        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes('-alpha', 0.9)
        root.configure(bg='#263238')
        
        canvas = tk.Canvas(root, bg='#263238', width=950, height=350)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        title_label = tk.Label(canvas, text="Assault Cube Mod Menu", font=('Helvetica', 14, 'bold'), bg='#263238', fg='#FFFFFF')
        title_label.grid(row=0, column=0, columnspan=4, pady=10)
        
        title_label = tk.Label(canvas, text="Made By: GitHub.com/Cr0mb/", font=('Helvetica', 10, 'bold'), bg='#263238', fg='#FFFFFF')
        title_label.grid(row=1, column=0, columnspan=4, pady=10)
        
        def create_option_widgets(options_list, column):
            for idx, (option, offset, value_type) in enumerate(options_list):
                label = tk.Label(canvas, text=option, bg='#263238', fg='#FFFFFF')
                label.grid(row=idx+2, column=column, sticky='w', padx=10, pady=5)
                entry = tk.Entry(canvas, width=20, bg='#455A64', fg='#FFFFFF', insertbackground='#FFFFFF')
                current_value = pm.read_string(local_entity_addr + offset, 32) if value_type == 'string' else pm.read_int(local_entity_addr + offset)
                entry.insert(0, str(current_value))
                entry.grid(row=idx+2, column=column + 1, padx=10, pady=5, sticky='e')
                entry.bind('<Return>', lambda event, pm=pm, local_entity_addr=local_entity_addr, offset=offset, value_type=value_type, entry=entry: update_value(event, pm, local_entity_addr, offset, value_type, entry))
                entry.bind('<Enter>', lambda event, entry=entry: entry.config(bg='#546E7A'))
                entry.bind('<Leave>', lambda event, entry=entry: entry.config(bg='#455A64'))
        
        options_part1 = [
            ("Health", offset_health, 'int'),
            ("Current Ammo", offset_current_ammo, 'int'),
            ("Magazine Ammo", offset_magazine_ammo, 'int'),
            ("Pistol Current Ammo", offset_pistol_current_ammo, 'int')
        ]
        
        options_part2 = [
            ("Pistol Magazine Ammo", offset_pistol_magazine_ammo, 'int'),
            ("Grenade Ammo", offset_grenade_ammo, 'int'),
            ("Kevlar", offset_kevlar, 'int'),
            ("Name", offset_name, 'string')
        ]
        
        create_option_widgets(options_part1, 0)
        create_option_widgets(options_part2, 2)

        image_path = "crumb.jpg"
        if os.path.exists(image_path):
            image = Image.open(image_path)
            image = image.resize((60, 85), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            img_label = tk.Label(canvas, image=photo, bg='#263238')
            img_label.image = photo
            img_label.grid(row=4, column=4, rowspan=len(options_part1) + len(options_part2), padx=10, pady=10)
        
        god_mode_var = tk.IntVar()
        god_mode_button = tk.Button(canvas, text="God Mode Off", bg='#009688', fg='#FFFFFF', activebackground='#00796B',
                                    command=lambda: toggle_god_mode(pm, local_entity_addr, god_mode_button, god_mode_var))
        god_mode_button.grid(row=len(options_part1)+2, column=0, padx=10, pady=5, sticky='w', columnspan=2)
        god_mode_button.bind('<Enter>', lambda event, button=god_mode_button: button.config(bg='#00796B'))
        god_mode_button.bind('<Leave>', lambda event, button=god_mode_button: button.config(bg='#009688'))

        unlimited_ammo_var = tk.IntVar()
        unlimited_ammo_button = tk.Button(canvas, text="Unlimited Ammo Off", bg='#009688', fg='#FFFFFF', activebackground='#00796B',
                                          command=lambda: toggle_unlimited_ammo(pm, local_entity_addr, unlimited_ammo_button, unlimited_ammo_var))
        unlimited_ammo_button.grid(row=len(options_part1)+2, column=2, padx=10, pady=5, sticky='w')
        unlimited_ammo_button.bind('<Enter>', lambda event, button=unlimited_ammo_button: button.config(bg='#00796B'))
        unlimited_ammo_button.bind('<Leave>', lambda event, button=unlimited_ammo_button: button.config(bg='#009688'))

        def start_move(event):
            root.x = event.x
            root.y = event.y

        def stop_move(event):
            root.x = None
            root.y = None

        def do_move(event):
            deltax = event.x - root.x
            deltay = event.y - root.y
            x = root.winfo_x() + deltax
            y = root.winfo_y() + deltay
            root.geometry(f"+{x}+{y}")

        canvas.bind("<ButtonPress-1>", start_move)
        canvas.bind("<ButtonRelease-1>", stop_move)
        canvas.bind("<B1-Motion>", do_move)

        exit_button = tk.Button(canvas, text="Exit", bg='#FF5722', fg='#FFFFFF', activebackground='#E64A19', command=lambda: exit_application(root))
        exit_button.grid(row=len(options_part1)+2, column=3, padx=10, pady=10, sticky='se')

        def keep_on_top():
            root.attributes("-topmost", True)
            root.after(100, keep_on_top)

        keep_on_top()

        monitor_thread = threading.Thread(target=monitor_values, args=(pm, local_entity_addr, god_mode_button, god_mode_var, unlimited_ammo_button, unlimited_ammo_var), daemon=True)
        monitor_thread.start()
        
        root.mainloop()

    except pymem.process.ProcessNotFound:
        logging.error(f"Process '{process_name}' not found.")
        messagebox.showerror("Error", f"Process '{process_name}' not found.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    main()
