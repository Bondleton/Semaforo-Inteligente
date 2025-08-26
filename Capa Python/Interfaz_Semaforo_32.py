import tkinter as tk
from tkinter import font as tkfont
import requests
from PIL import Image, ImageTk  # <- Pillow

# ==========================
# CONFIGURACIÓN BÁSICA
# ==========================
esp32_ip = "172.26.161.254"  # Asegúrese de que esté en la misma red

COLORES = {
    "fondo": "#2E3440",
    "sidebar": "#3B4252",
    "texto": "#E5E9F0",
    "verde": "#A3BE8C",
    "verde_oscuro": "#5b6f49",
    "amarillo": "#EBCB8B",
    "amarillo_oscuro": "#dea97e",
    "rojo": "#BF616A",
    "rojo_oscuro": "#a64358",
    "boton_cerrar": "#5E81AC",
    "sombra": "#4C566A"
}

# Rutas de imágenes
RUTAS_IMAGENES = {
    "rojo":     {"on": r"D:\Arquitectura de Software\rojo_on.png",      "off": r"D:\Arquitectura de Software\rojo_off.png"},
    "amarillo": {"on": r"D:\Arquitectura de Software\amarillo_on.png",  "off": r"D:\Arquitectura de Software\amarillo_off.png"},
    "verde":    {"on": r"D:\Arquitectura de Software\verde_on.png",     "off": r"D:\Arquitectura de Software\verde_off.png"},
}

# Tamaño estandarizado para las imágenes (ancho, alto)
IMAGE_SIZE = (120, 120)  # ajuste a conveniencia

# Estado local de los LEDs
estado_leds = {"verde": False, "amarillo": False, "rojo": False}

# ==========================
# UTILIDADES DE IMAGEN (Pillow)
# ==========================
def cargar_imagen_redimensionada(ruta, size=IMAGE_SIZE):
    """
    Carga una imagen con Pillow, la redimensiona a 'size' y devuelve un ImageTk.PhotoImage.
    """
    try:
        # Si desea mantener proporción exacta sin deformar, use thumbnail en lugar de resize.
        img_raw = Image.open(ruta).convert("RGBA").resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img_raw)
    except Exception as e:
        raise RuntimeError(f"No se pudo cargar la imagen '{ruta}': {e}")

def cargar_set_imagenes():
    """
    Carga y redimensiona todas las imágenes ON/OFF para cada color.
    Retorna un dict: imagenes[color]['on'|'off'] -> ImageTk.PhotoImage
    """
    imgs = {}
    for color, estados in RUTAS_IMAGENES.items():
        imgs[color] = {
            "on":  cargar_imagen_redimensionada(estados["on"]),
            "off": cargar_imagen_redimensionada(estados["off"])
        }
    return imgs

# ==========================
# CALLBACKS / LÓGICA CLIENTE
# ==========================
def Close_Window():
    cuadro.destroy()

def toggle_led(color):
    """Alterna el foco en el ESP32 y refleja el cambio en la GUI."""
    try:
        response = requests.get(f"http://{esp32_ip}/led/{color}/toggle", timeout=3)
        print(response.text)
        estado_leds[color] = not estado_leds[color]
        actualizar_estado(color)
        actualizar_semaforo(color, "on" if estado_leds[color] else "off")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def actualizar_estado(color):
    """Actualiza etiquetas de estado y color de botones."""
    estado = "ENCENDIDO" if estado_leds[color] else "APAGADO"
    color_texto = COLORES["verde"] if estado_leds[color] else COLORES["rojo"]

    if color == "verde":
        estado_verde.config(text=estado, fg=color_texto)
        boton_verde.config(bg=COLORES["verde"] if estado_leds[color] else COLORES["verde_oscuro"])
    elif color == "amarillo":
        estado_amarillo.config(text=estado, fg=color_texto)
        boton_amarillo.config(bg=COLORES["amarillo"] if estado_leds[color] else COLORES["amarillo_oscuro"])
    elif color == "rojo":
        estado_rojo.config(text=estado, fg=color_texto)
        boton_rojo.config(bg=COLORES["rojo"] if estado_leds[color] else COLORES["rojo_oscuro"])

def iniciar_rutina():
    try:
        response = requests.get(f"http://{esp32_ip}/rutina/semaforo/on", timeout=3)
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def apagar_rutina():
    try:
        response = requests.get(f"http://{esp32_ip}/rutina/semaforo/off", timeout=3)
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def enviar_tiempo_verde(event):
    valor = slider_tiempo_verde.get()
    _enviar_tiempo("verde", valor, slider_tiempo_verde)

def enviar_tiempo_amarillo(event):
    valor = slider_tiempo_amarillo.get()
    _enviar_tiempo("amarillo", valor, slider_tiempo_amarillo)

def enviar_tiempo_rojo(event):
    valor = slider_tiempo_rojo.get()
    _enviar_tiempo("rojo", valor, slider_tiempo_rojo)

def _enviar_tiempo(color, valor, widget_slider):
    try:
        response = requests.get(f"http://{esp32_ip}/tiempo/{color}?tiempo={valor}", timeout=3)
        print(response.text)
        widget_slider.config(fg=COLORES[color] if color in COLORES else COLORES["texto"])
        cuadro.after(900, lambda: widget_slider.config(fg=COLORES["texto"]))
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        widget_slider.config(fg=COLORES["rojo"])
        cuadro.after(900, lambda: widget_slider.config(fg=COLORES["texto"]))

# ==========================
# GUI
# ==========================
cuadro = tk.Tk()
cuadro.title("Control de Semáforo Inteligente")
cuadro.configure(bg="black")
try:
    cuadro.state("zoomed")  # Windows
except Exception:
    cuadro.attributes("-zoomed", True)  # Linux

# Fuentes
fuente_titulo = tkfont.Font(family="Helvetica", size=16, weight="bold")
fuente_botones = tkfont.Font(family="Helvetica", size=12)
fuente_estado = tkfont.Font(family="Helvetica", size=14, weight="bold")

# Sidebar
sidebar = tk.Frame(cuadro, bg=COLORES["sidebar"], width=260)
sidebar.pack(side="left", fill="y")

# Main frame
main_frame = tk.Frame(cuadro, bg=COLORES["fondo"])
main_frame.pack(side="right", expand=True, fill="both")

# Título
titulo = tk.Label(sidebar, text="Control de Semáforo 🚦",
                  bg=COLORES["sidebar"], fg=COLORES["texto"], font=fuente_titulo)
titulo.pack(pady=30)

# ---------- Sección Verde ----------
frame_verde = tk.Frame(sidebar, bg=COLORES["sidebar"])
frame_verde.pack(pady=10)

tk.Label(frame_verde, text="LED Verde", bg=COLORES["sidebar"],
         fg=COLORES["texto"], font=fuente_botones).pack()

boton_verde = tk.Button(frame_verde, text="Encender/Apagar", bg=COLORES["verde_oscuro"],
                        fg="white", font=fuente_botones, relief="flat",
                        command=lambda: toggle_led("verde"))
boton_verde.pack(pady=5, fill="x")

slider_tiempo_verde = tk.Scale(frame_verde, from_=1, to=10, orient="horizontal",
                               label="Tiempo Verde (segundos)", length=200,
                               bg=COLORES["sidebar"], fg=COLORES["texto"],
                               troughcolor=COLORES["verde_oscuro"], highlightthickness=0)
slider_tiempo_verde.set(3)
slider_tiempo_verde.pack(pady=10)
slider_tiempo_verde.bind("<ButtonRelease-1>", enviar_tiempo_verde)

# ---------- Sección Amarillo ----------
frame_amarillo = tk.Frame(sidebar, bg=COLORES["sidebar"])
frame_amarillo.pack(pady=10)

tk.Label(frame_amarillo, text="LED Amarillo", bg=COLORES["sidebar"],
         fg=COLORES["texto"], font=fuente_botones).pack()

boton_amarillo = tk.Button(frame_amarillo, text="Encender/Apagar", bg=COLORES["amarillo_oscuro"],
                           fg="white", font=fuente_botones, relief="flat",
                           command=lambda: toggle_led("amarillo"))
boton_amarillo.pack(pady=5, fill="x")

slider_tiempo_amarillo = tk.Scale(frame_amarillo, from_=1, to=10, orient="horizontal",
                                  label="Tiempo Amarillo (segundos)", length=200,
                                  bg=COLORES["sidebar"], fg=COLORES["texto"],
                                  troughcolor=COLORES["amarillo_oscuro"], highlightthickness=0)
slider_tiempo_amarillo.set(1)
slider_tiempo_amarillo.pack(pady=10)
slider_tiempo_amarillo.bind("<ButtonRelease-1>", enviar_tiempo_amarillo)

# ---------- Sección Rojo ----------
frame_rojo = tk.Frame(sidebar, bg=COLORES["sidebar"])
frame_rojo.pack(pady=10)

tk.Label(frame_rojo, text="LED Rojo", bg=COLORES["sidebar"],
         fg=COLORES["texto"], font=fuente_botones).pack()

boton_rojo = tk.Button(frame_rojo, text="Encender/Apagar", bg=COLORES["rojo_oscuro"],
                       fg="white", font=fuente_botones, relief="flat",
                       command=lambda: toggle_led("rojo"))
boton_rojo.pack(pady=5, fill="x")

slider_tiempo_rojo = tk.Scale(frame_rojo, from_=1, to=10, orient="horizontal",
                              label="Tiempo Rojo (segundos)", length=200,
                              bg=COLORES["sidebar"], fg=COLORES["texto"],
                              troughcolor=COLORES["rojo_oscuro"], highlightthickness=0)
slider_tiempo_rojo.set(2)
slider_tiempo_rojo.pack(pady=10)
slider_tiempo_rojo.bind("<ButtonRelease-1>", enviar_tiempo_rojo)

# ---------- Botones de rutina ----------
frame_rutina = tk.Frame(sidebar, bg=COLORES["sidebar"])
frame_rutina.pack(pady=20)

boton_rutina_on = tk.Button(frame_rutina, text="Iniciar Rutina", bg=COLORES["verde"],
                            fg="white", font=fuente_botones, relief="flat",
                            command=iniciar_rutina)
boton_rutina_on.pack(pady=5,  fill="x")

boton_rutina_off = tk.Button(frame_rutina, text="Apagar Rutina", bg=COLORES["rojo"],
                             fg="white", font=fuente_botones, relief="flat",
                             command=apagar_rutina)
boton_rutina_off.pack(pady=5,  fill="x")

# ---------- Botón cerrar ----------
boton_cerrar = tk.Button(sidebar, text="Cerrar", bg=COLORES["boton_cerrar"],
                         fg="white", font=fuente_botones, relief="flat",
                         command=Close_Window)
boton_cerrar.pack(side="bottom", pady=20)

# ==========================
# PANEL DE ESTADO (texto)
# ==========================
estado_frame = tk.Frame(main_frame, bg=COLORES["fondo"])
estado_frame.grid(row=0, column=0, padx=50, pady=200, sticky="n")

tk.Label(estado_frame, text="Estado Actual", bg=COLORES["fondo"],
         fg=COLORES["texto"], font=fuente_titulo).pack()

tk.Label(estado_frame, text="Verde:", bg=COLORES["fondo"],
         fg=COLORES["texto"], font=fuente_estado).pack(pady=10)
estado_verde = tk.Label(estado_frame, text="APAGADO", bg=COLORES["fondo"],
                        fg=COLORES["rojo"], font=fuente_estado)
estado_verde.pack()

tk.Label(estado_frame, text="Amarillo:", bg=COLORES["fondo"],
         fg=COLORES["texto"], font=fuente_estado).pack(pady=10)
estado_amarillo = tk.Label(estado_frame, text="APAGADO", bg=COLORES["fondo"],
                           fg=COLORES["rojo"], font=fuente_estado)
estado_amarillo.pack()

tk.Label(estado_frame, text="Rojo:", bg=COLORES["fondo"],
         fg=COLORES["texto"], font=fuente_estado).pack(pady=10)
estado_rojo = tk.Label(estado_frame, text="APAGADO", bg=COLORES["fondo"],
                       fg=COLORES["rojo"], font=fuente_estado)
estado_rojo.pack()

# ==========================
# SEMÁFORO EN CANVAS (fondo + focos)
# ==========================
semaforo_frame = tk.Frame(main_frame, bg=COLORES["fondo"])
semaforo_frame.grid(row=0, column=1, padx=50, pady=100, sticky="n")

# Canvas donde dibujaremos la "cajita" del semáforo
ANCHO = 180
ALTO  = 420
sem_bg = tk.Canvas(semaforo_frame, width=ANCHO, height=ALTO,
                   bg=COLORES["fondo"], highlightthickness=0)
sem_bg.pack()

def rounded_rect(canvas, x1, y1, x2, y2, r=20, **kwargs):
    """Dibuja un rectángulo con esquinas redondeadas en Canvas."""
    points = [
        x1+r, y1,
        x2-r, y1,
        x2, y1,
        x2, y1+r,
        x2, y2-r,
        x2, y2,
        x2-r, y2,
        x1+r, y2,
        x1, y2,
        x1, y2-r,
        x1, y1+r,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

# Fondo/caja del semáforo
MARGEN = 20
rect_fondo = rounded_rect(
    sem_bg,
    MARGEN, MARGEN,
    ANCHO - MARGEN, ALTO - MARGEN,
    r=25,
    fill="#4C566A", outline=""  # puede usar outline="#3B4252", width=2
)

# Cargar y redimensionar imágenes usando Pillow
imagenes = cargar_set_imagenes()

# Posiciones de las luces (centros)
cx = ANCHO // 2
cy_verde     = 90
cy_amarillo = 210
cy_rojo    = 330

# Crear imágenes en el Canvas (inician en OFF)
luz_verde_img  = sem_bg.create_image(cx, cy_verde,     image=imagenes["verde"]["off"])
luz_amar_img  = sem_bg.create_image(cx, cy_amarillo, image=imagenes["amarillo"]["off"])
luz_roja_img = sem_bg.create_image(cx, cy_rojo,    image=imagenes["rojo"]["off"])

def actualizar_semaforo(color, accion):
    """Cambia la imagen del foco correspondiente entre ON/OFF en el Canvas."""
    img = imagenes[color]["on" if accion == "on" else "off"]
    if color == "verde":
        sem_bg.itemconfig(luz_verde_img, image=img)
    elif color == "amarillo":
        sem_bg.itemconfig(luz_amar_img, image=img)
    elif color == "rojo":
        sem_bg.itemconfig(luz_roja_img, image=img)

# Distribución del main_frame
main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)

# Lanzar GUI
cuadro.mainloop()