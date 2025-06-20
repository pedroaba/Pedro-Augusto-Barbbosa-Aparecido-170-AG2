import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

from model import Model

trained = Model.train()
model = trained['model']
label_encoders = trained['label_encoders']
feature_names = trained['feature_names']


class ClassifierApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Classificador de Crédito - Statlog German Credit")

        self.entries = {}
        self.fields = feature_names
        self.label_encoders = label_encoders

        frm = ttk.Frame(self, padding=20)
        frm.pack(fill=tk.BOTH, expand=True)

        for idx, field in enumerate(self.fields):
            label = ttk.Label(frm, text=field)
            label.grid(row=idx, column=0, sticky=tk.W, pady=3)

            # Se for campo categórico, cria um combobox com valores possíveis
            if field in self.label_encoders:
                le = self.label_encoders[field]
                values = list(le.classes_)
                cb = ttk.Combobox(frm, values=values, state='readonly')
                cb.grid(row=idx, column=1, pady=3)
                self.entries[field] = cb
            else:
                entry = ttk.Entry(frm)
                entry.grid(row=idx, column=1, pady=3)
                self.entries[field] = entry

        classify_btn = ttk.Button(frm, text="Classificar", command=self.classify)
        classify_btn.grid(row=len(self.fields), columnspan=2, pady=12)

    def classify(self):
        input_data = {}
        # Pega todos os dados do formulário
        for field in self.fields:
            widget = self.entries[field]
            value = widget.get()

            if field in self.label_encoders:
                le = self.label_encoders[field]
                if value not in le.classes_:
                    messagebox.showerror("Erro", f"Valor inválido para {field}")
                    return
                # Transforma em valor numérico para o modelo
                value = le.transform([value])[0]
            else:
                try:
                    value = float(value)
                except Exception:
                    messagebox.showerror("Erro", f"Valor inválido para {field}")
                    return
            input_data[field] = value

        # Cria DataFrame de uma linha para classificar
        df_new = pd.DataFrame([input_data])
        result = model.predict(df_new)[0]

        # Mostra o resultado
        messagebox.showinfo("Resultado", f"Classificação: {result}")
