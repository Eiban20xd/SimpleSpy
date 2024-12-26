import tkinter as tk
from tkinter import scrolledtext
import psutil
import webbrowser
import subprocess

class SimpleSpyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SimpleSpy")
        self.root.geometry("620x420")  
        self.root.configure(bg='white')

        title_label = tk.Label(root, text="SimpleSpy", font=("Arial", 24, "bold"), bg='white', fg='black')
        title_label.pack(pady=20)

        subtitle_label = tk.Label(root, text="Creado por Eiban20", font=("Arial", 12), bg='white', fg='black')
        subtitle_label.pack(pady=5)

        self.text_area = scrolledtext.ScrolledText(root, width=70, height=15, bg='lightyellow', fg='black', font=("Arial", 10))
        self.text_area.pack(pady=10)

        button_frame = tk.Frame(root, bg='white')
        button_frame.pack(pady=5)

        self.clear_button = tk.Button(button_frame, text="Vaciar Registro", command=self.clear_log, bg='orange', fg='black', width=15)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.start_button = tk.Button(button_frame, text="Empezar a Registrar", command=self.start_logging, bg='blue', fg='white', width=15)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.execute_button = tk.Button(button_frame, text="Ejecutar Registro", command=self.open_execute_window, bg='purple', fg='white', width=15)
        self.execute_button.pack(side=tk.LEFT, padx=5)

        self.discord_button = tk.Button(button_frame, text="Abrir Discord", command=self.open_discord, bg='green', fg='white', width=15)
        self.discord_button.pack(side=tk.LEFT, padx=5)

        self.processes = set()  
        self.is_logging = False
        self.logged_messages = set()  

    def start_logging(self):
        """Inicia o termina el registro de aplicaciones abiertas."""
        if not self.is_logging:
            self.is_logging = True
            self.start_button.config(text="Terminar de Registrar", bg='red')
            self.check_open_apps()
            self.text_area.insert(tk.END, "Registro de aplicaciones iniciado:\n\n")
        else:
            self.is_logging = False
            self.start_button.config(text="Empezar a Registrar", bg='blue')

    def check_open_apps(self):
        """Verifica y registra las aplicaciones abiertas en un bucle."""
        if self.is_logging:
            current_apps = self.get_open_apps()
            new_apps = current_apps - self.processes  
            closed_apps = self.processes - current_apps  

            for app in new_apps:
                if app not in self.logged_messages:  
                    self.text_area.insert(tk.END, f"Aplicación iniciada: {app}\n\n")
                    self.logged_messages.add(app)

            for app in closed_apps:
                close_message = f"Aplicación cerrada: {app}\n\n"
                if close_message not in self.logged_messages:  
                    self.text_area.insert(tk.END, close_message)
                    self.logged_messages.add(close_message)

            self.text_area.see(tk.END)  
            self.processes = current_apps  
            self.root.after(2000, self.check_open_apps)  
    def get_open_apps(self):
        """Obtiene una lista de aplicaciones abiertas."""
        apps = set()
        for process in psutil.process_iter(['name', 'exe']):
            try:
                if process.info['name'] and 'python' not in process.info['name']:  
                    apps.add(f"{process.info['name']} - Ruta: {process.info['exe']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return apps

    def clear_log(self):
        """Vacía el registro de texto sin añadir mensaje de registro vacío."""
        self.text_area.delete(1.0, tk.END)  
        self.logged_messages.clear()  

    def open_discord(self):
        """Abre el enlace de Discord en el navegador predeterminado."""
        webbrowser.open("https://discord.gg/WDhYYTUbKg")

    def open_execute_window(self):
        """Abre una nueva ventana para ejecutar un registro manual."""
        self.execute_window = tk.Toplevel(self.root)
        self.execute_window.title("Ejecutar Registro")
        self.execute_window.geometry("400x200")
        self.execute_window.configure(bg='white')

        self.execute_text_area = scrolledtext.ScrolledText(self.execute_window, width=50, height=5, bg='lightyellow', fg='black', font=("Arial", 10))
        self.execute_text_area.pack(pady=10)

        self.execute_button = tk.Button(self.execute_window, text="Execute", command=self.execute_record, bg='blue', fg='white')
        self.execute_button.pack(pady=5)

    def execute_record(self):
        """Ejecuta o cierra el registro pegado en el área de texto."""
        record = self.execute_text_area.get(1.0, tk.END).strip()
        if record:
            parts = record.split(' - Ruta: ')
            if len(parts) == 2:
                app_name = parts[0].replace('Aplicación iniciada: ', '').replace('Aplicación cerrada: ', '').strip()
                app_path = parts[1].strip()

                if "Aplicación iniciada:" in record:
                    try:
                        subprocess.Popen(app_path)  
                    except Exception as e:
                        self.text_area.insert(tk.END, f"Error al iniciar la aplicación: {e}\n\n")
                elif "Aplicación cerrada:" in record:
                    self.close_application(app_name)

    def close_application(self, app_name):
        """Cierra la aplicación dada su nombre, forzando el cierre si es necesario."""
        found = False
        for process in psutil.process_iter(['name']):
            if process.info['name'] == app_name.split('.')[0] + '.exe':  
                try:
                    process.terminate()  
                    found = True
                except psutil.NoSuchProcess:
                    continue
                except psutil.AccessDenied:
                    continue
                except Exception as e:
                    self.text_area.insert(tk.END, f"Error al cerrar la aplicación: {e}\n\n")
        if not found:
            self.text_area.insert(tk.END, f"No se encontró la aplicación {app_name} para cerrar.\n\n")

def main():
    root = tk.Tk()
    app = SimpleSpyApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
