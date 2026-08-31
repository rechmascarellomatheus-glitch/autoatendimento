import sqlite3
from pathlib import Path
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, NumericProperty

DB_NAME = None

KV = r'''
#:import dp kivy.metrics.dp

<MainMenuScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(24)
        spacing: dp(16)
        Label:
            text: "AUTOATENDIMENTO"
            font_size: dp(30)
            bold: True
            size_hint_y: None
            height: dp(70)
        Label:
            text: "Escolha uma opção"
            font_size: dp(20)
            size_hint_y: None
            height: dp(40)
        Button:
            text: "FAZER COMPRA"
            font_size: dp(22)
            size_hint_y: None
            height: dp(75)
            on_release: app.new_sale()
        Button:
            text: "ADMINISTRADOR"
            font_size: dp(22)
            size_hint_y: None
            height: dp(75)
            on_release: app.root.current = "login"
        Widget:

<LoginScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(24)
        spacing: dp(14)
        Label:
            text: "LOGIN DO ADMINISTRADOR"
            font_size: dp(27)
            bold: True
            size_hint_y: None
            height: dp(60)
        TextInput:
            id: username
            hint_text: "Usuário"
            multiline: False
            size_hint_y: None
            height: dp(55)
        TextInput:
            id: password
            hint_text: "Senha"
            password: True
            multiline: False
            size_hint_y: None
            height: dp(55)
        Label:
            id: message
            text: ""
            size_hint_y: None
            height: dp(35)
        Button:
            text: "ENTRAR"
            size_hint_y: None
            height: dp(65)
            on_release: root.do_login()
        Button:
            text: "VOLTAR"
            size_hint_y: None
            height: dp(55)
            on_release: root.go_back()
        Widget:

<AdminScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(12)
        spacing: dp(8)
        Label:
            text: "PAINEL DO ADMINISTRADOR"
            font_size: dp(25)
            bold: True
            size_hint_y: None
            height: dp(52)
        Label:
            text: root.summary
            size_hint_y: None
            height: dp(45)
            text_size: self.width, None
        GridLayout:
            cols: 2
            spacing: dp(7)
            size_hint_y: None
            height: dp(118)
            Button:
                text: "CADASTRAR PRODUTO"
                on_release: app.root.current = "product"
            Button:
                text: "LISTAR PRODUTOS"
                on_release: root.show_products()
            Button:
                text: "HISTÓRICO DE VENDAS"
                on_release: root.show_history()
            Button:
                text: "TOTAL DO CAIXA"
                on_release: root.show_cash()
        TextInput:
            id: product_id
            hint_text: "ID para remover produto"
            input_filter: "int"
            multiline: False
            size_hint_y: None
            height: dp(48)
        Button:
            text: "REMOVER PRODUTO"
            size_hint_y: None
            height: dp(50)
            on_release: root.remove_product()
        ScrollView:
            do_scroll_x: False
            Label:
                id: info
                text: root.info_text
                text_size: self.width, None
                halign: "left"
                valign: "top"
                size_hint_y: None
                height: self.texture_size[1] + dp(20)
        Button:
            text: "SAIR DO ADMINISTRADOR"
            size_hint_y: None
            height: dp(55)
            on_release: root.logout()

<ProductScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(18)
        spacing: dp(10)
        Label:
            text: "CADASTRAR PRODUTO"
            font_size: dp(26)
            bold: True
            size_hint_y: None
            height: dp(55)
        TextInput:
            id: name
            hint_text: "Nome do produto"
            multiline: False
            size_hint_y: None
            height: dp(52)
        TextInput:
            id: price
            hint_text: "Preço (ex.: 12.90)"
            multiline: False
            input_filter: "float"
            size_hint_y: None
            height: dp(52)
        TextInput:
            id: barcode
            hint_text: "Código de barras"
            multiline: False
            size_hint_y: None
            height: dp(52)
        Label:
            id: message
            text: ""
            size_hint_y: None
            height: dp(42)
        Button:
            text: "CADASTRAR"
            size_hint_y: None
            height: dp(62)
            on_release: root.save_product()
        Button:
            text: "VOLTAR AO PAINEL"
            size_hint_y: None
            height: dp(56)
            on_release: root.go_back()
        Widget:

<PurchaseScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(10)
        spacing: dp(7)
        Label:
            text: "FAZER COMPRA"
            font_size: dp(25)
            bold: True
            size_hint_y: None
            height: dp(48)
        TextInput:
            id: search
            hint_text: "Nome do produto ou código de barras"
            multiline: False
            size_hint_y: None
            height: dp(52)
            on_text_validate: root.search_product()
        Button:
            text: "PROCURAR"
            size_hint_y: None
            height: dp(48)
            on_release: root.search_product()
        Label:
            id: result
            text: "Digite um produto para procurar."
            text_size: self.width, None
            halign: "left"
            valign: "middle"
            size_hint_y: None
            height: dp(78)
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(7)
            TextInput:
                id: quantity
                hint_text: "Qtd"
                text: "1"
                input_filter: "int"
                multiline: False
            Button:
                text: "ADICIONAR"
                on_release: root.add_to_cart()
        Label:
            text: "CARRINHO"
            font_size: dp(19)
            bold: True
            size_hint_y: None
            height: dp(35)
        ScrollView:
            do_scroll_x: False
            Label:
                id: cart
                text: root.cart_text
                text_size: self.width, None
                halign: "left"
                valign: "top"
                size_hint_y: None
                height: self.texture_size[1] + dp(15)
        GridLayout:
            cols: 2
            spacing: dp(6)
            size_hint_y: None
            height: dp(108)
            Button:
                text: "REMOVER ÚLTIMO"
                on_release: root.remove_last()
            Button:
                text: "LIMPAR CARRINHO"
                on_release: root.clear_cart()
            Button:
                text: "FINALIZAR COMPRA"
                on_release: root.checkout()
            Button:
                text: "VOLTAR"
                on_release: root.go_home()

<PaymentScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(22)
        spacing: dp(12)
        Label:
            text: "PAGAMENTO"
            font_size: dp(27)
            bold: True
            size_hint_y: None
            height: dp(55)
        Label:
            text: root.total_text
            font_size: dp(24)
            size_hint_y: None
            height: dp(45)
        Button:
            text: "DINHEIRO"
            size_hint_y: None
            height: dp(65)
            on_release: root.pay_cash()
        Button:
            text: "PIX"
            size_hint_y: None
            height: dp(65)
            on_release: root.pay_simple("PIX")
        Button:
            text: "CARTÃO"
            size_hint_y: None
            height: dp(65)
            on_release: root.pay_simple("CARTAO")
        Label:
            id: message
            text: ""
            size_hint_y: None
            height: dp(45)
        Button:
            text: "VOLTAR"
            size_hint_y: None
            height: dp(55)
            on_release: app.root.current = "purchase"
        Widget:

<CashScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(22)
        spacing: dp(12)
        Label:
            text: "PAGAMENTO EM DINHEIRO"
            font_size: dp(25)
            bold: True
            size_hint_y: None
            height: dp(55)
        Label:
            text: root.total_text
            font_size: dp(23)
            size_hint_y: None
            height: dp(45)
        TextInput:
            id: received
            hint_text: "Valor recebido"
            input_filter: "float"
            multiline: False
            size_hint_y: None
            height: dp(55)
        Label:
            id: message
            text: ""
            text_size: self.width, None
            halign: "center"
            size_hint_y: None
            height: dp(55)
        Button:
            text: "CONFIRMAR PAGAMENTO"
            size_hint_y: None
            height: dp(62)
            on_release: root.confirm()
        Button:
            text: "VOLTAR"
            size_hint_y: None
            height: dp(55)
            on_release: app.root.current = "payment"
        Widget:

<ReceiptScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(12)
        spacing: dp(8)
        Label:
            text: "COMPRA FINALIZADA"
            font_size: dp(24)
            bold: True
            size_hint_y: None
            height: dp(48)
        ScrollView:
            do_scroll_x: False
            Label:
                id: receipt
                text: root.receipt_text
                text_size: self.width, None
                halign: "left"
                valign: "top"
                size_hint_y: None
                height: self.texture_size[1] + dp(20)
        Button:
            text: "NOVA COMPRA"
            size_hint_y: None
            height: dp(62)
            on_release: root.new_purchase()
'''


def money_to_cents(value):
    try:
        d = Decimal(str(value).replace(",", ".")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if d < 0:
            raise ValueError
        return int(d * 100)
    except (InvalidOperation, ValueError):
        raise ValueError("Valor inválido")


def cents_to_money(cents):
    return f"R$ {cents / 100:.2f}".replace(".", ",")


class Database:
    def __init__(self, filename):
        self.filename = filename
        self.init_db()

    def connect(self):
        con = sqlite3.connect(self.filename)
        con.row_factory = sqlite3.Row
        return con

    def init_db(self):
        with self.connect() as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL COLLATE NOCASE,
                    preco_centavos INTEGER NOT NULL CHECK(preco_centavos >= 0),
                    codigo TEXT NOT NULL UNIQUE
                )
            """)
            con.execute("""
                CREATE TABLE IF NOT EXISTS vendas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL,
                    total_centavos INTEGER NOT NULL,
                    pagamento TEXT NOT NULL
                )
            """)
            con.execute("""
                CREATE TABLE IF NOT EXISTS itens_venda (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venda_id INTEGER NOT NULL,
                    produto_id INTEGER NOT NULL,
                    nome TEXT NOT NULL,
                    codigo TEXT NOT NULL,
                    preco_centavos INTEGER NOT NULL,
                    quantidade INTEGER NOT NULL,
                    subtotal_centavos INTEGER NOT NULL,
                    FOREIGN KEY(venda_id) REFERENCES vendas(id),
                    FOREIGN KEY(produto_id) REFERENCES produtos(id)
                )
            """)

    def add_product(self, name, price_cents, barcode):
        with self.connect() as con:
            con.execute(
                "INSERT INTO produtos (nome, preco_centavos, codigo) VALUES (?, ?, ?)",
                (name.strip(), price_cents, barcode.strip()),
            )

    def search_products(self, query):
        q = query.strip()
        with self.connect() as con:
            return con.execute(
                """
                SELECT id, nome, preco_centavos, codigo
                FROM produtos
                WHERE nome LIKE ? OR codigo = ?
                ORDER BY nome
                LIMIT 20
                """,
                (f"%{q}%", q),
            ).fetchall()

    def get_product(self, product_id):
        with self.connect() as con:
            return con.execute(
                "SELECT id, nome, preco_centavos, codigo FROM produtos WHERE id = ?",
                (product_id,),
            ).fetchone()

    def list_products(self):
        with self.connect() as con:
            return con.execute(
                "SELECT id, nome, preco_centavos, codigo FROM produtos ORDER BY nome"
            ).fetchall()

    def delete_product(self, product_id):
        with self.connect() as con:
            con.execute("DELETE FROM produtos WHERE id = ?", (product_id,))

    def create_sale(self, cart, total_cents, payment):
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        with self.connect() as con:
            cur = con.execute(
                "INSERT INTO vendas (data, total_centavos, pagamento) VALUES (?, ?, ?)",
                (now, total_cents, payment),
            )
            sale_id = cur.lastrowid
            for item in cart:
                con.execute(
                    """
                    INSERT INTO itens_venda (
                        venda_id, produto_id, nome, codigo, preco_centavos,
                        quantidade, subtotal_centavos
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        sale_id,
                        item["id"],
                        item["nome"],
                        item["codigo"],
                        item["preco_centavos"],
                        item["quantidade"],
                        item["subtotal_centavos"],
                    ),
                )
        return sale_id, now

    def history(self):
        with self.connect() as con:
            sales = con.execute(
                "SELECT id, data, total_centavos, pagamento FROM vendas ORDER BY id DESC"
            ).fetchall()
            result = []
            for sale in sales:
                items = con.execute(
                    """
                    SELECT nome, codigo, preco_centavos, quantidade, subtotal_centavos
                    FROM itens_venda WHERE venda_id = ? ORDER BY id
                    """,
                    (sale["id"],),
                ).fetchall()
                result.append((sale, items))
            return result

    def cash_total(self):
        with self.connect() as con:
            return con.execute(
                "SELECT COALESCE(SUM(total_centavos), 0) AS total FROM vendas"
            ).fetchone()["total"]

    def sales_count(self):
        with self.connect() as con:
            return con.execute("SELECT COUNT(*) AS n FROM vendas").fetchone()["n"]

    def product_count(self):
        with self.connect() as con:
            return con.execute("SELECT COUNT(*) AS n FROM produtos").fetchone()["n"]


class MainMenuScreen(Screen):
    pass


class LoginScreen(Screen):
    def do_login(self):
        if self.ids.username.text.strip() == "admin" and self.ids.password.text == "1234":
            self.ids.username.text = ""
            self.ids.password.text = ""
            self.ids.message.text = ""
            self.manager.current = "admin"
        else:
            self.ids.message.text = "Usuário ou senha incorretos."

    def go_back(self):
        self.ids.username.text = ""
        self.ids.password.text = ""
        self.ids.message.text = ""
        self.manager.current = "main"


class AdminScreen(Screen):
    summary = StringProperty("")
    info_text = StringProperty("Escolha uma opção acima.")

    def on_pre_enter(self):
        self.refresh()

    def refresh(self):
        db = App.get_running_app().db
        self.summary = (
            f"Produtos: {db.product_count()} | Vendas: {db.sales_count()} | "
            f"Caixa: {cents_to_money(db.cash_total())}"
        )

    def show_products(self):
        rows = App.get_running_app().db.list_products()
        if not rows:
            self.info_text = "Nenhum produto cadastrado."
            return
        lines = ["PRODUTOS CADASTRADOS\n"]
        for p in rows:
            lines.append(
                f"ID {p['id']} | {p['nome']} | {cents_to_money(p['preco_centavos'])} | "
                f"Código: {p['codigo']}"
            )
        self.info_text = "\n".join(lines)

    def remove_product(self):
        raw = self.ids.product_id.text.strip()
        if not raw:
            self.info_text = "Digite o ID do produto."
            return
        try:
            product_id = int(raw)
        except ValueError:
            self.info_text = "ID inválido."
            return
        if not App.get_running_app().db.get_product(product_id):
            self.info_text = "Produto não encontrado."
            return
        App.get_running_app().db.delete_product(product_id)
        self.ids.product_id.text = ""
        self.info_text = "Produto removido."
        self.refresh()

    def show_history(self):
        history = App.get_running_app().db.history()
        if not history:
            self.info_text = "Nenhuma venda realizada."
            return
        lines = ["HISTÓRICO DE VENDAS\n"]
        for sale, items in history:
            lines.append(
                f"Venda #{sale['id']} | {sale['data']} | "
                f"{cents_to_money(sale['total_centavos'])} | {sale['pagamento']}"
            )
            for item in items:
                lines.append(
                    f"  - {item['nome']} | {item['quantidade']} x "
                    f"{cents_to_money(item['preco_centavos'])} = "
                    f"{cents_to_money(item['subtotal_centavos'])}"
                )
            lines.append("")
        self.info_text = "\n".join(lines)

    def show_cash(self):
        db = App.get_running_app().db
        self.info_text = (
            f"TOTAL VENDIDO: {cents_to_money(db.cash_total())}\n"
            f"VENDAS: {db.sales_count()}\n"
            f"PRODUTOS: {db.product_count()}"
        )

    def logout(self):
        self.info_text = "Escolha uma opção acima."
        self.manager.current = "main"


class ProductScreen(Screen):
    def save_product(self):
        name = self.ids.name.text.strip()
        price = self.ids.price.text.strip()
        barcode = self.ids.barcode.text.strip()
        if not name or not price or not barcode:
            self.ids.message.text = "Preencha nome, preço e código."
            return
        try:
            cents = money_to_cents(price)
        except ValueError:
            self.ids.message.text = "Preço inválido."
            return
        try:
            App.get_running_app().db.add_product(name, cents, barcode)
        except sqlite3.IntegrityError:
            self.ids.message.text = "Esse código de barras já existe."
            return
        self.ids.name.text = ""
        self.ids.price.text = ""
        self.ids.barcode.text = ""
        self.ids.message.text = "Produto cadastrado com sucesso!"

    def go_back(self):
        self.manager.get_screen("admin").refresh()
        self.manager.current = "admin"


class PurchaseScreen(Screen):
    cart_text = StringProperty("Carrinho vazio.")
    selected_product_id = NumericProperty(0)

    @property
    def cart(self):
        return App.get_running_app().cart

    def search_product(self):
        query = self.ids.search.text.strip()
        if not query:
            self.ids.result.text = "Digite um nome ou código de barras."
            self.selected_product_id = 0
            return
        rows = App.get_running_app().db.search_products(query)
        if not rows:
            self.ids.result.text = "Produto não encontrado."
            self.selected_product_id = 0
        elif len(rows) == 1:
            p = rows[0]
            self.selected_product_id = p["id"]
            self.ids.result.text = (
                f"{p['nome']}\nCódigo: {p['codigo']}\n"
                f"Preço: {cents_to_money(p['preco_centavos'])}\nSelecionado."
            )
        else:
            self.selected_product_id = 0
            self.ids.result.text = "\n".join(
                ["Vários produtos encontrados:"]
                + [
                    f"{p['nome']} | {cents_to_money(p['preco_centavos'])} | {p['codigo']}"
                    for p in rows
                ]
            )

    def add_to_cart(self):
        if not self.selected_product_id:
            self.ids.result.text = "Procure um produto primeiro."
            return
        try:
            quantity = int(self.ids.quantity.text or "1")
        except ValueError:
            self.ids.result.text = "Quantidade inválida."
            return
        if quantity <= 0:
            self.ids.result.text = "Quantidade deve ser maior que zero."
            return
        p = App.get_running_app().db.get_product(self.selected_product_id)
        if not p:
            self.ids.result.text = "Produto não encontrado."
            return
        for item in self.cart:
            if item["id"] == p["id"]:
                item["quantidade"] += quantity
                item["subtotal_centavos"] = item["preco_centavos"] * item["quantidade"]
                self.update_cart_text()
                self.ids.result.text = "Quantidade atualizada."
                return
        self.cart.append({
            "id": p["id"],
            "nome": p["nome"],
            "codigo": p["codigo"],
            "preco_centavos": p["preco_centavos"],
            "quantidade": quantity,
            "subtotal_centavos": p["preco_centavos"] * quantity,
        })
        self.update_cart_text()
        self.ids.result.text = "Produto adicionado."

    def update_cart_text(self):
        if not self.cart:
            self.cart_text = "Carrinho vazio."
            return
        lines = []
        total = 0
        count = 0
        for i, item in enumerate(self.cart, 1):
            lines.append(
                f"{i}. {item['nome']}\n"
                f"   {item['quantidade']} x {cents_to_money(item['preco_centavos'])}\n"
                f"   Subtotal: {cents_to_money(item['subtotal_centavos'])}\n"
            )
            total += item["subtotal_centavos"]
            count += item["quantidade"]
        lines += ["-" * 28, f"Itens: {count}", f"TOTAL: {cents_to_money(total)}"]
        self.cart_text = "\n".join(lines)

    def remove_last(self):
        if self.cart:
            self.cart.pop()
            self.update_cart_text()

    def clear_cart(self):
        self.cart.clear()
        self.update_cart_text()

    def checkout(self):
        if not self.cart:
            self.ids.result.text = "Adicione pelo menos um produto."
            return
        payment = self.manager.get_screen("payment")
        payment.set_total(sum(item["subtotal_centavos"] for item in self.cart))
        self.manager.current = "payment"

    def go_home(self):
        self.cart.clear()
        self.update_cart_text()
        self.ids.search.text = ""
        self.ids.quantity.text = "1"
        self.ids.result.text = "Digite um produto para procurar."
        self.selected_product_id = 0
        self.manager.current = "main"


class PaymentScreen(Screen):
    total_text = StringProperty("TOTAL: R$ 0,00")

    def set_total(self, total_cents):
        self.total_cents = total_cents
        self.total_text = f"TOTAL: {cents_to_money(total_cents)}"
        self.ids.message.text = ""

    def pay_cash(self):
        cash = self.manager.get_screen("cash")
        cash.set_total(self.total_cents)
        self.manager.current = "cash"

    def pay_simple(self, method):
        self.finish_sale(method, 0)

    def finish_sale(self, method, received_cents):
        app = App.get_running_app()
        change = max(0, received_cents - self.total_cents)
        sale_id, date = app.db.create_sale(app.cart, self.total_cents, method)
        receipt = app.build_receipt(
            sale_id, date, app.cart, self.total_cents, method, received_cents, change
        )
        app.root.get_screen("receipt").receipt_text = receipt
        self.manager.current = "receipt"


class CashScreen(Screen):
    total_text = StringProperty("TOTAL: R$ 0,00")

    def set_total(self, total_cents):
        self.total_cents = total_cents
        self.total_text = f"TOTAL: {cents_to_money(total_cents)}"
        self.ids.received.text = ""
        self.ids.message.text = ""

    def confirm(self):
        try:
            received = money_to_cents(self.ids.received.text.strip())
        except ValueError:
            self.ids.message.text = "Valor inválido."
            return
        if received < self.total_cents:
            self.ids.message.text = f"Falta {cents_to_money(self.total_cents - received)}."
            return
        self.manager.get_screen("payment").finish_sale("DINHEIRO", received)


class ReceiptScreen(Screen):
    receipt_text = StringProperty("")

    def new_purchase(self):
        app = App.get_running_app()
        app.cart.clear()
        purchase = self.manager.get_screen("purchase")
        purchase.ids.search.text = ""
        purchase.ids.quantity.text = "1"
        purchase.ids.result.text = "Digite um produto para procurar."
        purchase.selected_product_id = 0
        purchase.update_cart_text()
        self.manager.current = "main"


class Manager(ScreenManager):
    pass


class CaixaApp(App):
    title = "Autoatendimento"

    def build(self):
        # No Android, o banco fica no diretório privado do aplicativo.
        # Isso permite que o APK grave os dados sem depender de uma pasta externa.
        db_path = str(Path(self.user_data_dir) / "caixa.db")
        self.db = Database(db_path)
        self.cart = []
        Builder.load_string(KV)
        sm = Manager()
        sm.add_widget(MainMenuScreen(name="main"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(AdminScreen(name="admin"))
        sm.add_widget(ProductScreen(name="product"))
        sm.add_widget(PurchaseScreen(name="purchase"))
        sm.add_widget(PaymentScreen(name="payment"))
        sm.add_widget(CashScreen(name="cash"))
        sm.add_widget(ReceiptScreen(name="receipt"))
        return sm

    def new_sale(self):
        self.cart.clear()
        purchase = self.root.get_screen("purchase")
        purchase.ids.search.text = ""
        purchase.ids.quantity.text = "1"
        purchase.ids.result.text = "Digite um produto para procurar."
        purchase.selected_product_id = 0
        purchase.update_cart_text()
        self.root.current = "purchase"

    def build_receipt(self, sale_id, date, cart, total_cents, payment, received_cents, change):
        lines = [
            "=" * 32,
            "      AUTOATENDIMENTO",
            "            CUPOM",
            "=" * 32,
            f"Venda: #{sale_id}",
            f"Data: {date}",
            "",
        ]
        for item in cart:
            lines.extend([
                item["nome"],
                f"Código: {item['codigo']}",
                f"{item['quantidade']} x {cents_to_money(item['preco_centavos'])} = "
                f"{cents_to_money(item['subtotal_centavos'])}",
                "",
            ])
        lines.extend([
            "-" * 32,
            f"TOTAL: {cents_to_money(total_cents)}",
            f"Pagamento: {payment}",
        ])
        if payment == "DINHEIRO":
            lines.extend([
                f"Recebido: {cents_to_money(received_cents)}",
                f"Troco: {cents_to_money(change)}",
            ])
        lines.extend(["=" * 32, "         OBRIGADO!", "=" * 32])
        return "\n".join(lines)


if __name__ == "__main__":
    CaixaApp().run()
