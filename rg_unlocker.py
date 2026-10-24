import os
import re
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from urllib.parse import urlparse, unquote
import webbrowser
import urllib.request
import urllib.error
import html

APP_TITLE = "RG Unlocker Desktop v0.3"
RAPIDGATOR_HOSTS = {"rapidgator.net", "www.rapidgator.net"}

QUOTA_HINTS = (
    "daily download limit", "daily limit", "maximum number of downloads",
    "you have reached", "download limit", "daily downloads",
    "nombre de téléchargements quotidiens", "téléchargements quotidiens autorisés",
    "limite de téléchargement", "réessayez plus tard", "reessayez plus tard",
)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("790x620")
        self.root.minsize(690, 540)

        self.url_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Prêt. Collez un lien Rapidgator.")
        self.quota_var = tk.StringVar(value="État du quota : non vérifié")
        self.destination_var = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        self.queue = []
        self.busy = False

        outer = ttk.Frame(root, padding=18)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="RG Unlocker Desktop", font=("Segoe UI", 19, "bold")).pack(anchor="w")
        ttk.Label(outer, text="v0.3 • Gestionnaire local • Rapidgator uniquement", foreground="#555").pack(anchor="w", pady=(2, 14))

        ttk.Label(outer, text="Lien Rapidgator").pack(anchor="w")
        url_row = ttk.Frame(outer)
        url_row.pack(fill="x", pady=(5, 10))
        self.url_entry = ttk.Entry(url_row, textvariable=self.url_var)
        self.url_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(url_row, text="Coller", command=self.paste_clipboard).pack(side="left", padx=(8, 0))

        buttons = ttk.Frame(outer)
        buttons.pack(fill="x", pady=(0, 12))
        ttk.Button(buttons, text="Ouvrir dans Chrome", command=self.open_rapidgator).pack(side="left")
        ttk.Button(buttons, text="Ajouter à la file", command=self.add_to_queue).pack(side="left", padx=8)
        ttk.Button(buttons, text="Retirer de la file", command=self.remove_from_queue).pack(side="left")

        ttk.Label(outer, text="File d'attente (les liens seront ouverts manuellement ; aucun quota n'est contourné)").pack(anchor="w")
        self.queue_box = tk.Listbox(outer, height=5, activestyle="dotbox")
        self.queue_box.pack(fill="x", pady=(5, 12))

        ttk.Label(outer, text="Dossier de destination pour les URL directes autorisées").pack(anchor="w")
        dest_row = ttk.Frame(outer)
        dest_row.pack(fill="x", pady=(5, 10))
        ttk.Entry(dest_row, textvariable=self.destination_var).pack(side="left", fill="x", expand=True)
        ttk.Button(dest_row, text="Parcourir…", command=self.choose_folder).pack(side="left", padx=(8, 0))

        ttk.Button(outer, text="Télécharger une URL directe autorisée…", command=self.download_direct_prompt).pack(anchor="w", pady=(0, 10))

        quota_frame = ttk.LabelFrame(outer, text="Diagnostic de quota", padding=10)
        quota_frame.pack(fill="x", pady=(2, 10))
        ttk.Label(quota_frame, textvariable=self.quota_var, wraplength=700).pack(anchor="w")
        ttk.Label(
            quota_frame,
            text="Si Rapidgator indique que le quota quotidien est atteint, attendez la réinitialisation annoncée par le site. "
                 "Le délai de 120 minutes entre fichiers ne garantit pas la remise à zéro d'un quota quotidien.",
            foreground="#555", wraplength=700, justify="left"
        ).pack(anchor="w", pady=(6, 0))

        ttk.Label(outer, textvariable=self.status_var, wraplength=720).pack(anchor="w", pady=(4, 0))
        ttk.Label(
            outer,
            text="Cette application ne réinitialise pas le quota et ne contourne pas l'authentification, le CAPTCHA, les délais ou les restrictions de compte.",
            foreground="#555", wraplength=720, justify="left"
        ).pack(anchor="w", pady=(10, 0))

    def validate_page_url(self):
        raw = self.url_var.get().strip()
        if not raw:
            raise ValueError("Collez d’abord un lien.")
        if not re.match(r"^https?://", raw, re.I):
            raw = "https://" + raw
        parsed = urlparse(raw)
        host = (parsed.hostname or "").lower()
        if host not in RAPIDGATOR_HOSTS or parsed.scheme != "https" or not parsed.path or parsed.path == "/":
            raise ValueError("Collez un lien de fichier HTTPS valide sur rapidgator.net.")
        return raw

    def paste_clipboard(self):
        try:
            self.url_var.set(self.root.clipboard_get().strip())
        except tk.TclError:
            self.status_var.set("Le presse-papiers est vide.")

    def choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.destination_var.get() or os.path.expanduser("~"))
        if folder:
            self.destination_var.set(folder)

    def open_rapidgator(self):
        try:
            url = self.validate_page_url()
        except ValueError as exc:
            messagebox.showerror("Lien invalide", str(exc))
            return
        webbrowser.open(url)
        self.quota_var.set("État du quota : à vérifier sur la page Rapidgator dans le navigateur.")
        self.status_var.set("Lien ouvert dans le navigateur. Si un quota est atteint, suivez le délai indiqué par Rapidgator.")

    def add_to_queue(self):
        try:
            url = self.validate_page_url()
        except ValueError as exc:
            messagebox.showerror("Lien invalide", str(exc))
            return
        if url in self.queue:
            self.status_var.set("Ce lien est déjà dans la file.")
            return
        self.queue.append(url)
        self.queue_box.insert(tk.END, url)
        self.status_var.set(f"Lien ajouté à la file ({len(self.queue)}). Les liens ne seront pas téléchargés automatiquement.")

    def remove_from_queue(self):
        selection = self.queue_box.curselection()
        if not selection:
            self.status_var.set("Sélectionnez un lien dans la file.")
            return
        index = selection[0]
        self.queue_box.delete(index)
        self.queue.pop(index)
        self.status_var.set(f"Lien retiré. {len(self.queue)} lien(s) restant(s).")

    def download_direct_prompt(self):
        messagebox.showinfo(
            "URL directe autorisée requise",
            "Un lien /file/... est généralement une page web, pas une URL directe du fichier.\\n\\n"
            "Cette fonction ne peut pas réinitialiser le quota gratuit. Utilisez uniquement une URL directe "
            "fournie par Rapidgator via un accès autorisé ; les liens temporaires peuvent expirer."
        )
        win = tk.Toplevel(self.root)
        win.title("Télécharger une URL directe")
        win.geometry("650x190")
        win.transient(self.root)
        frame = ttk.Frame(win, padding=14)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="URL directe fournie par Rapidgator").pack(anchor="w")
        var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=var)
        entry.pack(fill="x", pady=8)
        entry.focus_set()
        ttk.Label(frame, text="L'URL doit être en HTTPS et sur rapidgator.net.", foreground="#555").pack(anchor="w")
        ttk.Button(frame, text="Choisir le fichier et télécharger", command=lambda: self.start_direct_download(var.get().strip(), win)).pack(anchor="e", pady=10)

    def start_direct_download(self, url, win):
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        if parsed.scheme != "https" or host not in RAPIDGATOR_HOSTS or not parsed.path:
            messagebox.showerror("URL refusée", "L’URL directe doit être en HTTPS sur rapidgator.net.")
            return
        if self.busy:
            messagebox.showwarning("Téléchargement en cours", "Attendez la fin du téléchargement actuel.")
            return
        folder = self.destination_var.get().strip()
        if not os.path.isdir(folder):
            messagebox.showerror("Dossier invalide", "Choisissez un dossier de destination existant.")
            return
        name = unquote(os.path.basename(parsed.path)) or "rapidgator_download.bin"
        name = re.sub(r'[<>:"/\\\\|?*\\x00-\\x1f]', "_", name)
        if name in ("", ".", ".."):
            name = "rapidgator_download.bin"
        path = filedialog.asksaveasfilename(title="Enregistrer le fichier", initialdir=folder, initialfile=name)
        if not path:
            return
        win.destroy()
        self.busy = True
        self.status_var.set("Connexion à l'URL directe…")
        threading.Thread(target=self.download_worker, args=(url, path), daemon=True).start()

    def download_worker(self, url, path):
        temp_path = path + ".part"
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "RGUnlockerDesktop/0.3"})
            with urllib.request.urlopen(request, timeout=30) as response:
                content_type = response.headers.get("Content-Type", "").lower()
                total_header = response.headers.get("Content-Length")
                total = int(total_header) if total_header and total_header.isdigit() else 0
                first = response.read(8192)
                first_text = first.decode("utf-8", errors="ignore").lower()
                if "text/html" in content_type or any(hint in first_text for hint in QUOTA_HINTS):
                    if any(hint in first_text for hint in QUOTA_HINTS):
                        msg = "Rapidgator semble avoir renvoyé une page de quota/limite au lieu du fichier. Ouvrez le lien dans Chrome et respectez le délai affiché."
                        self.root.after(0, self.quota_var.set, "État du quota : réponse de limite détectée ; consultez Rapidgator dans Chrome.")
                    else:
                        msg = "Le serveur a renvoyé une page HTML, pas le fichier. Le lien peut être une page de téléchargement, une session expirée ou une page de vérification."
                    raise ValueError(msg)
                downloaded = len(first)
                with open(temp_path, "wb") as out:
                    out.write(first)
                    while True:
                        chunk = response.read(262144)
                        if not chunk:
                            break
                        out.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            self.root.after(0, self.status_var.set, f"Téléchargement : {downloaded / 1048576:.1f} / {total / 1048576:.1f} Mo")
                        else:
                            self.root.after(0, self.status_var.set, f"Téléchargement : {downloaded / 1048576:.1f} Mo")
            os.replace(temp_path, path)
            self.root.after(0, self.status_var.set, f"Terminé : {path}")
            self.root.after(0, messagebox.showinfo, "Téléchargement terminé", f"Fichier enregistré :\\n{path}")
        except Exception as exc:
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except OSError:
                pass
            text = str(exc)
            if "10061" in text or "Connection refused" in text:
                text = "Connexion refusée. Vérifiez l'accès au site et assurez-vous que l'URL est une URL directe encore valide."
            self.root.after(0, self.status_var.set, f"Échec : {text}")
            self.root.after(0, messagebox.showerror, "Téléchargement impossible", text)
        finally:
            self.busy = False

def main():
    root = tk.Tk()
    try:
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
    except Exception:
        pass
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
