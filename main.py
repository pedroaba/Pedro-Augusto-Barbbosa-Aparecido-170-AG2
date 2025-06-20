import flet as ft
import threading
import pandas as pd
import asyncio

from model import Model
from database import Connection

class AppState:
    model = None
    label_encoders = None
    feature_names = None
    trained = False
    error = None

# Codetables (igual antes)
CODETABLES = {
    "laufkont": [
        ("1", "Sem conta corrente"),
        ("2", "Saldo < 0 DM"),
        ("3", "0 <= Saldo < 200 DM"),
        ("4", "Saldo >= 200 DM / salário há 1 ano+"),
    ],
    "moral": [
        ("0", "Atraso no pagamento no passado"),
        ("1", "Conta crítica / outros créditos"),
        ("2", "Sem créditos ou todos pagos em dia"),
        ("3", "Créditos pagos em dia até agora"),
        ("4", "Todos os créditos deste banco pagos"),
    ],
    "verw": [
        ("0", "Outros"),
        ("1", "Carro (novo)"),
        ("2", "Carro (usado)"),
        ("3", "Móveis/equipamentos"),
        ("4", "Rádio/TV"),
        ("5", "Eletrodomésticos"),
        ("6", "Reformas"),
        ("7", "Educação"),
        ("8", "Férias"),
        ("9", "Reciclagem profissional"),
        ("10", "Negócios"),
    ],
    "sparkont": [
        ("1", "Desconhecido / sem conta poupança"),
        ("2", "< 100 DM"),
        ("3", "100 <= saldo < 500 DM"),
        ("4", "500 <= saldo < 1000 DM"),
        ("5", ">= 1000 DM"),
    ],
    "beszeit": [
        ("1", "Desempregado"),
        ("2", "< 1 ano"),
        ("3", "1-4 anos"),
        ("4", "4-7 anos"),
        ("5", ">= 7 anos"),
    ],
    "rate": [
        ("1", ">= 35%"),
        ("2", "25-35%"),
        ("3", "20-25%"),
        ("4", "< 20%"),
    ],
    "famges": [
        ("1", "Masculino: divorciado/separado"),
        ("2", "Feminino: não solteira ou Masculino: solteiro"),
        ("3", "Masculino: casado/viúvo"),
        ("4", "Feminino: solteira"),
    ],
    "buerge": [
        ("1", "Nenhum"),
        ("2", "Co-requerente"),
        ("3", "Fiador"),
    ],
    "wohnzeit": [
        ("1", "< 1 ano"),
        ("2", "1-4 anos"),
        ("3", "4-7 anos"),
        ("4", ">= 7 anos"),
    ],
    "verm": [
        ("1", "Desconhecido / sem bens"),
        ("2", "Carro ou outros"),
        ("3", "Poupança / seguro de vida"),
        ("4", "Imóvel"),
    ],
    "weitkred": [
        ("1", "Banco"),
        ("2", "Lojas"),
        ("3", "Nenhum"),
    ],
    "wohn": [
        ("1", "Sem custo (for free)"),
        ("2", "Aluguel"),
        ("3", "Própria"),
    ],
    "bishkred": [
        ("1", "1"),
        ("2", "2-3"),
        ("3", "4-5"),
        ("4", ">= 6"),
    ],
    "beruf": [
        ("1", "Desempregado / não qualificado - não residente"),
        ("2", "Não qualificado - residente"),
        ("3", "Empregado qualificado / oficial"),
        ("4", "Gerente / autônomo / altamente qualificado"),
    ],
    "pers": [
        ("1", "3 ou mais"),
        ("2", "0 a 2"),
    ],
    "telef": [
        ("1", "Não"),
        ("2", "Sim (em nome do cliente)"),
    ],
    "gastarb": [
        ("1", "Sim"),
        ("2", "Não"),
    ],
}

FIELD_MAP = {
    "laufkont":   ("Identificação", "Tipo de Conta Corrente", "Selecione..."),
    "laufzeit":   ("Identificação", "Prazo do Empréstimo (meses)", "Ex: 24"),
    "moral":      ("Informações Financeiras", "Histórico de Crédito", "Selecione..."),
    "verw":       ("Informações do Empréstimo", "Finalidade", "Selecione..."),
    "hoehe":      ("Informações do Empréstimo", "Valor do Crédito", "Valor solicitado..."),
    "sparkont":   ("Informações Financeiras", "Conta Poupança", "Selecione..."),
    "beszeit":    ("Identificação", "Tempo de Emprego (anos)", "Selecione..."),
    "rate":       ("Informações do Empréstimo", "Parcela Mensal (%)", "Selecione..."),
    "famges":     ("Dados Pessoais", "Estado Civil / Sexo", "Selecione..."),
    "buerge":     ("Dados Pessoais", "Fiador", "Selecione..."),
    "wohnzeit":   ("Identificação", "Tempo de Residência (anos)", "Selecione..."),
    "verm":       ("Informações Financeiras", "Bens", "Selecione..."),
    "alter":      ("Dados Pessoais", "Idade", "Idade do cliente..."),
    "weitkred":   ("Informações Financeiras", "Outros Créditos", "Selecione..."),
    "wohn":       ("Identificação", "Tipo de Residência", "Selecione..."),
    "bishkred":   ("Informações Financeiras", "Outros Empréstimos", "Selecione..."),
    "beruf":      ("Dados Pessoais", "Profissão", "Selecione..."),
    "pers":       ("Dados Pessoais", "Pessoas Dependentes", "Selecione..."),
    "telef":      ("Identificação", "Telefone", "Selecione..."),
    "gastarb":    ("Dados Pessoais", "Trabalhador Estrangeiro", "Selecione..."),
}

ICONS = {
    "Identificação": ft.Icons.PERSON,
    "Dados Pessoais": ft.Icons.BADGE,
    "Informações Financeiras": ft.Icons.ATTACH_MONEY,
    "Informações do Empréstimo": ft.Icons.PAYMENTS,
    "Outros Dados": ft.Icons.INSIGHTS,
}

def section_card(title, icon, children):
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(icon, size=24, color=ft.Colors.BLUE_600),
                ft.Text(title, size=22, weight="bold"),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Divider(height=6, thickness=1, color="#EDF2FA"),
            *children
        ], spacing=16, expand=True),
        padding=24,
        margin=ft.Margin(0, 18, 0, 0),
        bgcolor="#FAFBFD",
        border_radius=16,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=20,
            color="#DFE8F6",
            offset=ft.Offset(1, 3)
        ),
        expand=True
    )

def main(page: ft.Page):
    page.title = "Classificação de Novo Cliente"
    page.window_width = 750
    page.window_height = 940
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = "#F6F8FB"

    main_column = ft.Column(
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
        spacing=0
    )

    main_column.controls.append(
        ft.Container(
            content=ft.Column([
                ft.Text(
                    "Classificação de Novo Cliente",
                    size=38,
                    weight="bold",
                    color=ft.Colors.BLACK,
                    text_align="center"
                ),
                ft.Text(
                    "Sistema inteligente de análise e classificação de risco",
                    size=18,
                    color=ft.Colors.BLUE_GREY_500,
                    text_align="center"
                )
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            padding=ft.Padding(0, 32, 0, 16),
            alignment=ft.alignment.center
        )
    )

    def show_form():
        sections = {}
        state = {}

        for field in AppState.feature_names:
            if field == "id" or field == "kredit":
                continue

            section, label, placeholder = FIELD_MAP.get(
                field,
                ("Outros Dados", field.replace("_", " ").title(), ""),
            )

            # Dropdowns baseados na codetable, se houver
            if field in CODETABLES:
                options = [ft.dropdown.Option(key, text=desc) for key, desc in CODETABLES[field]]
                widget = ft.Dropdown(
                    label=label,
                    hint_text=placeholder,
                    options=options,
                    filled=True,
                    border_radius=8,
                    bgcolor="#F5F8FE",
                    dense=True,
                    expand=True
                )
            elif field in AppState.label_encoders:
                le = AppState.label_encoders[field]
                values = list(le.classes_)
                widget = ft.Dropdown(
                    label=label,
                    hint_text=placeholder,
                    options=[ft.dropdown.Option(v) for v in values],
                    filled=True,
                    border_radius=8,
                    bgcolor="#F5F8FE",
                    dense=True,
                    expand=True
                )
            else:
                widget = ft.TextField(
                    label=label,
                    hint_text=placeholder,
                    filled=True,
                    border_radius=8,
                    bgcolor="#F5F8FE",
                    keyboard_type=ft.KeyboardType.NUMBER if any(k in field for k in ["idade", "valor", "taxa", "ano", "tempo", "prazo", "amount"]) else ft.KeyboardType.TEXT,
                    dense=True,
                    expand=True
                )
            state[field] = widget
            sections.setdefault(section, []).append(widget)

        cards = []
        for sec, widgets in sections.items():
            cards.append(
                ft.Container(
                    content=section_card(sec, ICONS.get(sec, ft.Icons.INSIGHTS), widgets),
                    expand=True,
                    padding=ft.Padding(0, 0, 0, 0),
                )
            )

        result_text = ft.Text(
            "",
            size=22,
            weight="bold",
            color=ft.Colors.GREEN_700,
            text_align="center",
            max_lines=2,
        )

        btn = ft.ElevatedButton(
            "Classificar",
            icon=ft.Icons.SEARCH,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                bgcolor=ft.Colors.BLUE_700,
                color=ft.Colors.WHITE,
                padding=20,
            ),
            scale=1.1,
            on_click=lambda _: classify(state, result_text),
            expand=True
        )

        # ListView para rolar os cards de seções
        listview = ft.ListView(
            controls=cards + [
                ft.Container(
                    btn,
                    padding=ft.Padding(0, 30, 0, 30),
                    alignment=ft.alignment.center,
                    expand=True
                ),
                ft.Container(
                    result_text,
                    alignment=ft.alignment.center,
                    margin=ft.Margin(0, 8, 0, 0),
                    expand=True
                ),
            ],
            expand=True,
            spacing=16,
            padding=ft.Padding(12, 0, 12, 24),
            auto_scroll=False,
        )

        main_column.controls = main_column.controls[:1]
        main_column.controls.append(listview)

        page.update()

    def classify(state, result_text):
        input_data = {
            "id": 28
        }
        try:
            for field in AppState.feature_names:
                if field == "id" or field == "kredit":
                    continue
                widget = state[field]
                value = widget.value
                if field in CODETABLES or field in AppState.label_encoders:
                    if not value:
                        result_text.value = f"Selecione um valor para {FIELD_MAP[field][1]}"
                        result_text.color = ft.Colors.RED_700
                        page.update()
                        return
                else:
                    if value is None or value.strip() == "":
                        result_text.value = f"Preencha o valor de {FIELD_MAP[field][1]}"
                        result_text.color = ft.Colors.RED_700
                        page.update()
                        return
                    value = float(value.replace(",", "."))
                input_data[field] = value

            df_new = pd.DataFrame([input_data])
            result = AppState.model.predict(df_new)[0]
            if result == 1:
                msg = "Aprovado ✅"
                result_text.color = ft.Colors.GREEN_700
            else:
                msg = "Reprovado ❌"
                result_text.color = ft.Colors.RED_700
            result_text.value = f"Classificação: {msg}"
        except Exception as ex:
            print(ex)
            result_text.value = f"Erro: {str(ex)}"
            result_text.color = ft.Colors.RED_700
        page.update()

    # Loading, training, polling igual antes
    loading = ft.Column(
        [
            ft.ProgressRing(width=70, height=70, color=ft.Colors.BLUE_500),
            ft.Text(
                "Treinando modelo de crédito...",
                size=22,
                weight="bold",
                color=ft.Colors.BLUE_800,
                text_align="center",
            ),
            ft.Text(
                "Aguarde, isso pode levar alguns segundos.",
                color=ft.Colors.BLUE_700,
                text_align="center",
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=30,
    )

    loading_container = ft.Container(
        content=loading,
        alignment=ft.alignment.center,
        margin=30,
        border_radius=16,
        bgcolor=ft.Colors.WHITE,
        width=400,
        height=300,
        shadow=ft.BoxShadow(
            spread_radius=2, blur_radius=30, color=ft.Colors.BLUE_200, offset=ft.Offset(1, 3)
        ),
    )

    main_column.controls.append(loading_container)
    page.add(
        ft.Container(
            content=main_column,
            expand=True,
            alignment=ft.alignment.top_center,
        )
    )

    def train_model():
        try:
            Connection.connect()
            trained = Model.train()
            Connection.disconnect()
            AppState.model = trained["model"]
            AppState.label_encoders = trained["label_encoders"]
            AppState.feature_names = trained["feature_names"]
            AppState.trained = True
        except Exception as e:
            AppState.trained = False
            AppState.error = str(e)

    async def poll_training():
        while not AppState.trained and AppState.error is None:
            await asyncio.sleep(0.2)
        if AppState.trained:
            main_column.controls = main_column.controls[:1]
            show_form()
            page.update()
        elif AppState.error is not None:
            main_column.controls.clear()
            main_column.controls.append(
                ft.Text(
                    f"Erro ao treinar modelo: {AppState.error}",
                    size=16,
                    color=ft.Colors.RED_800,
                )
            )
            page.update()

    threading.Thread(target=train_model, daemon=True).start()
    page.run_task(poll_training)

ft.app(target=main)
