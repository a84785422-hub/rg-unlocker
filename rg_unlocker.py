import os
import re
import threading
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from urllib.parse import urlparse, unquote

APP_TITLE = "RG Unlocker Desktop — prototype"
RAPIDGATOR_HOSTS = {"rapidgator.net", "www.rapidgator.net"}

class App:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("720x470")
        self.root.minsize(620, 420)

        self.url_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Prêt. Collez un lien Rapidgator.")
        self.progress_var = tk.DoubleVar(value=0)
        self.destination_var = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        self.busy = False

        outer = ttk.Frame(root, padding=18)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="RG Unlocker Desktop", font=("Segoe UI", 19, "bold")).pack(anchor="w")
        ttk.Label(
            outer,
            text="Prototype gratuit • Rapidgator uniquement • Windows",
            foreground="#555"
        ).pack(anchor="w", pady=(2, 16))

        ttk.Label(outer, text="Lien Rapidgator").pack(anchor="w")
        url_row = ttk.Frame(outer)
        url_row.pack(fill="x", pady=(5, 12))
        self.url_entry = ttk.Entry(url_row, textvariable=self.url_var)
        self.url_entry.pack(side="left", fill="x", expand=True)
        self.url_entry.focus_set()
        ttk.Button(url_row, text="Coller", command=self.paste_clipboard).pack(side="left", padx=(8, 0))

        ttk.Label(outer, text="Dossier de destination").pack(anchor="w")
        dest_row = ttk.Frame(outer)
        dest_row.pack(fill="x", pady=(5, 12))
        ttk.Entry(dest_row, textvariable=self.destination_var).pack(side="left", fill="x", expand=True)
        ttk.Button(dest_row, text="Parcourir…", command=self.choose_folder).pack(side="left", padx=(8, 0))

        actions = ttk.Frame(outer)
        actions.pack(fill="x", pady=(2, 12))
        ttk.Button(actions, text="Ouvrir sur Rapidgator", command=self.open_rapidgator).pack(side="left")
        ttk.Button(actions, text="Télécharger un lien direct…", command=self.download_direct_prompt).pack(side="left", padx=8)

        self.progress = ttk.Progressbar(outer, variable=self.progress_var, maximum=100)
        self.progress.pack(fill="x", pady=(8, 5))
        ttk.Label(outer, textvariable=self.status_var, wraplength=660).pack(anchor="w", pady=(2, 10))

        note = (
            "Limite de cette V0 : un lien /file/… est généralement une page web, pas l’adresse directe du fichier. "
            "Le bouton de téléchargement ne contourne ni le compte Premium, ni l’attente, ni le CAPTCHA. "
            "Pour les téléchargements Rapidgator gratuits, ouvrez le lien dans le navigateur et suivez les étapes du site."
        )
        ttk.Label(outer, text=note, wraplength=660, foreground="#555", justify="left").pack(anchor="w", pady=(6, 0))

    def paste_clipboard(self):
        try:
            self.url_var.set(self.root.clipboard_get().strip())
        except tk.TclError:
            self.status_var.set("Le presse-papiers est vide.")

    def choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.destination_var.get() or os.path.expanduser("~"))
        if folder:
            self.destination_var.set(folder)

    def parsed_url(self):
        raw = self.url_var.get().strip()
        if not raw:
            raise ValueError("Collez d’abord un lien.")
        if not re.match(r"^https?://", raw, re.I):
            raw = "https://" + raw
        parsed = urlparse(raw)
        host = (parsed.hostname or "").lower()
        if host not in RAPIDGATOR_HOSTS:
            raise ValueError("Cette version accepte uniquement rapidgator.net.")
        if parsed.scheme != "https":
            raise ValueError("Utilisez un lien HTTPS.")
        if not parsed.path or parsed.path == "/":
            raise ValueError("Le lien ne semble pas pointer vers un fichier Rapidgator.")
        return raw, parsed

    def open_rapidgator(self):
        import webbrowser
        try:
            url, _ = self.parsed_url()
        except ValueError as exc:
            messagebox.showerror("Lien invalide", str(exc))
            return
        webbrowser.open(url)
        self.status_var.set("Lien ouvert dans le navigateur. Connectez-vous si nécessaire et suivez les étapes Rapidgator.")

    def download_direct_prompt(self):
        try:
            url, parsed = self.parsed_url()
        except ValueError as exc:
            messagebox.showerror("Lien invalide", str(exc))
            return
        messagebox.showinfo(
            "Adresse directe requise",
            "Le lien collé est une page Rapidgator, pas forcément le fichier lui-même.\\n\\n"
            "Cette V0 ne contourne pas le compte, l’attente ou le CAPTCHA. "
            "Si Rapidgator vous fournit une URL directe de téléchargement autorisée, "
            "vous pourrez la coller dans la fenêtre suivante."
        )
        direct = tk.Toplevel(self.root)
        direct.title("Télécharger une URL directe")
        direct.geometry("620x180")
        direct.transient(self.root)
        frame = ttk.Frame(direct, padding=14)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="URL directe fournie par Rapidgator").pack(anchor="w")
        direct_var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=direct_var)
        entry.pack(fill="x", pady=8)
        entry.focus_set()
        ttk.Label(frame, text="Cette URL peut être temporaire et expirer rapidement.", foreground="#555").pack(anchor="w")
        ttk.Button(frame, text="Choisir le fichier et télécharger",
                   command=lambda: self.start_direct_download(direct_var.get().strip(), direct)).pack(anchor="e", pady=10)

    def start_direct_download(self, url, window):
        parsed = urlparse(url)
        if parsed.scheme not in ("https", "http") or not (parsed.hostname or "").lower().endswith("rapidgator.net"):
            messagebox.showerror("URL refusée", "Pour cette version, l’URL doit être sur rapidgator.net.")
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
        path = filedialog.asksaveasfilename(
            title="Enregistrer le fichier",
            initialdir=folder,
            initialfile=name,
            defaultextension=""
        )
        if not path:
            return
        window.destroy()
        self.busy = True
        self.progress_var.set(0)
        self.status_var.set("Connexion au lien direct…")
        threading.Thread(target=self.download_worker, args=(url, path), daemon=True).start()

    def download_worker(self, url, path):
        temp_path = path + ".part"
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "RGUnlockerDesktop/0.1"})
            with urllib.request.urlopen(request, timeout=30) as response:
                content_type = response.headers.get("Content-Type", "").lower()
                disposition = response.headers.get("Content-Disposition", "")
                total_header = response.headers.get("Content-Length")
                total = int(total_header) if total_header and total_header.isdigit() else 0

                # Avoid silently saving an HTML login/error page as the requested file.
                first = response.read(8192)
                if "text/html" in content_type or first.lstrip().lower().startswith((b"<!doctype html", b"<html")):
                    raise ValueError("Le serveur a renvoyé une page HTML (connexion, CAPTCHA, erreur ou lien expiré), pas le fichier.")
                downloaded = len(first)
                with open(temp_path, "wb") as output:
                    output.write(first)
                    while True:
                        chunk = response.read(1024 * 256)
                        if not chunk:
                            break
                        output.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            pct = min(100, downloaded * 100 / total)
                            self.root.after(0, self.progress_var.set, pct)
                            self.root.after(0, self.status_var.set,
                                            f"Téléchargement : {downloaded / 1048576:.1f} / {total / 1048576:.1f} Mo")
                        else:
                            self.root.after(0, self.status_var.set,
                                            f"Téléchargement : {downloaded / 1048576:.1f} Mo")
            os.replace(temp_path, path)
            self.root.after(0, self.progress_var.set, 100)
            self.root.after(0, self.status_var.set, f"Terminé : {path}")
            self.root.after(0, messagebox.showinfo, "Téléchargement terminé", f"Fichier enregistré :\\n{path}")
        except urllib.error.URLError as exc:
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except OSError:
                pass
            reason = getattr(exc, "reason", exc)
            if isinstance(reason, ConnectionRefusedError) or "10061" in str(reason):
                message = (
                    "Connexion refusée par le serveur. Le lien collé est probablement une page Rapidgator, "
                    "pas une URL directe de fichier, ou l’URL directe a expiré. "
                    "Ouvre le lien dans le navigateur et suis les étapes Rapidgator. "
                    "Cette application ne contourne pas l’attente, le CAPTCHA ou les restrictions de compte."
                )
            else:
                message = f"Erreur réseau : {reason}"
            self.root.after(0, self.status_var.set, f"Échec : {message}")
            self.root.after(0, messagebox.showerror, "Téléchargement impossible", message)
        except Exception as exc:
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except OSError:
                pass
            self.root.after(0, self.status_var.set, f"Échec : {exc}")
            self.root.after(0, messagebox.showerror, "Téléchargement impossible", str(exc))
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
