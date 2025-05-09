# -*- coding: utf-8 -*-
import qrcode
from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox

def generar_qr():
    url = entry_url.get().strip()
    try:
        espacio_ratio = float(entry_ratio.get())
        if not 0.1 <= espacio_ratio <= 0.7:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Porcentaje debe estar entre 0.1 y 0.7")
        return

    if not url:
        messagebox.showerror("Error", "Debes ingresar una URL o texto.")
        return

    # Generar QR
    qr = qrcode.QRCode(
        version=6,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    ancho, alto = img.size
    tamano_centro = int(ancho * espacio_ratio)

    x = (ancho - tamano_centro) // 2
    y = (alto - tamano_centro) // 2

    draw = ImageDraw.Draw(img)
    draw.rectangle([x, y, x + tamano_centro, y + tamano_centro], fill="white")

    # Mostrar en interfaz
    global img_tk
    img_tk = ImageTk.PhotoImage(img.resize((250, 250)))
    canvas.create_image(125, 125, image=img_tk)

    # Guardar archivo
    path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("Imagen PNG", "*.png")])
    if path:
        img.save(path)
        messagebox.showinfo("Éxito", f"Código QR guardado como:\n{path}")

# Interfaz
root = tk.Tk()
root.title("Generador de QR con espacio central")

tk.Label(root, text="URL o texto para el QR:").grid(row=0, column=0, sticky="e")
entry_url = tk.Entry(root, width=40)
entry_url.grid(row=0, column=1, pady=5)

tk.Label(root, text="Espacio central (0.1 - 0.7):").grid(row=1, column=0, sticky="e")
entry_ratio = tk.Entry(root, width=10)
entry_ratio.insert(0, "0.4")
entry_ratio.grid(row=1, column=1, sticky="w", pady=5)

btn_generar = tk.Button(root, text="Generar QR", command=generar_qr)
btn_generar.grid(row=2, column=0, columnspan=2, pady=10)

canvas = tk.Canvas(root, width=250, height=250, bg="white")
canvas.grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()
