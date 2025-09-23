from flask import Flask, render_template, request, redirect, session, url_for
from flask import send_from_directory
from random import randint
from werkzeug.utils import secure_filename
from flask import flash, url_for, redirect
from datetime import datetime, date
import pytz
import shutil    
import os
import json
import time

TZ = pytz.timezone("America/Sao_Paulo")

CAMINHO_USUARIOS = "/mnt/data/usuarios.json"
CAMINHO_CURSOS = "/mnt/data/cursos.json"
CAMINHO_MATRICULAS = "/mnt/data/matriculas.json"
CAMINHO_PROGRESSO = "/mnt/data/progresso.json"
CAMINHO_CERTIFICADOS = "/mnt/data/certificados.json"
CAMINHO_TURMAS = "/mnt/data/turmas.json"
CAMINHO_VENCIMENTOS = "/mnt/data/vencimentos.json"

CURSOS_FIXOS = [
        "Doutrinamento Básico de Solo",
        "Conhecimentos Gerais",
        "Emergências Gerais",
        "SGSO",
        "Sobrevivência na Selva",
        "Instrutor de Voo",
        "Examinador",
        "BELL 206-B06",
        "AS350 SERIES-B,BA,B2,AS50",
        "AS 365 SERIES (N,N1,N2)/AS65",
        "AS 355 SERIES (F,F1,F2,NP)/AS55",
        "AS330J",
        "AS350B-BA",
        "AS350B2-B3",
        "Arriel1 Series",
        "RR250-C20 Series",
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = "/mnt/data/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
def gerar_ip():
    return ".".join(str(randint(0, 225)) for _ in range(4))

def inicializar_dados():
    arquivos = ["usuarios.json", "cursos.json", "matriculas.json", "progresso.json"]
    for nome in arquivos:
        origem = os.path.join("data", nome)  # pasta do repositório
        destino = os.path.join("/mnt/data", nome)
        if not os.path.exists(destino):
            shutil.copyfile(origem, destino)

def salvar_dados(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

def salvar_turmas_ctrl():
    salvar_dados(CAMINHO_TURMAS, turmas_ctrl)

def proxima_turma(curso_nome: str) -> str:
    last = int(turmas_ctrl.get(curso_nome, 0))
    nxt = last + 1
    turmas_ctrl[curso_nome] = nxt
    salvar_turmas_ctrl()
    return f"{nxt:03d}"

def sugerir_turma(curso_nome: str) -> str:
    """
    Apenas sugere (não persiste) o próximo número, para mostrar no formulário.
    """
    last = int(turmas_ctrl.get(curso_nome, 0))
    return f"{last+1:03d}"
    
def carregar_dados(caminho, padrao):
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    return padrao
    
inicializar_dados()
progresso_por_aluno = {}

usuarios    = carregar_dados(CAMINHO_USUARIOS, {})
cursos      = carregar_dados(CAMINHO_CURSOS, [])
matriculas  = carregar_dados(CAMINHO_MATRICULAS, [])
progresso   = carregar_dados(CAMINHO_PROGRESSO, {})
certificados = carregar_dados(CAMINHO_CERTIFICADOS, {})
turmas_ctrl  = carregar_dados(CAMINHO_TURMAS, {})
vencimentos = carregar_dados(CAMINHO_VENCIMENTOS, [])  

def obter_data_certificado_fixa(aluno: str, curso: str):
    """
    Retorna um dict com a data/hora fixa da 1ª emissão do certificado para (aluno, curso).
    Se ainda não existir, cria agora, salva em /mnt/data/certificados.json e retorna.
    """
    chave = f"{aluno}||{curso}"

    # Se já existe registro, reutiliza
    reg = certificados.get(chave)
    if reg and "emitido_em" in reg:
        return reg["emitido_em"]  # {'iso':..., 'data':..., 'hora':...}

    # Não existe ainda -> cria agora e persiste
    agora = datetime.now(TZ)
    emitido_em = {
        "iso":  agora.isoformat(),
        "data": agora.strftime("%d/%m/%Y"),
        "hora": agora.strftime("%H:%M"),
    }
    certificados[chave] = {"emitido_em": emitido_em}
    salvar_dados(CAMINHO_CERTIFICADOS, certificados)
    return emitido_em

def salvar_vencimentos():
    salvar_dados(CAMINHO_VENCIMENTOS, vencimentos)


def salvar_usuarios():
    with open(CAMINHO_USUARIOS, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, indent=2, ensure_ascii=False)

# ==== INÍCIO DO PATCH DE CATEGORIAS ====

def _title_from_email(email: str) -> str:
    base = (email.split("@")[0] if "@" in email else email)
    base = base.replace(".", " ").replace("_", " ").strip()
    return " ".join(p.capitalize() for p in base.split())

PILOTOS_SET = {
    "cmte.siqueira@ambipar.com",
    "cmte.taskilas@ambipar.com",
    "andre.gustavo@ambipar.com",
    "cmte.sales@ambipar.com",
    "andre.lyra@ambipar.com",
    "antonio.jorge@ambipar.com",
    "bruna.tasca@ambipar.com",
    "carlos.negreiros@ambipar.com",
    "carlos.maria@ambipar.com",
    "carlos.moraes@ambipar.com",
    "cmte.franck@ambipar.com",
    "cmte.rubens@ambipar.com",
    "cmte.celio@ambipar.com",
    "charles.pannain@ambipar.com",
    "cmte.cleyton@ambipar.com",
    "daniel.telles@ambipar.com",
    "danielle.pereira@ambipar.com",
    "djalma.neto@ambipar.com",
    "eduardo.antonio@ambipar.com",
    "eduardo.worm@ambipar.com",
    "fabio.araujo@ambipar.com",
    "fernando.telles@ambipar.com",
    "flavio.santos@ambipar.com",
    "hazafe.alencar@ambipar.com",
    "cmte.isaac@ambipar.com",
    "jairodop@hotmail.com",
    "cmte.trajano@ambipar.com",
    "leonardo.rapini@ambipar.com",
    "lohana.tose@ambipar.com",
    "cmte.mattara@ambipar.com",
    "cmte.pessoa@ambipar.com",
    "cmte.marron@ambipar.com",
    "luiz.lima@ambipar.com",
    "manollo.jordao@ambipar.com",
    "cmte.metre@ambipar.com",
    "marcelo.hashizume@ambipar.com",
    "mateus.sousa@ambipar.com",
    "matheus.fraga@ambipar.com",
    "cmte.mauricio@ambipar.com",
    "paulo.claudino@ambipar.com",
    "p.jalmeida@yahoo.com.br",
    "cmte.paulinho@ambipar.com",
    "cmte.chacon@ambipar.com",
    "ricardo.ramos@ambipar.com",
    "rodrigo.vasconcelos@ambipar.com",
    "cmte.romanato@ambipar.com",
    "romulo.equey@ambipar.com",
    "cmte.ronaldo@ambipar.com",
    "thiago.cury@ambipar.com",
    "victor.soares@ambipar.com",
    "cmte.welner@ambipar.com",
}

MECANICOS_SET = {
    "alan.araujo@ambipar.com",
    "aleksandro.inacio@ambipar.com",
    "allan.silva@ambipar.com",
    "andre.jales@ambipar.com",
    "ari.pinho@ambipar.com",
    "bruno.marins@ambipar.com",
    "carlos.ferezin@ambipar.com",
    "carlos.nunes@ambipar.com",
    "cesar.dupin@ambipar.com",
    "clayton.luis@ambipar.com",
    "daniel.levandeira@ambipar.com",
    "diego.campagnaro@ambipar.com",
    "eliomar.bruno@ambipar.com",
    "barbosa.fernando@ambipar.com",
    "frederico.malta@ambipar.com",
    "helio.souza@ambipar.com",
    "joao.augusto@ambipar.com",
    "joao.goncalves@ambipar.com",
    "jorge.figueiredo@ambipar.com",
    "jorge.dias@ambipar.com",
    "jurandyr.neto@ambipar.com",
    "laerte.lima@ambipar.com",
    "leandro.ribeiro@ambipar.com",
    "leandro.volk@ambipar.com",
    "luizvaldo.santos@ambipar.com",
    "marcelo.prado@ambipar.com",
    "marcelo.soares@ambipar.com",
    "nivaldo.lima@ambipar.com",
    "ricardo.jesus@ambipar.com",
    "robson.veiga@ambipar.com",
    "ronaldo.nicolli@ambipar.com",
    "bogomilrj@hotmail.com",
    "samuel.santarem@ambipar.com",
    "thalys.martins@ambipar.com",
    "thiago.rocha@ambipar.com",
    "valdecir.macedo@ambipar.com",
    "araujo.tiago@ambipar.com",
    "samuel.borges@ambipar.com",
    "felipe.pires@ambipar.com",
    "jeferson.jose@ambipar.com",
    "guilherme.azevedo@ambipar.com",
    "juliana.furtado@ambipar.com",
    "pereira.mar.mil@hotmail.com",
}

# Garante que existam registros para todos listados (se não existir, cria como aluno)
for email in sorted(PILOTOS_SET | MECANICOS_SET):
    if email not in usuarios:
        usuarios[email] = {
            "senha": "Ambipar2025",
            "tipo": "aluno",
            "nome": _title_from_email(email),
        }

# Atribui a categoria correta sem mexer no resto
for email, d in usuarios.items():
    if d.get("tipo") == "aluno":
        if email in PILOTOS_SET:
            d["categoria"] = "piloto"
        elif email in MECANICOS_SET:
            d["categoria"] = "mecanico"

# Filtro de visibilidade para professores por NOME
_prof_filtro_por_nome = {
    "Tuany Vasques": "piloto",
    "Leandro Michelin": "piloto",
    "Carlos Lourenço": "piloto",
    "Larissa Furtado": "mecanico",
}
for email, d in usuarios.items():
    if d.get("tipo") == "professor":
        alvo = _prof_filtro_por_nome.get(d.get("nome", ""))
        if alvo in ("piloto", "mecanico"):
            d["ver_categoria"] = alvo

salvar_usuarios()
# ==== FIM DO PATCH DE CATEGORIAS ====

# ==== FORÇA FILTRO DE VISIBILIDADE POR E-MAIL DO PROFESSOR ====
_forcar_prof_por_email = {
    "tuany.oliveira@ambipar.com": "piloto",    # Tuany vê só pilotos
    "leandro.michelin@ambipar.com": "piloto",  # Leandro vê só pilotos
    "carlos.lopes@ambipar.com": "piloto",      # Carlos vê só pilotos
    "larissafr.ctm@gmail.com": "mecanico",     # Larissa vê só mecânicos
}

mudou = False
for email, cat in _forcar_prof_por_email.items():
    u = usuarios.get(email)
    if u and u.get("tipo") == "professor":
        if u.get("ver_categoria") != cat:
            u["ver_categoria"] = cat
            mudou = True

if mudou:
    salvar_usuarios()
# ===============================================================


# --- Helpers de categoria do professor/aluno ---
def prof_categoria_atual():
    """Retorna 'piloto' ou 'mecanico' para o professor logado. Para aluno ou sem filtro, retorna None."""
    user = usuarios.get(session.get("usuario", ""), {})
    return user.get("ver_categoria")

def _aluno_e_da_categoria(email, cat):
    """True se cat is None (sem filtro) ou se o aluno tem usuarios[email]['categoria'] == cat."""
    if not cat:
        return True
    return usuarios.get(email, {}).get("categoria") == cat


def _lista_instrutores_por_categoria(cat: str):
    """
    Retorna uma lista de NOMES para o dropdown 'Professor' conforme a categoria do usuário logado.
    Usa PILOTOS_SET / MECANICOS_SET e puxa o 'nome' do usuarios.json.
    """
    if cat == "piloto":
        base_emails = sorted(PILOTOS_SET)
    elif cat == "mecanico":
        base_emails = sorted(MECANICOS_SET)
    else:
        # Sem filtro → todos (alunos e professores cadastrados)
        base_emails = sorted(
            [e for e, d in usuarios.items() if d.get("tipo") in ("aluno", "professor")]
        )

    nomes = []
    for e in base_emails:
        nome = usuarios.get(e, {}).get("nome") or _title_from_email(e)
        nomes.append(nome)

    nomes.sort(key=str.casefold)
    return nomes


def add_years(d: date, years: int) -> date:
    """Soma 'years' anos à data d, ajustando 29/02 -> 28/02 quando necessário."""
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        # lida com 29/02
        return d.replace(month=2, day=28, year=d.year + years)

progresso_por_aluno = {}

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx', 'jpg', 'jpeg', 'png', 'mp4', 'mp3', 'zip', 'rar', 'txt', 'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "chave_secreta"
app.config["MAX_CONTENT_LENGTH"] = 140 * 1024 * 1024  # 16 MB
def gerar_ip_falso() -> str:
    """Gera um IP v4 aleatório tipo '87.142.233.19'."""
    return ".".join(str(randint(10, 254)) for _ in range(4))
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ======================================================================
#                             ROTAS GERAIS
# ======================================================================
@app.route("/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

ALLOWED_EXTS = {"png", "jpg", "jpeg", "webp"}

AVATAR_DIR = os.path.join(app.static_folder, "avatars")
os.makedirs(AVATAR_DIR, exist_ok=True)

@app.route("/upload_foto", methods=["POST"])
def upload_foto():
    # Precisa estar logado
    email = session.get("usuario")   # <- usa a MESMA chave que você usa no login
    if not email:
        return redirect(url_for("home"))

    file = request.files.get("foto")
    if not file or file.filename.strip() == "":
        flash("Nenhum arquivo escolhido.", "error")
        return redirect(url_for("home"))

    # valida extensão
    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTS:
        flash("Formato inválido. Use PNG, JPG, JPEG ou WEBP.", "error")
        return redirect(url_for("home"))

    # nome de arquivo estável por usuário
    safe_email = email.replace("@", "_at_").replace(".", "_")
    final_name = f"{safe_email}.{ext}"
    save_path = os.path.join(AVATAR_DIR, final_name)
    file.save(save_path)

    # atualiza cadastro do usuário para apontar para o arquivo estático
    # usamos SEMPRE a chave 'foto'
    rel_path = f"avatars/{final_name}"

    global usuarios
    usuarios.setdefault(email, {})
    usuarios[email]["foto"] = rel_path
    try:
        salvar_dados(CAMINHO_USUARIOS, usuarios)
    except Exception:
        pass

    flash("Foto de perfil atualizada!", "success")
    return redirect(url_for("home"))

@app.route("/")
def home():
    if "usuario" not in session:
        return redirect("/login")

    if session["tipo"] == "professor":
        return render_template("professor_home.html", usuario=session["usuario"])

    # ---------- Aluno ----------
    email = session["usuario"]

    # Avatar com cache-busting
    avatar_url = url_for("static", filename="avatar_padrao.png")
    foto_rel = usuarios.get(email, {}).get("foto")
    if foto_rel:
        abs_path = os.path.join(app.static_folder, foto_rel)
        if os.path.exists(abs_path):
            ver = str(int(os.path.getmtime(abs_path)))
            avatar_url = url_for("static", filename=foto_rel) + f"?v={ver}"

    # Cursos do aluno (pelas matrículas)
    cursos_aluno = [m["curso"] for m in matriculas if m["aluno"] == email]
    cursos_disp = [c for c in cursos if c.get("nome") in cursos_aluno]

    cursos_matriculados = []  # inclui “aguardando início” e “em andamento”
    cursos_concluidos   = []  # somente com certificado liberado

    for curso in cursos_disp:
        nome = curso.get("nome")

        # Matrícula deste curso
        mat = next((m for m in matriculas if m["aluno"] == email and m["curso"] == nome), None)
        presenca_ok = bool(mat and mat.get("presenca_assinada"))

        # Progresso e resultado
        prog = curso.get("progresso", {}).get(email, {"concluido": False})
        res  = curso.get("resultados", {}).get(email)

        aprovado = bool(res and res.get("total", 0) > 0 and res["acertos"] >= 0.7 * res["total"])
        certificado_disponivel = (aprovado and presenca_ok and bool(prog.get("concluido")))

        # Monta payload enxuto pra tela
        item = {
            "nome": nome,
            "data_fim": mat.get("data_fim") if mat else None,
        }

        if certificado_disponivel:
            cursos_concluidos.append(item)
        else:
            cursos_matriculados.append(item)

    return render_template(
        "home_aluno.html",
        usuario=usuarios.get(email, {}).get("nome", email),
        avatar_url=avatar_url,
        cursos_matriculados=cursos_matriculados,
        cursos_concluidos=cursos_concluidos,
        aluno_email=email,
    )


    return redirect("/login")



# ----------------------------- LOGIN ----------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["nome"].strip().lower()
        senha = request.form["senha"]
        user  = usuarios.get(email)

        if user and user["senha"] == senha:
            session["usuario"] = email
            session["tipo"]    = user["tipo"]
            session["nome"]    = user["nome"]  # <- Aqui agora está corretamente indentado
            return redirect("/")

        return "Usuário ou senha incorretos"

    return render_template("login.html")




@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/cadastro")
def cadastro_bloqueado():
    return redirect("/login")

@app.route("/alterar_senha", methods=["GET", "POST"])
def alterar_senha():
    # precisa estar logado
    if "usuario" not in session:
        return redirect("/login")

    email = session["usuario"]

    if request.method == "POST":
        nova_senha = request.form.get("senha")
        if nova_senha:
            usuarios[email]["senha"] = nova_senha
            salvar_usuarios()
            flash("Senha alterada com sucesso!", "success")
            return redirect("/")  # volta para home (professor ou aluno)

    # GET → abre a página
    return render_template("alterar_senha.html", usuario=usuarios[email])


@app.route("/controle_vencimentos")
def controle_vencimentos():
    if session.get("tipo") != "professor":
        return redirect("/login")
    return render_template("controle_vencimentos.html")


@app.route("/vencimentos/adicionar", methods=["GET", "POST"])
def vencimentos_adicionar():
    if session.get("tipo") != "professor":
        return redirect("/login")

    # monta a lista de opções de curso como o template espera: [{nome: "..."}]
    nomes_cadastrados = {c.get("nome", "") for c in cursos if isinstance(c, dict)}
    nomes_fixos = set(CURSOS_FIXOS)
    nomes_validos = {n for n in (nomes_cadastrados | nomes_fixos) if n}  # união

    cursos_para_select = [{"nome": n} for n in sorted(nomes_validos, key=str.casefold)]
    cat = prof_categoria_atual()
    alunos_para_select = [{"email": e, "nome": d["nome"]}
                      for e, d in usuarios.items()
                      if d.get("tipo") == "aluno" and _aluno_e_da_categoria(e, cat)]

    if request.method == "POST":
        aluno_email = (request.form.get("aluno") or "").strip().lower()
        curso_nome  = (request.form.get("curso") or "").strip()
        data_venc   = (request.form.get("data_vencimento") or "").strip()  # YYYY-MM-DD

        erro = None
        if not aluno_email or not curso_nome or not data_venc:
            erro = "Preencha todos os campos."
        elif aluno_email not in usuarios:
            erro = "Aluno inválido."
        elif curso_nome not in nomes_validos:
            # agora aceita tanto os fixos quanto os que estão no cursos.json
            erro = "Curso inválido."

        if erro:
            return render_template(
                "vencimentos_adicionar.html",
                alunos=alunos_para_select,
                cursos=cursos_para_select,  # mantém o nome 'cursos' p/ seu template
                erro=erro
            )

        # mantém APENAS 1 registro por (aluno, curso): se existir, substitui
        global vencimentos
        vencimentos = [
            v for v in vencimentos
            if not (v.get("aluno") == aluno_email and v.get("curso") == curso_nome)
        ]
        vencimentos.append({
            "aluno": aluno_email,
            "curso": curso_nome,
            "data_vencimento": data_venc,  # YYYY-MM-DD
        })
        salvar_vencimentos()
        return redirect("/vencimentos/verificar")

    # GET
    return render_template(
        "vencimentos_adicionar.html",
        alunos=alunos_para_select,
        cursos=cursos_para_select,   # mantém o contrato atual do template
        erro=None
    )

# --- AJUSTE na rota existente: pular arquivados ---
@app.route("/vencimentos/verificar")
def vencimentos_verificar():
    if session.get("tipo") != "professor":
        return redirect("/login")

    hoje = datetime.now(TZ).date()
    cat = prof_categoria_atual()
    linhas = []

    for v in vencimentos:
        if v.get("arquivado"):
            continue

        aluno_email = v.get("aluno")
        if not _aluno_e_da_categoria(aluno_email, cat):
            continue

        curso_nome = v.get("curso")
        data_str   = v.get("data_vencimento")  # YYYY-MM-DD
        aluno_nome = usuarios.get(aluno_email, {}).get("nome", aluno_email)

        try:
            data_venc = datetime.strptime(data_str, "%Y-%m-%d").date()
        except Exception:
            data_venc = None

        if data_venc:
            dias = (data_venc - hoje).days
            vencido = dias < 0
            em_alerta = dias <= 90
            status = "Vencido" if vencido else f"Vence em {dias} dias"
        else:
            status = "Data inválida"
            em_alerta = False

        linhas.append({
            "aluno_email": aluno_email,
            "aluno_nome": aluno_nome,
            "curso": curso_nome,
            "data_venc": data_str,
            "status": status,
            "mostrar_matricular": em_alerta and (data_venc is not None)
        })

    def _key(l):
        try:
            return datetime.strptime(l["data_venc"], "%Y-%m-%d")
        except Exception:
            return datetime(2100, 1, 1)
    linhas.sort(key=_key)

    return render_template("vencimentos_verificar.html", linhas=linhas)


@app.route("/vencimentos/arquivar", methods=["POST"])
def vencimentos_arquivar():
    if session.get("tipo") != "professor":
        return redirect("/login")

    aluno = (request.form.get("aluno") or "").strip().lower()
    curso = (request.form.get("curso") or "").strip()

    alterado = False
    for v in vencimentos:
        if v.get("aluno") == aluno and v.get("curso") == curso:
            v["arquivado"] = True
            alterado = True
            break

    if alterado:
        salvar_vencimentos()
    return redirect(url_for("vencimentos_verificar"))

@app.route("/vencimentos/arquivados")
def vencimentos_arquivados():
    if session.get("tipo") != "professor":
        return redirect("/login")

    cat = prof_categoria_atual()
    linhas = []

    for v in vencimentos:
        if not v.get("arquivado"):
            continue
        aluno_email = v.get("aluno")
        if not _aluno_e_da_categoria(aluno_email, cat):
            continue

        curso_nome = v.get("curso")
        data_str   = v.get("data_vencimento")
        aluno_nome = usuarios.get(aluno_email, {}).get("nome", aluno_email)

        linhas.append({
            "aluno_email": aluno_email,
            "aluno_nome": aluno_nome,
            "curso": curso_nome,
            "data_venc": data_str,
        })

    def _key(l):
        try:
            return datetime.strptime(l["data_venc"], "%Y-%m-%d")
        except Exception:
            return datetime(2100, 1, 1)
    linhas.sort(key=_key)

    return render_template("vencimentos_arquivados.html", linhas=linhas)


@app.route("/vencimentos/restaurar", methods=["POST"])
def vencimentos_restaurar():
    if session.get("tipo") != "professor":
        return redirect("/login")

    aluno = (request.form.get("aluno") or "").strip().lower()
    curso = (request.form.get("curso") or "").strip()

    alterado = False
    for v in vencimentos:
        if v.get("aluno") == aluno and v.get("curso") == curso and v.get("arquivado"):
            v["arquivado"] = False
            alterado = True
            break

    if alterado:
        salvar_vencimentos()
    return redirect(url_for("vencimentos_arquivados"))
    
# ======================================================================
#                       ROTAS (PROFESSOR)
# ======================================================================
@app.route("/cadastrar_curso", methods=["GET", "POST"])
def cadastrar_curso():
    if session.get("tipo") != "professor":
        return redirect("/")

    if request.method == "POST":
        # -------- MÓDULOS MULTI-ARQUIVO --------
        modulos = []
        index = 0
        while True:
            titulo = request.form.get(f'modulos[{index}][titulo]')
            arquivo = request.files.get(f'modulos[{index}][arquivo]')
            if not titulo or not arquivo:
                break
            if allowed_file(arquivo.filename):
                filename = secure_filename(arquivo.filename)
                caminho = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(os.path.dirname(caminho), exist_ok=True)
                arquivo.save(caminho)
                modulos.append({"titulo": titulo, "arquivo": filename})
            index += 1

        # -------- PROVA MULTIPLA ESCOLHA --------
        perguntas = []

        for key, val in request.form.items():
            if key.startswith("perguntas[") and "][" in key:
                try:
                    idx = int(key.split("[")[1].split("]")[0])
                    campo = key.split("][")[1].rstrip("]")
                except (IndexError, ValueError):
                    continue  # ignora campos malformados

                while len(perguntas) <= idx:
                    perguntas.append({
                        "enunciado": "",
                        "a": "",
                        "b": "",
                        "c": "",
                        "d": "",
                        "correta": ""
                    })

                perguntas[idx][campo] = val

        # -------- CRIA O CURSO --------
        usuario_sessao = session.get("usuario")
        instrutor_nome = usuarios[usuario_sessao]["nome"] if usuario_sessao and usuario_sessao in usuarios else "Desconhecido"

        curso = {
            "nome":            request.form["nome"],
            "carga_horaria":   request.form["carga_horaria"],
            "modulos":         modulos,
            "instrutor":       request.form.get("instrutor", instrutor_nome),
            "conteudo":        request.form.get("conteudo", ""),
            "prova":           perguntas,
        }

        cursos.append(curso)
        salvar_dados(CAMINHO_CURSOS, cursos)  # Salva o curso novo no disco
        return redirect("/")

    return render_template("cadastrar_curso.html")

@app.route("/editar_turma")
def editar_turma_list():
    if session.get("tipo") != "professor":
        return redirect("/login")

    # agrupa por (curso, turma)
    
    cat = prof_categoria_atual()
    grupos = {}
    for m in matriculas:
            if not _aluno_e_da_categoria(m.get("aluno",""), cat):
                continue
            key = (m.get("curso", ""), m.get("turma", ""))
            grupos.setdefault(key, []).append(m)

    # monta linhas para a tabela
    linhas = []
    for (curso_nome, turma_num), regs in sorted(grupos.items()):
        if not curso_nome or not turma_num:
            continue
        ref = regs[0]
        linhas.append({
            "curso": curso_nome,
            "turma": turma_num,
            "nrt":   ref.get("nrt", "—"),
            "tipo":  ref.get("tipo", "—"),
            "professor": ref.get("professor", "—"),
            "periodicidade": ref.get("periodicidade", "—"),
            "data_inicio": ref.get("data_inicio", "—"),
            "data_fim":    ref.get("data_fim", "—"),
            "qtd_alunos":  len(regs),
        })

    return render_template("editar_turma.html", linhas=linhas)


@app.route("/editar_turma/<path:curso>/<turma>", methods=["GET", "POST"])
def editar_turma_detalhe(curso, turma):
    if session.get("tipo") != "professor":
        return redirect("/login")
    global matriculas
    cat = prof_categoria_atual()
        
    # matrículas desta turma
    regs = [m for m in matriculas if m.get("curso") == curso and m.get("turma") == turma]
    if not regs:
        return "Turma não encontrada", 404

    ref = regs[0]  # usa como referência dos metadados da turma
    nrt   = ref.get("nrt", "")
    tipo  = ref.get("tipo", "")
    prof  = ref.get("professor", "")
    per   = ref.get("periodicidade", "")
    di    = ref.get("data_inicio", "")
    df    = ref.get("data_fim", "")

    # alunos já na turma
    alunos_da_turma = [m["aluno"] for m in regs]

    # alunos candidatos = todos os 'aluno' do sistema que NÃO estão na turma deste curso
        
    candidatos = [
            {"email": e, "nome": d["nome"]}
            for e, d in usuarios.items()
            if d.get("tipo") == "aluno"
               and e not in alunos_da_turma
               and _aluno_e_da_categoria(e, cat)
    ]
        
    # ordena por nome
    candidatos.sort(key=lambda x: x["nome"].casefold())

    if request.method == "POST":
        acao = request.form.get("acao")

        if acao == "add":
            aluno_email = (request.form.get("aluno_novo") or "").strip().lower()
            if not aluno_email or aluno_email not in usuarios:
                flash("Selecione um aluno válido.", "erro")
            else:
                # impede duplicata na mesma turma
                existe = any(m for m in matriculas
                             if m.get("aluno") == aluno_email and
                                m.get("curso") == curso and
                                m.get("turma") == turma)
                if existe:
                    flash("Este aluno já está nesta turma.", "erro")
                else:
                    matriculas.append({
                        "aluno":       aluno_email,
                        "curso":       curso,
                        "professor":   prof,
                        "tipo":        tipo,
                        "nrt":         nrt,
                        "turma":       turma,
                        "data_inicio": di,
                        "data_fim":    df,
                        "periodicidade": per,
                    })
                    salvar_dados(CAMINHO_MATRICULAS, matriculas)
                    flash("Aluno adicionado à turma.", "success")
            return redirect(url_for("editar_turma_detalhe", curso=curso, turma=turma))

        elif acao == "remove":
            aluno_email = (request.form.get("aluno_email") or "").strip().lower()
            # remove somente a matrícula deste curso/turma
            
            matriculas = [
                m for m in matriculas
                if not (m.get("aluno") == aluno_email and
                        m.get("curso") == curso and
                        m.get("turma") == turma)
            ]
            salvar_dados(CAMINHO_MATRICULAS, matriculas)
            flash("Aluno removido da turma.", "success")
            return redirect(url_for("editar_turma_detalhe", curso=curso, turma=turma))

    # reconsulta após possíveis alterações
    regs = [m for m in matriculas if m.get("curso") == curso and m.get("turma") == turma]
    alunos_da_turma = [{
        "email": m["aluno"],
        "nome": usuarios.get(m["aluno"], {}).get("nome", m["aluno"])
    } for m in regs]
    alunos_da_turma.sort(key=lambda x: x["nome"].casefold())

    return render_template(
        "editar_turma_detalhe.html",
        curso=curso, turma=turma,
        nrt=nrt, tipo=tipo, professor=prof,
        periodicidade=per, data_inicio=di, data_fim=df,
        alunos=alunos_da_turma, candidatos=candidatos
    )

    # ============== GET: monta contexto ===================
    # Alunos **da turma** (nome + email)
    alunos_da_turma = []
    for m in ms:
        email = m.get("aluno")
        nome  = usuarios.get(email, {}).get("nome", email)
        alunos_da_turma.append({"email": email, "nome": nome})

    # Alunos elegíveis para adicionar: são "aluno" e NÃO estão matriculados neste mesmo curso
    ja_no_curso = {m.get("aluno") for m in matriculas if m.get("curso") == curso}
    candidatos = []
    for email, d in usuarios.items():
        if d.get("tipo") == "aluno" and email not in ja_no_curso:
            candidatos.append({"email": email, "nome": d.get("nome", email)})
    candidatos.sort(key=lambda x: x["nome"].casefold())

    ctx = {
        "curso": curso,
        "turma": turma,
        "nrt": unico_ou_vazio("nrt"),
        "tipo": unico_ou_vazio("tipo"),
        "professor": unico_ou_vazio("professor"),
        "periodicidade": str(unico_ou_vazio("periodicidade")) if unico_ou_vazio("periodicidade") != "" else "",
        "data_inicio": unico_ou_vazio("data_inicio"),
        "data_fim": unico_ou_vazio("data_fim"),
        "professores_lista": [
            "Airton Benedito de Siqueira Junior", "Alexandre Kopfer Martins", "Andre Gustavo Chialastri Altounian",
            "Andre Luis Damazio de Sales", "André Palazzo Lyra", "Antonio Jorge de Souza Neto", "Bruna Maria Tasca",
            "Carlos Agusto da Silva Negreiros", "Carlos Eduardo Alho Maria", "Carlos Eduardo Vizentim de Moraes",
            "Carlos Franck da Costa Simanke", "Carlos Rubens Prudente Melo", "Celio Ricardo de Albuquerque Pimentel",
            "Charles Pires Pannain", "Cleyton de Oliveira Almeida", "Danielle dos Santos Pereira",
            "Daniel de Sousa Freitas da Silva Telles", "Djalma da Conceição Neto", "Eduardo Antonio Ferreira",
            "Eduardo Dupke Worm", "Fabio Amaral Goes de Araujo", "Fernando Carlos da Silva Telles",
            "Flavio Ramalho dos Santos", "Hazafe Pacheco de Alencar", "Isaac Barreto de Andrade",
            "Jerusa Cristiane Alves Trajano da Silva", "Leonardo Pompein Campos Rapini", "Lohana Detes Tose",
            "Lucas Medonça Mattara", "Luís Eduardo Santana Pessôa de Oliveira", "Luiz Fellipe Marron Rabello",
            "Luiz Fernando Lima", "Manollo Aleixo Jordão", "Marcelo Ricardo Soares Metre", "Marcelo Teruo Hashizume",
            "Mateus Cruz de Sousa", "Matheus Tondim Fraga", "Mauricio Andries dos Santos",
            "Paulo Cesar Machado Claudino", "Paulo Roberto de Andrade Costa", "Rafael Herculano Cavalcante",
            "Ricardo Chacon Veeck", "Ricardo de Moraes Ramos", "Rodrigo Pereira Silva Vasconcelos",
            "Rodrigo Romanato de Castro", "Ronaldo de Albuquerque Filho", "Romulo Leonardo Equey Gomes",
            "Thiago Falcão Cury", "Victor Lucas Pereira Soares", "Welner Silva Lima"
        ],
        "alunos_da_turma": sorted(alunos_da_turma, key=lambda x: x["nome"].casefold()),
        "candidatos": candidatos,
    }
    return render_template("editar_turma_form.html", **ctx)


    # POST -> atualiza TODAS as matrículas da turma
    nrt_new   = (request.form.get("nrt") or "").strip()
    tipo_new  = (request.form.get("tipo") or "").strip()
    prof_new  = (request.form.get("professor") or "").strip()
    per_new   = request.form.get("periodicidade")  # pode vir '', '1','2','3','5'
    di_new    = (request.form.get("data_inicio") or "").strip()
    df_new    = (request.form.get("data_fim") or "").strip()

    # Normaliza periodicidade
    if per_new not in ("", "1", "2", "3", "5"):
        per_new = ""

    # Aplica (somente campos preenchidos no form)
    for m in ms:
        if nrt_new:  m["nrt"] = nrt_new
        if tipo_new: m["tipo"] = tipo_new
        if prof_new: m["professor"] = prof_new
        if per_new != "": m["periodicidade"] = int(per_new)
        if di_new:   m["data_inicio"] = di_new
        if df_new:   m["data_fim"] = df_new

    salvar_dados(CAMINHO_MATRICULAS, matriculas)
    flash("Turma atualizada com sucesso!", "success")
    return redirect(url_for("editar_turma_lista"))
        
@app.route("/cadastrar_professor", methods=["GET", "POST"])
def cadastrar_professor():
    # Só professor pode acessar
    if session.get("tipo") != "professor":
        return redirect("/login")

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        nome  = request.form.get("nome", "").strip()
        senha = request.form.get("senha", "")

        # validações simples
        if not email or not nome or not senha:
            return render_template("cadastrar_professor.html", erro="Preencha todos os campos.")

        if email in usuarios:
            return render_template("cadastrar_professor.html", erro="Já existe um usuário com esse e-mail.")

        # cria o usuário professor
        usuarios[email] = {"nome": nome, "senha": senha, "tipo": "professor"}
        salvar_usuarios()  # você já tem essa função

        # volta para home do professor
        return redirect("/")

    # GET
    return render_template("cadastrar_professor.html", erro=None)


@app.route("/matricular", methods=["GET", "POST"])
def matricular():
    if session.get("tipo") != "professor":
        return redirect("/")

    # Categoria visível para este professor: "piloto" | "mecanico" | None
    cat = prof_categoria_atual()

    if request.method == "POST":
        alunos_email = request.form.getlist("alunos[]")  # lista de e-mails
        curso_nome   = (request.form.get("curso") or "").strip()
        professor    = (request.form.get("professor") or "").strip()
        nrt_turma    = (request.form.get("nrt") or "").strip()
        data_inicio  = (request.form.get("data_inicio") or "").strip()
        data_fim     = (request.form.get("data_fim") or "").strip()

        try:
            periodicidade_anos = int(request.form.get("periodicidade", "1"))
        except ValueError:
            periodicidade_anos = 1
        if periodicidade_anos not in (1, 2, 3, 5):
            periodicidade_anos = 1

        tipo_matricula = (request.form.get("tipo") or "").strip()
        turma_form     = (request.form.get("turma") or "").strip()

        # ---------- resolve número da turma ----------
        turma_num = None
        if turma_form:
            if turma_form.isdigit():
                turma_form = f"{int(turma_form):03d}"
            if len(turma_form) == 3 and turma_form.isdigit():
                turma_num = turma_form

        # se já existir a turma para o curso, força criar automaticamente a próxima
        if turma_num and any(m.get("curso") == curso_nome and m.get("turma") == turma_num for m in matriculas):
            turma_num = None

        if not turma_num:
            last = int(turmas_ctrl.get(curso_nome, 0))
            if last >= 250:
                # volta para o form com erro e listas filtradas pela categoria
                alunos_ctx = [
                    {"email": e, "nome": d["nome"]}
                    for e, d in usuarios.items()
                    if d.get("tipo") == "aluno" and _aluno_e_da_categoria(e, cat)
                ]
                professores = _lista_instrutores_por_categoria(cat)
                sugestoes_por_curso = {
                    c["nome"]: f"{min(int(turmas_ctrl.get(c['nome'], 0)) + 1, 250):03d}" for c in cursos
                }
                return render_template(
                    "matricular.html",
                    alunos=alunos_ctx,
                    cursos=cursos,
                    professores=professores,
                    sugestoes_por_curso=sugestoes_por_curso,
                    erro="Limite máximo de 250 turmas atingido para este curso."
                )

            # cria próxima turma automaticamente (💡 ESTE BLOCO FICA DENTRO DO if not turma_num:)
            nxt = last + 1
            turmas_ctrl[curso_nome] = nxt
            salvar_dados(CAMINHO_TURMAS, turmas_ctrl)
            turma_num = f"{nxt:03d}"

        # ---------- matrícula (⚠️ este FOR precisa estar DESALINHADO UM NÍVEL para a ESQUERDA) ----------
        for aluno_email in alunos_email:
            if not _aluno_e_da_categoria(aluno_email, cat):
                continue
            if not any(m["aluno"] == aluno_email and m["curso"] == curso_nome for m in matriculas):
                matriculas.append({
                    "aluno":         aluno_email,
                    "curso":         curso_nome,
                    "professor":     professor,
                    "tipo":          tipo_matricula,
                    "nrt":           nrt_turma,
                    "turma":         turma_num,
                    "data_inicio":   data_inicio,
                    "data_fim":      data_fim,
                    "periodicidade": periodicidade_anos,
                })

        salvar_dados(CAMINHO_MATRICULAS, matriculas)
        flash("Matriculado com Sucesso!", "success")
        return redirect(url_for("home"))

    # --- GET ---
    alunos = [
        {"email": e, "nome": d["nome"]}
        for e, d in usuarios.items()
        if d.get("tipo") == "aluno" and _aluno_e_da_categoria(e, cat)
    ]

    # 🔽 nomes do <select> Professor, já filtrados pela categoria
    professores = _lista_instrutores_por_categoria(cat)

    sugestoes_por_curso = {
        c["nome"]: f"{min(int(turmas_ctrl.get(c['nome'], 0)) + 1, 250):03d}" for c in cursos
    }

    return render_template(
        "matricular.html",
        alunos=alunos,
        cursos=cursos,
        professores=professores,
        sugestoes_por_curso=sugestoes_por_curso
    )


            
@app.route("/editar_curso/<path:nome>", methods=["GET", "POST"])
def editar_curso_nome(nome):
    if session.get("tipo") != "professor":
        return redirect("/login")

    curso = next((c for c in cursos if c["nome"] == nome), None)
    if not curso:
        return "Curso não encontrado", 404

    if request.method == "POST":
    # Atualiza campos básicos
        curso["carga_horaria"] = request.form.get("carga_horaria", curso.get("carga_horaria"))
        curso["instrutor"]     = request.form.get("instrutor", curso.get("instrutor", ""))
        curso["conteudo"]      = request.form.get("conteudo", curso.get("conteudo", ""))

    # -------- MÓDULOS (preserva arquivo se não enviar um novo) --------
    novos_modulos = []
    idx = 0
    while True:
        titulo = request.form.get(f"modulos[{idx}][titulo]")
        if titulo is None:
            break  # chegou ao fim
        titulo = titulo.strip()
        if not titulo:
            idx += 1
            continue

        file = request.files.get(f"modulos[{idx}][arquivo]")
        arquivo_atual = request.form.get(f"modulos[{idx}][arquivo_atual]", "").strip()

        arquivo_nome = None
        if file and file.filename:
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                caminho = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(os.path.dirname(caminho), exist_ok=True)
                file.save(caminho)
                arquivo_nome = filename
        else:
            # mantém o arquivo já existente, se houver
            if arquivo_atual:
                arquivo_nome = arquivo_atual

        novos_modulos.append({
            "titulo":  titulo,
            "arquivo": arquivo_nome
        })
        idx += 1

    curso["modulos"] = novos_modulos

    # -------- PROVA (permite editar perguntas) --------
    novas_perguntas = []
    # coletar todos os campos "perguntas[i][campo]"
    for key, val in request.form.items():
        if key.startswith("perguntas[") and "][" in key:
            try:
                i = int(key.split("[")[1].split("]")[0])
                campo = key.split("][")[1].rstrip("]")
            except (IndexError, ValueError):
                continue
            while len(novas_perguntas) <= i:
                novas_perguntas.append({"enunciado":"", "a":"", "b":"", "c":"", "d":"", "correta":""})
            novas_perguntas[i][campo] = val

    curso["prova"] = [q for q in novas_perguntas if q.get("enunciado")]

    salvar_dados(CAMINHO_CURSOS, cursos)
    return redirect(url_for("lista_cursos_para_editar"))

@app.route("/editar_curso_form", methods=["GET", "POST"])
def editar_curso_form_handler():
    if session.get("tipo") != "professor":
        return redirect("/login")

    nome = request.args.get("nome", "").strip()
    curso = next((c for c in cursos if c.get("nome") == nome), None)
    if not curso:
        return "Curso não encontrado", 404

    # garante chaves básicas
    curso.setdefault("carga_horaria", "")
    curso.setdefault("conteudo", "")
    curso.setdefault("modulos", [])
    curso.setdefault("prova", [])

    if request.method == "POST":
        # --------- CAMPOS SIMPLES ---------
        curso["carga_horaria"] = request.form.get("carga_horaria", curso["carga_horaria"]).strip()
        curso["conteudo"]      = request.form.get("conteudo", curso["conteudo"]).strip()

        # --------- MÓDULOS (multi-upload) ---------
        # Captura todos os índices presentes no POST
        mod_idxs = set()
        for k in request.form.keys():
            if k.startswith("modulos[") and "][titulo]" in k:
                try:
                    mod_idxs.add(int(k.split("[")[1].split("]")[0]))
                except:
                    pass
        for k in request.files.keys():
            if k.startswith("modulos[") and "][arquivo]" in k:
                try:
                    mod_idxs.add(int(k.split("[")[1].split("]")[0]))
                except:
                    pass

        new_modulos = []
        for i in sorted(mod_idxs):
            titulo = (request.form.get(f"modulos[{i}][titulo]") or "").strip()
            remover = request.form.get(f"modulos[{i}][remover]") == "on"
            atual   = (request.form.get(f"modulos[{i}][arquivo_atual]") or "").strip()
            file    = request.files.get(f"modulos[{i}][arquivo]")

            if remover:
                # pula (remoção)
                continue

            filename = atual
            if file and file.filename:
                raw = secure_filename(file.filename)
                # evita sobrescrever: prefixo com timestamp
                filename = f"{int(time.time())}_{raw}"
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # só adiciona módulo se tiver ao menos título ou arquivo
            if titulo or filename:
                new_modulos.append({"titulo": titulo, "arquivo": filename})

        curso["modulos"] = new_modulos

        # --------- PROVA (perguntas) ---------
        q_idxs = set()
        for k in request.form.keys():
            if k.startswith("perguntas[") and "][" in k:
                try:
                    q_idxs.add(int(k.split("[")[1].split("]")[0]))
                except:
                    pass

        novas_perguntas = []
        for i in sorted(q_idxs):
            rmv = request.form.get(f"perguntas[{i}][remover]") == "on"
            en  = (request.form.get(f"perguntas[{i}][enunciado]") or "").strip()
            a   = (request.form.get(f"perguntas[{i}][a]") or "").strip()
            b   = (request.form.get(f"perguntas[{i}][b]") or "").strip()
            c   = (request.form.get(f"perguntas[{i}][c]") or "").strip()
            d   = (request.form.get(f"perguntas[{i}][d]") or "").strip()
            cor = (request.form.get(f"perguntas[{i}][correta]") or "").strip()

            if rmv:
                continue

            # só guarda se tiver enunciado
            if en:
                novas_perguntas.append({
                    "enunciado": en,
                    "a": a, "b": b, "c": c, "d": d,
                    "correta": cor
                })

        curso["prova"] = novas_perguntas

        salvar_dados(CAMINHO_CURSOS, cursos)
        return redirect(url_for("lista_cursos_para_editar"))

    # GET: envia dados atuais
    return render_template(
        "editar_curso_form.html",
        curso=curso,
        mods=curso["modulos"],
        perguntas=curso["prova"],
        enumerate=enumerate,     # ok usar enumerate no template, se quiser
    )

@app.route("/perfil/foto", methods=["POST"])
def atualizar_foto_perfil():
    if "usuario" not in session:
        return redirect("/login")

    email = session["usuario"]
    file = request.files.get("foto")
    if not file or file.filename.strip() == "":
        return redirect("/")

    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in {"png", "jpg", "jpeg", "webp"}:
        return redirect("/")

    safe_email = email.replace("@", "_at_").replace(".", "_")
    final_name = f"{safe_email}.{ext}"
    save_path = os.path.join(AVATAR_DIR, final_name)
    file.save(save_path)

    rel_path = f"avatars/{final_name}"
    usuarios.setdefault(email, {})
    usuarios[email]["foto"] = rel_path
    salvar_dados(CAMINHO_USUARIOS, usuarios)

    return redirect("/")


@app.route("/editar_curso", endpoint="lista_cursos_para_editar")
def lista_cursos_para_editar():
    if session.get("tipo") != "professor":
        return redirect("/login")

    alunos = {email: dados for email, dados in usuarios.items() if dados["tipo"] == "aluno"}
    return render_template("editar_curso.html", cursos=cursos, alunos=alunos, matriculas=matriculas, usuarios=usuarios)

    if session.get("tipo") != "professor":
        return redirect("/login")

    return render_template("editar_curso.html", cursos=cursos)

@app.route("/remover_matricula", methods=["POST"])
def remover_matricula():
    curso_nome = request.form["curso"]
    aluno_id = request.form["aluno"]

    global matriculas
    matriculas = [m for m in matriculas if not (m["curso"] == curso_nome and m["aluno"] == aluno_id)]

    salvar_dados(CAMINHO_MATRICULAS, matriculas)  # <- salvando a alteração no disco

    return redirect(url_for("lista_cursos_para_editar"))

    
@app.route("/remover_curso", methods=["POST"])
def remover_curso():
    nome = request.form["curso"]
    global cursos, matriculas
    cursos = [c for c in cursos if c["nome"] != nome]
    matriculas = [m for m in matriculas if m["curso"] != nome]

    salvar_dados(CAMINHO_CURSOS, cursos)
    salvar_dados(CAMINHO_MATRICULAS, matriculas)

    return redirect(url_for("lista_cursos_para_editar"))

# ======================================================================
#                       ROTAS (ALUNO)
# ======================================================================
@app.route("/ver_material/<curso>", methods=["GET", "POST"])
def ver_material(curso):
    if "usuario" not in session:
        return redirect("/login")

    aluno = session["usuario"]
    curso_obj = next((c for c in cursos if c["nome"] == curso), None)
    if not curso_obj:
        return "Curso não encontrado", 404

    print("DEBUG ARQUIVO:", curso_obj["modulos"][0]["arquivo"] if curso_obj.get("modulos") else "SEM MODULOS")

    # Pega a lista de módulos (ou lista vazia)
    modulos = curso_obj.get("modulos", [])
    total_modulos = len(modulos)

    # Sanitiza o índice do módulo
    try:
        modulo_atual = int(request.args.get("modulo", 0))
    except (TypeError, ValueError):
        modulo_atual = 0

    if total_modulos > 0:
        modulo_atual = max(0, min(modulo_atual, total_modulos - 1))
    else:
        modulo_atual = None  # não há módulos

    session["start_time"] = datetime.now().isoformat()
    session["curso_visualizado"] = curso

    if aluno not in progresso_por_aluno:
        progresso_por_aluno[aluno] = {}

    # Garante que a lista de progresso tenha o tamanho certo
    progresso_individual = progresso_por_aluno[aluno].get(curso, [0] * total_modulos)
    if len(progresso_individual) < total_modulos:
        progresso_individual = (progresso_individual + [0] * total_modulos)[:total_modulos]

    # Marca módulo como 100% concluído (se existir módulo)
    if modulo_atual is not None and 0 <= modulo_atual < total_modulos:
        progresso_individual[modulo_atual] = 100

    progresso_por_aluno[aluno][curso] = progresso_individual

    # Salva o progresso no disco
    salvar_dados(CAMINHO_PROGRESSO, progresso_por_aluno)
    salvar_dados(CAMINHO_CURSOS, cursos)

    progresso_total = int(sum(progresso_individual) / (100 * total_modulos) * 100) if total_modulos > 0 else 0

    return render_template(
        "ver_material.html",
        curso=curso_obj,
        modulo_atual=modulo_atual,
        progresso=progresso_total
    )


@app.route("/concluir/<nome>", methods=["POST"])
def concluir(nome):
    if session.get("tipo") != "aluno":
        return redirect("/login")

    aluno_email = session["usuario"]
    start_iso = session.get("start_time")
    curso_visualizado = session.get("curso_visualizado")

    if not (start_iso and curso_visualizado == nome):
        return redirect("/")  # valida antes de apagar

    session.pop("start_time", None)
    session.pop("curso_visualizado", None)

    elapsed = (datetime.now() - datetime.fromisoformat(start_iso)).total_seconds() / 60
    curso = next((c for c in cursos if c["nome"] == nome), None)

    if curso:
        curso.setdefault("progresso", {})[aluno_email] = {
            "tempo": round(elapsed, 2),
            "concluido": True
        }

        # ✅ salva progresso no disco
        salvar_dados(CAMINHO_CURSOS, cursos)

        return redirect(url_for("lista_presenca", curso=nome))


@app.route("/ver_lista_presenca/<aluno>/<curso>")
def ver_lista_presenca(aluno, curso):
    # 1) Garante que só professor acesse
    if session.get("tipo") != "professor":
        return redirect("/login")

    # 2) Busca o objeto do curso
    curso_obj = next((c for c in cursos if c["nome"] == curso), None)
    if not curso_obj:
        return "Curso não encontrado", 404

    # 3) Busca matrículas desse curso
    matriculas_do_curso = [m for m in matriculas if m["curso"] == curso]

    # 4) Monta o dicionário presencas: { "Nome Completo": bool_assinou }
    #    Aqui você decide onde vai armazenar o fato de ter assinado (ex: em curso_obj["presencas"])
    presencas = {}
    for m in matriculas_do_curso:
        email_aluno = m["aluno"]
        nome_aluno  = usuarios[email_aluno]["nome"]
        # lê diretamente da matrícula o flag que o aluno assinou
        signed = m.get("presenca_assinada", False)
        presencas[nome_aluno] = signed
    
    instrutor_matricula = (
        matriculas_do_curso[0]["professor"]
        if matriculas_do_curso
        else curso_obj.get("instrutor", "---")
    )
    carga_horaria = curso_obj.get("carga_horaria", "---")
 

    # 5) Meta­dados para exibir no cabeçalho
    fuso_sp = pytz.timezone("America/Sao_Paulo")
    agora = datetime.now(fuso_sp)
    data = agora.strftime("%d/%m/%Y")
    hora = agora.strftime("%H:%M")
    ip = gerar_ip_falso()  

    turma_nrt = matriculas_do_curso[0].get("nrt", "---") if matriculas_do_curso else "---"  # ⬅️ NOVO

    return render_template(
        "visualizar_lista_presenca.html",
        curso=curso_obj,
        nrt=turma_nrt,                 # ⬅️ USA A NRT DA TURMA (MATRÍCULA)
        carga_horaria=carga_horaria,
        instrutor=instrutor_matricula,
        data=data,
        hora=hora,
        ip=ip,
        presencas=presencas    
    )


# Página de lista de presença
@app.route("/lista_presenca/<curso>", methods=["GET", "POST"])
def lista_presenca(curso):
    if session.get("tipo") != "aluno":
        return redirect("/login")

    email = session["usuario"]
    curso_obj = next((c for c in cursos if c["nome"] == curso), None)
    matricula = next((m for m in matriculas if m["aluno"] == email and m["curso"] == curso), None)
    if not (curso_obj and matricula):
        return "Curso ou matrícula não encontrado", 404

    if "presenca_assinada" not in matricula:
        matricula["presenca_assinada"] = False

    fuso_sp = pytz.timezone("America/Sao_Paulo")
    agora   = datetime.now(fuso_sp)
    data    = agora.strftime("%d/%m/%Y")
    hora    = agora.strftime("%H:%M")
    ip      = gerar_ip_falso()
    carga_horaria = curso_obj.get("carga_horaria", "")

    if request.method == "POST":
        matricula["presenca_assinada"] = True
        salvar_dados(CAMINHO_MATRICULAS, matriculas)

    return render_template("lista_presenca.html",
                           curso=curso_obj,
                           aluno=usuarios[email]["nome"],
                           instrutor=matricula["professor"],
                           nrt=matricula.get("nrt", ""),
                           carga_horaria=carga_horaria,
                           data=data,
                           hora=hora,
                           ip=ip,
                           presenca=matricula["presenca_assinada"])


@app.route("/central-aluno")
def central_aluno():
    if "usuario" not in session or session["tipo"] != "aluno":
        return redirect("/login")

    email = session["usuario"]

    # Pega as matrículas do aluno
    minhas_matriculas = [m for m in matriculas if m["aluno"] == email]

    cursos_disp = []
    for m in minhas_matriculas:
        curso = next((c for c in cursos if c["nome"] == m["curso"]), None)
        if not curso:
            continue

        progresso = curso.get("progresso", {}).get(email, {"concluido": False})
        resultado = curso.get("resultados", {}).get(email)
        presenca_ok = m.get("presenca_assinada", False)

        aprovado = resultado and resultado["acertos"] >= 0.7 * resultado["total"]
        pode_emitir_certificado = progresso["concluido"] and presenca_ok and aprovado

        cursos_disp.append({
            "nome": curso["nome"],
            "modulos": curso.get("modulos", []),
            "progresso": progresso,
            "data_fim": m.get("data_fim"),
            "certificado_disponivel": pode_emitir_certificado
        })

    return render_template(
        "home_aluno.html",
        usuario=usuarios[email]["nome"],
        cursos=cursos_disp
    )

    
@app.route("/perfil", methods=["GET", "POST"])
def perfil_aluno():
    if session.get("tipo") != "aluno":
        return redirect("/login")

    email = session["usuario"]

    if request.method == "POST":
        nova_senha = request.form.get("senha")
        if nova_senha:
            usuarios[email]["senha"] = nova_senha
            salvar_dados(CAMINHO_USUARIOS, usuarios)  # ⬅️ Salva a nova senha no disco
        return redirect("/perfil")

    return render_template("perfil_aluno.html", usuario=usuarios[email])


@app.route("/prova/<nome>", methods=["GET", "POST"])
def prova(nome):
    if session.get("tipo") != "aluno":
        return redirect("/login")

    aluno_email = session["usuario"]
    curso = next((c for c in cursos if c["nome"] == nome), None)
    if not curso:
        return "Curso não encontrado", 404

    # matrícula (para mostrar se assinou presença)
    matricula = next((m for m in matriculas if m["aluno"] == aluno_email and m["curso"] == nome), None)
    presenca_assinada = matricula.get("presenca_assinada", False) if matricula else False

    perguntas = curso.get("prova", [])

    if request.method == "POST":
        # ----- coletar escolhas do aluno -----
        escolhas = {}  # ex.: {"0":"a","1":"d","2":"b"}
        acertos = 0
        total = len(perguntas)

        for i, p in enumerate(perguntas):
            esc = (request.form.get(f"pergunta_{i}") or "").strip()
            escolhas[str(i)] = esc
            if esc and esc == p.get("correta"):
                acertos += 1

        aprovado = (acertos >= 0.7 * total) if total > 0 else True
        porcentagem = int((acertos / total) * 100) if total > 0 else 0

        # ----- salvar RESULTADO agregado (como você já fazia) -----
        curso.setdefault("resultados", {})[aluno_email] = {
            "acertos": acertos,
            "total": total,
            "porcentagem": porcentagem,
            "aprovado": aprovado,
            "quando": datetime.now(TZ).isoformat(),
        }

        # ----- salvar ESCOLHAS por pergunta -----
        # guarda tanto o mapa escolhas quanto um detalhamento por pergunta
        detalhes = []
        for i, p in enumerate(perguntas):
            marcada = escolhas.get(str(i), "")
            detalhes.append({
                "i": i,
                "enunciado": p.get("enunciado", ""),
                "correta": p.get("correta", ""),
                "marcada": marcada,
                "ok": (marcada == p.get("correta", "")),
            })

        curso.setdefault("respostas", {})[aluno_email] = {
            "escolhas": escolhas,   # simples e leve
            "detalhe": detalhes,    # pronto para exibir/baixar depois
            "quando": datetime.now(TZ).isoformat(),
        }

        # persiste no disco
        salvar_dados(CAMINHO_CURSOS, cursos)

        # renderiza a mesma tela com o resultado (compatível com seu template atual)
        return render_template(
            "prova.html",
            curso=curso,
            enumerate=enumerate,
            enviado=True,
            acertos=acertos,
            total=total,
            porcentagem=porcentagem,
            aprovado=aprovado,
            presenca_assinada=presenca_assinada,
            escolhas=escolhas  # opcional; template pode ignorar
        )

    # GET: exibe a prova
    return render_template(
        "prova.html",
        curso=curso,
        enumerate=enumerate,
        presenca_assinada=presenca_assinada
    )




@app.route("/certificado_confirmacao/<aluno>/<curso>")
def certificado_confirmacao(aluno, curso):
    if session.get("usuario") != aluno:
        return redirect("/login")

    curso_obj = next((c for c in cursos if c["nome"] == curso), None)
    resultado = curso_obj.get("resultados", {}).get(aluno) if curso_obj else None
    if not (curso_obj and resultado and resultado["acertos"] >= 0.7 * resultado["total"]):
        return "Não autorizado.", 403

    return render_template(
        "certificado_confirmacao.html",
        aluno_email=aluno,
        aluno_nome=usuarios[aluno]["nome"],
        curso=curso_obj["nome"],
        acertos=resultado["acertos"],
        total=resultado["total"],
    )
# ======================================================================
#                NOVA ROTA  –  CONFIRMAÇÃO DE ASSINATURA
# ======================================================================
@app.route("/assinar_certificado/<aluno>/<curso>")
def assinar_certificado(aluno, curso):
    return redirect(url_for('emitir_certificado', aluno=aluno, curso=curso))

  # ======================================================================
#                 EMISSÃO / ASSINATURA DE CERTIFICADO
# ======================================================================
@app.route("/emitir_certificado/<aluno>/<curso>", methods=["GET", "POST"])
def emitir_certificado(aluno, curso):
    if "usuario" not in session:
        return redirect("/login")

    tipo_usuario = session.get("tipo")
    email_logado = session.get("usuario").lower()

    if tipo_usuario == "aluno" and email_logado != aluno.lower():
        return redirect("/login")

    curso_obj = next((c for c in cursos if c["nome"] == curso), None)
    if not curso_obj:
        return "Curso não encontrado", 404

    resultado = curso_obj.get("resultados", {}).get(aluno)
    if not (resultado and resultado["acertos"] >= 0.7 * resultado["total"]):
        return "Não autorizado.", 403

    # Recupera o professor definido na matrícula
    matricula = next((m for m in matriculas if m["aluno"] == aluno and m["curso"] == curso), None)
    professor_assinante = matricula["professor"] if matricula else curso_obj.get("instrutor", "—")

    emitido_em = obter_data_certificado_fixa(aluno=aluno, curso=curso)

    # --------- CÁLCULO E GRAVAÇÃO DO VENCIMENTO (agora dentro da função) ----------
    periodicidade_anos = 1
    if matricula:
        try:
            periodicidade_anos = int(matricula.get("periodicidade", 1))
        except (ValueError, TypeError):
            periodicidade_anos = 1
    if periodicidade_anos not in (1, 2, 3, 5):
        periodicidade_anos = 1

    # data de emissão preferindo ISO
    emissao_date = None
    iso = emitido_em.get("iso")
    if iso:
        try:
            emissao_date = datetime.fromisoformat(iso).date()
        except Exception:
            emissao_date = None
    if emissao_date is None:
        # fallback "dd/mm/YYYY"
        try:
            emissao_date = datetime.strptime(emitido_em.get("data", ""), "%d/%m/%Y").date()
        except Exception:
            emissao_date = datetime.now(TZ).date()

    venc_date = add_years(emissao_date, periodicidade_anos)
    venc_str  = venc_date.strftime("%Y-%m-%d")

    global vencimentos
    vencimentos = [
        v for v in vencimentos
        if not (v.get("aluno") == aluno and v.get("curso") == curso)
    ]
    vencimentos.append({
        "aluno": aluno,
        "curso": curso,
        "data_vencimento": venc_str,
    })
    salvar_vencimentos()
    # --------- FIM DO CÁLCULO/GRAVAÇÃO DO VENCIMENTO -----------------------------

    data_assinatura_instrutor = emitido_em["data"]
    hora_assinatura_instrutor = emitido_em["hora"]
    data_assinatura_aluno     = emitido_em["data"]
    hora_assinatura_aluno     = emitido_em["hora"]

    carga     = curso_obj.get("carga_horaria", "")
    conteudo  = curso_obj.get("conteudo", "")
    aluno_nome = usuarios.get(aluno, {}).get("nome", aluno)

    # Registrar que o certificado foi emitido
    curso_obj.setdefault("certificados_emitidos", {})[aluno] = {
        "data": data_assinatura_instrutor,
        "hora": hora_assinatura_instrutor,
        "ip": gerar_ip()
    }
    salvar_dados(CAMINHO_CURSOS, cursos)

    return render_template(
        "certificado.html",
        aluno_nome=aluno_nome,
        curso=curso,
        carga=carga,
        conteudo=conteudo,
        instrutor=professor_assinante,
        data_emissao=data_assinatura_instrutor,
        data_assinatura_aluno=data_assinatura_aluno,
        hora_assinatura_aluno=hora_assinatura_aluno,
        data_assinatura_instrutor=data_assinatura_instrutor,
        hora_assinatura_instrutor=hora_assinatura_instrutor,
        ip_instrutor=gerar_ip(),
        ip_aluno=gerar_ip()
    )

@app.route("/vencimentos/excluir", methods=["POST"])
def vencimentos_excluir():
    if session.get("tipo") != "professor":
        return redirect("/login")

    aluno = (request.form.get("aluno") or "").strip().lower()
    curso = (request.form.get("curso") or "").strip()

    global vencimentos
    antes = len(vencimentos)
    vencimentos = [
        v for v in vencimentos
        if not (v.get("aluno") == aluno and v.get("curso") == curso)
    ]
    if len(vencimentos) != antes:
        salvar_vencimentos()
    return redirect("/vencimentos/verificar")


@app.route("/vencimentos/editar", methods=["GET", "POST"])
def vencimentos_editar():
    if session.get("tipo") != "professor":
        return redirect("/login")

    aluno = (request.args.get("aluno") or request.form.get("aluno") or "").strip().lower()
    curso = (request.args.get("curso") or request.form.get("curso") or "").strip()

    # acha o registro
    reg = next((v for v in vencimentos if v.get("aluno") == aluno and v.get("curso") == curso), None)
    if not reg:
        # se não existe, volta para verificar
        return redirect("/vencimentos/verificar")

    if request.method == "POST":
        nova_data = (request.form.get("data_vencimento") or "").strip()  # YYYY-MM-DD
        # valida formato simples
        try:
            datetime.strptime(nova_data, "%Y-%m-%d")
            reg["data_vencimento"] = nova_data
            salvar_vencimentos()
            return redirect("/vencimentos/verificar")
        except Exception:
            # só re-renderiza com erro
            aluno_nome = usuarios.get(aluno, {}).get("nome", aluno)
            return render_template("vencimentos_editar.html",
                                   aluno_email=aluno,
                                   aluno_nome=aluno_nome,
                                   curso=curso,
                                   data_vencimento=nova_data,
                                   erro="Data inválida. Use o formato AAAA-MM-DD.")

    # GET
    aluno_nome = usuarios.get(aluno, {}).get("nome", aluno)
    return render_template("vencimentos_editar.html",
                           aluno_email=aluno,
                           aluno_nome=aluno_nome,
                           curso=curso,
                           data_vencimento=reg.get("data_vencimento", ""))
# ======================================================================
#                       RELATÓRIOS / UTIL
# ======================================================================

@app.route("/acompanhamento")
def acompanhamento():
    if session.get("tipo") != "professor":
        return redirect("/login")

    cat = prof_categoria_atual()
    enrollments = []
    for m in matriculas:
        # 🔽 respeita a categoria (piloto/mecanico) do professor
        if not _aluno_e_da_categoria(m.get("aluno",""), cat):
            continue

        curso_nome = m.get("curso")
        if not curso_nome:
            continue
        curso_obj = next((c for c in cursos if c.get("nome") == curso_nome), None)
        if not curso_obj:
            continue

        m_ref    = next((mm for mm in matriculas if mm["aluno"] == m["aluno"] and mm["curso"] == curso_nome), None)
        turma_num = m_ref.get("turma", "—") if m_ref else "—"
        nrt_val   = m_ref.get("nrt", "—")   if m_ref else "—"
        tipo_val  = m_ref.get("tipo", "—")  if m_ref else "—"

        prog = curso_obj.get("progresso", {}).get(m["aluno"], {"tempo": "---", "concluido": False})
        res  = curso_obj.get("resultados", {}).get(m["aluno"], {"acertos": 0, "total": 0})
        nota_num = (res["acertos"] / res["total"] * 100) if res.get("total") else 0.0
        nota     = f"{round(nota_num,1)}%" if res.get("total") else "---"
        aprovado = (res.get("total", 0) > 0 and res.get("acertos", 0) >= 0.7 * res["total"])
        cert_emitido = bool(curso_obj.get("certificados_emitidos", {}).get(m["aluno"]))

        enrollments.append({
            "curso":        curso_obj,
            "aluno":        usuarios.get(m["aluno"], {}).get("nome", m["aluno"]),
            "email":        m["aluno"],
            "tempo":        prog.get("tempo", "---"),
            "concluido":    bool(prog.get("concluido")),
            "nota":         nota,
            "nota_num":     nota_num,
            "nrt":          nrt_val,
            "turma":        turma_num,
            "tipo":         tipo_val,
            "aprovado":     aprovado,
            "cert_emitido": cert_emitido,
        })

    salvar_dados(CAMINHO_CURSOS, cursos)
    salvar_dados(CAMINHO_MATRICULAS, matriculas)
    return render_template("acompanhamento.html", enrollments=enrollments)


@app.route("/prova_resultado/<aluno>/<curso>")
def prova_resultado(aluno, curso):
    # somente professor
    if session.get("tipo") != "professor":
        return redirect("/login")

    curso_obj = next((c for c in cursos if c["nome"] == curso), None)
    if not curso_obj:
        return "Curso não encontrado", 404

    # precisa ter resultado, aprovado e certificado emitido
    resultado = curso_obj.get("resultados", {}).get(aluno)
    if not resultado:
        return "Prova ainda não realizada.", 403

    aprovado = (resultado["acertos"] >= 0.7 * resultado["total"])
    cert_emitido = bool(curso_obj.get("certificados_emitidos", {}).get(aluno))
    if not (aprovado and cert_emitido):
        return "Disponível apenas após aprovação e emissão do certificado.", 403

    aluno_nome = usuarios.get(aluno, {}).get("nome", aluno)
    questoes   = curso_obj.get("prova", [])  # lista com enunciado, a/b/c/d, correta
    # respostas do aluno: guardadas por name dos inputs em prova.html
    # se você não armazena as alternativas marcadas, mostramos só o gabarito/correção
    respostas_aluno = curso_obj.get("respostas", {}).get(aluno, {})  # opcional

    return render_template(
        "prova_resultado.html",
        aluno_email=aluno,
        aluno_nome=aluno_nome,
        curso_nome=curso,
        resultado=resultado,
        questoes=questoes,
        respostas_aluno=respostas_aluno,
        enumerate=enumerate,
    )


@app.route("/fale_tutor")
def fale_tutor():
    if "usuario" in session:
        return render_template("fale_tutor.html", usuario=session["usuario"])
    return redirect("/login")


# ----------------------------- MAIN -----------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
