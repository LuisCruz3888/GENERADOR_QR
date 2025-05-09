# -*- coding: utf-8 -*-
import qrcode
from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox

def generar_vcard():
    nombre = entry_nombre.get().strip()
    apellido = entry_apellido.get().strip()
    empresa = entry_empresa.get().strip()
    cargo = entry_cargo.get().strip()
    telefono = entry_telefono.get().strip()
    email = entry_email.get().strip()
    web = entry_web.get().strip()
    direccion = entry_direccion.get().strip()
    ciudad = entry_ciudad.get().strip()
    codpostal = entry_codpostal.get().strip()
    pais = entry_pais.get().strip()

    if not nombre or not telefono:
        messagebox.showerror("Error", "Nombre y teléfono son obligatorios.")
        return

    vcard = f"""BEGIN:VCARD
VERSION:3.0
N:{apellido};{nombre};;;
FN:{nombre} {apellido}
ORG:{empresa}
TITLE:{cargo}
TEL;TYPE=CELL:{telefono}
EMAIL:{email}
URL:{web}
ADR;TYPE=WORK:;;{direccion};{ciudad};;{codpostal};{pais}
END:VCARD
"""
    return vcard

def generar_qr():
    vcard = generar_vcard()
    if not vcard:
        return

    try:
        espacio_ratio = float(entry_ratio.get())
        if not 0.1 <= espacio_ratio <= 0.7:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Porcentaje debe estar entre 0.1 y 0.7")
        return

    # Crear QR
    qr = qrcode.QRCode(
        version=6,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(vcard)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    ancho, alto = img.size
    tamano_centro = int(ancho * espacio_ratio)

    x = (ancho - tamano_centro) // 2
    y = (alto - tamano_centro) // 2

    draw = ImageDraw.Draw(img)
    draw.rectangle([x, y, x + tamano_centro, y + tamano_centro], fill="white")

    # Mostrar QR
    global img_tk
    img_tk = ImageTk.PhotoImage(img.resize((250, 250)))
    canvas.create_image(125, 125, image=img_tk)

    # Guardar archivo
    path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("Imagen PNG", "*.png")])
    if path:
        img.save(path)
        messagebox.showinfo("Éxito", f"QR guardado:\n{path}")

# Interfaz
root = tk.Tk()
root.title("Generador de QR con vCard")

campos = [
    ("Nombre", "entry_nombre"),
    ("Apellido", "entry_apellido"),
    ("Empresa", "entry_empresa"),
    ("Cargo", "entry_cargo"),
    ("Teléfono", "entry_telefono"),
    ("Email", "entry_email"),
    ("Página web", "entry_web"),
    ("Dirección", "entry_direccion"),
    ("Ciudad", "entry_ciudad"),
    ("Código Postal", "entry_codpostal"),
    ("País", "entry_pais")
]

entries = {}
for i, (label, varname) in enumerate(campos):
    tk.Label(root, text=label + ":").grid(row=i, column=0, sticky="e")
    entry = tk.Entry(root, width=40)
    entry.grid(row=i, column=1, pady=2)
    entries[varname] = entry

globals().update(entries)

tk.Label(root, text="Espacio central (0.1 - 0.7):").grid(row=len(campos), column=0, sticky="e")
entry_ratio = tk.Entry(root, width=10)
entry_ratio.insert(0, "0.4")
entry_ratio.grid(row=len(campos), column=1, sticky="w", pady=5)

btn_generar = tk.Button(root, text="Generar QR de contacto", command=generar_qr)
btn_generar.grid(row=len(campos)+1, column=0, columnspan=2, pady=10)

canvas = tk.Canvas(root, width=250, height=250, bg="white")
canvas.grid(row=len(campos)+2, column=0, columnspan=2, pady=10)

root.mainloop()
