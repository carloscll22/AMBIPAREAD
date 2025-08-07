from flask import Flask, render_template, request, redirect, session, url_for
from random import randint
from werkzeug.utils import secure_filename  
from datetime import datetime
import pytz
import shutil    
import os
import json

CAMINHO_USUARIOS = "/mnt/data/usuarios.json"
CAMINHO_CURSOS = "/mnt/data/cursos.json"
CAMINHO_MATRICULAS = "/mnt/data/matriculas.json"
CAMINHO_PROGRESSO = "/mnt/data/progresso.json"

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

def salvar_usuarios():
    with open(CAMINHO_USUARIOS, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, indent=2, ensure_ascii=False)



# variável global opcional
progresso_por_aluno = {}

UPLOAD_FOLDER = 'static/conteudos'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx', 'jpg', 'jpeg', 'png', 'mp4', 'mp3', 'zip', 'rar', 'txt', 'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "chave_secreta"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB
def gerar_ip_falso() -> str:
    """Gera um IP v4 aleatório tipo '87.142.233.19'."""
    return ".".join(str(randint(10, 254)) for _ in range(4))
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# ----------------------------------------------------------------------
#  USUÁRIOS PRÉ‑CADASTRADOS  (e‑mail → dados)
# ----------------------------------------------------------------------
usuarios = {"cmte.siqueira@ambipar.com":  {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Airton Benedito De Siqueira Junior"},
    "cmte.taskilas@ambipar.com":  {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Alexandre Kopfer Martins"},
    "andre.gustavo@ambipar.com":  {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Andre Gustavo Chialastri Altounian"},
    "cmte.sales@ambipar.com":     {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Andre Luis Damazio De Sales"},
    "andre.lyra@ambipar.com":     {"senha": "Ambipar2025", "tipo": "aluno", "nome": "André Palazzo Lyra"},
    "antonio.jorge@ambipar.com":  {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Antonio Jorge De Souza Neto"},
    "bruna.tasca@ambipar.com":    {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Bruna Maria Tasca"},
    "carlos.negreiros@ambipar.com": {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Carlos Augusto Da Silva Negreiros"},
    "carlos.maria@ambipar.com":   {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Carlos Eduardo Alho Maria"},
    "carlos.moraes@ambipar.com":  {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Carlos Eduardo Vizentim De Moraes"},
    "cmte.franck@ambipar.com":    {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Carlos Franck Da Costa Simanke"},
    "cmte.rubens@ambipar.com":    {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Carlos Rubens Prudente Melo"},
    "cmte.celio@ambipar.com":     {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Celio Ricardo De Albuquerque Pimentel"},
    "charles.pannain@ambipar.com": {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Charles Pires Pannain"},
    "cmte.cleyton@ambipar.com":   {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Cleyton De Oliveira Almeida"},
    "daniel.telles@ambipar.com":  {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Daniel De Sousa Freitas Da Silva Telles"},
    "danielle.pereira@ambipar.com": {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Danielle Dos Santos Pereira"},
    "djalma.neto@ambipar.com":    {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Djalma Da Conceição Neto"},
    "eduardo.antonio@ambipar.com": {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Eduardo Antonio Ferreira"},
    "eduardo.worm@ambipar.com":   {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Eduardo Dupke Worm"},
    "fabio.araujo@ambipar.com":   {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Fabio Amaral Goes De Araujo"},
    "fernando.telles@ambipar.com": {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Fernando Carlos Da Silva Telles"},
    "flavio.santos@ambipar.com":  {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Flavio Ramalho Dos Santos"},
    "hazafe.alencar@ambipar.com": {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Hazafe Pacheco De Alencar"},
    "cmte.isaac@ambipar.com":     {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Isaac Barreto De Andrade"},
    "jairodop@hotmail.com":       {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Jairo De Oliveira Pereira"},
    "cmte.trajano@ambipar.com":   {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Jerusa Cristiane Alves Trajano Da Silva"},
    "leonardo.rapini@ambipar.com": {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Leonardo Pompein Campos Rapini"},
    "lohana.tose@ambipar.com":    {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Lohana Detes Tose"},
    "cmte.mattara@ambipar.com":   {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Lucas Medonça Mattara"},
    "cmte.pessoa@ambipar.com":    {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Luís Eduardo Santana Pessôa De Oliveira"},
    "cmte.marron@ambipar.com":    {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Luiz Fellipe Marron Rabello"},
    "luiz.lima@ambipar.com":      {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Luiz Fernando Lima"},
    "manollo.jordao@ambipar.com": {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Manollo Aleixo Jordão"},
    "cmte.metre@ambipar.com":     {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Marcelo Ricardo Soares Metre"},
    "marcelo.hashizume@ambipar.com": {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Marcelo Teruo Hashizume"},
    "mateus.sousa@ambipar.com":   {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Mateus Cruz De Sousa"},
    "matheus.fraga@ambipar.com":  {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Matheus Tondin Fraga"},
    "cmte.mauricio@ambipar.com":  {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Mauricio Andries Dos Santos"},
    "paulo.claudino@ambipar.com": {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Paulo Cesar Machado Claudino"},
    "p.jalmeida@yahoo.com.br":    {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Paulo Jose Nunes De Almeida"},
    "cmte.paulinho@ambipar.com":  {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Paulo Roberto De Andrade Costa"},
    "cmte.chacon@ambipar.com":    {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Ricardo Chacon Veeck"},
    "ricardo.ramos@ambipar.com":  {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Ricardo De Moraes Ramos"},
    "rodrigo.vasconcelos@ambipar.com": {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Rodrigo Pereira Silva Vasconcelos"},
    "cmte.romanato@ambipar.com":  {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Rodrigo Romanato De Castro"},
    "romulo.equey@ambipar.com":   {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Romulo Leonardo Equey Gomes"},
    "cmte.ronaldo@ambipar.com":   {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Ronaldo De Albuquerque Filho"},
    "thiago.cury@ambipar.com":    {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Thiago Falcao Cury"},
    "victor.soares@ambipar.com":  {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Victor Lucas Pereira Soares"},
    "cmte.welner@ambipar.com":    {"senha": "Ambipar2025", "tipo": "aluno", "nome": "Welner Silva Lima"},

    # ---------------------------  ALUNOS  -----------------------------
    

    # -------------------------  PROFESSORES  --------------------------
    "tuany.oliveira@ambipar.com":  {"senha": "Ambipar2025", "tipo": "professor", "nome": "TUANY OLIVEIRA"},
    "leandro.michelin@ambipar.com": {"senha": "Ambipar2025", "tipo": "professor", "nome": "LEANDRO MICHELIN"},
    "carlos.lopes@ambipar.com":     {"senha": "Ambipar2025", "tipo": "professor", "nome": "CARLOS LOPES"},
}

# ----------------------------------------------------------------------
cursos:      list[dict] = []
matriculas:  list[dict] = []
# ----------------------------------------------------------------------


# ======================================================================
#                             ROTAS GERAIS
# ======================================================================
@app.route("/")
def home():
    if "usuario" in session:
        if session["tipo"] == "professor":
            return render_template("professor_home.html", usuario=session["usuario"])

        # Aluno
        email = session["usuario"]
        cursos_aluno = [m["curso"] for m in matriculas if m["aluno"] == email]
        cursos_disp = [c for c in cursos if c["nome"] in cursos_aluno]
        progresso = {}
        vencimentos = {}

        for curso in cursos_disp:
            # Progresso
            prog = curso.get("progresso", {}).get(email)
            progresso[curso["nome"]] = prog if prog else {"tempo": 0, "concluido": False}

            # Data limite da matrícula
            matricula = next((m for m in matriculas if m["aluno"] == email and m["curso"] == curso["nome"]), None)
            curso["data_fim"] = matricula.get("data_fim") if matricula else None
            vencimentos[curso["nome"]] = curso["data_fim"] or "Não Definida"

            # Verifica se certificado está disponível
            resultado = curso.get("resultados", {}).get(email)
            if resultado and resultado.get("acertos", 0) >= 0.7 * resultado.get("total", 1):
                curso["certificado_disponivel"] = True
                # Força conclusão no progresso
                if curso.get("progresso") is None:
                    curso["progresso"] = {}
                if email not in curso["progresso"]:
                    curso["progresso"][email] = {}
                curso["progresso"][email]["concluido"] = True
                progresso[curso["nome"]]["concluido"] = True
            else:
                curso["certificado_disponivel"] = False

        return render_template("home_aluno.html",
                               usuario=usuarios[email]["nome"],
                               cursos=cursos_disp,
                               progresso=progresso,
                               vencimentos=vencimentos)

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
def alterar_senha_professor():
    if session.get("tipo") != "professor":
        return redirect("/login")

    email = session["usuario"]

    if request.method == "POST":
        nova_senha = request.form.get("senha")
        if nova_senha:
            usuarios[email]["senha"] = nova_senha
            salvar_usuarios()
        return redirect("/")

    return render_template("perfil_aluno.html", usuario=usuarios[email])


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
                caminho = os.path.join("static", "conteudos", filename)
                os.makedirs(os.path.dirname(caminho), exist_ok=True)
                arquivo.save(caminho)
                modulos.append({"titulo": titulo, "arquivo": f"conteudos/{filename}"})
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
            "tipo":            request.form["tipo"],
            "modulos":         modulos,
            "instrutor":       request.form.get("instrutor", instrutor_nome),
            "conteudo":        request.form.get("conteudo", ""),
            "data_realizacao": request.form["data_realizacao"],
            "nrt":             request.form["nrt"],
            "prova":           perguntas,
        }

        cursos.append(curso)
        salvar_dados(CAMINHO_CURSOS, cursos)  # Salva o curso novo no disco
        return redirect("/")

    return render_template("cadastrar_curso.html")


@app.route("/matricular", methods=["GET", "POST"])
def matricular():
    if session.get("tipo") != "professor":
        return redirect("/")

    if request.method == "POST":
        aluno_email = request.form["aluno"]
        curso_nome  = request.form["curso"]
        professor   = request.form["professor"]
        data_inicio = request.form.get("data_inicio")
        data_fim    = request.form.get("data_fim")

        # só adiciona se ainda não existe
        if not any(m["aluno"] == aluno_email and m["curso"] == curso_nome for m in matriculas):
            matriculas.append({
                "aluno":      aluno_email,
                "curso":      curso_nome,
                "professor":  professor,
                "data_inicio": data_inicio,
                "data_fim":    data_fim
            })
            salvar_dados(CAMINHO_MATRICULAS, matriculas)

        return redirect("/matricular")

    alunos = [{"email": e, "nome": d["nome"]} for e, d in usuarios.items() if d["tipo"] == "aluno"]
    professores = [ 
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
    ]

    return render_template("matricular.html",
                           alunos=alunos,
                           cursos=cursos,
                           professores=professores)

                  
@app.route("/editar_curso/<nome>", methods=["GET", "POST"])
def editar_curso_nome(nome):
    if session.get("tipo") != "professor":
        return redirect("/login")

    curso = next((c for c in cursos if c["nome"] == nome), None)
    if not curso:
        return "Curso não encontrado", 404

    if request.method == "POST":
        curso["nome"] = request.form["nome"]
        curso["carga_horaria"] = request.form["carga_horaria"]
        curso["tipo"] = request.form["tipo"]
        curso["data_realizacao"] = request.form["data_realizacao"]
        curso["nrt"] = request.form["nrt"]
        curso["conteudo"] = request.form["conteudo"]
        salvar_dados(CAMINHO_CURSOS, cursos)
        return redirect("/editar_curso")

    if 'arquivo' in request.files:
        file = request.files['arquivo']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            caminho = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(caminho)
            curso["arquivo"] = filename
            salvar_dados(CAMINHO_CURSOS, cursos)
            return redirect("/editar_curso")

    alunos_matriculados = [
        usuarios[m["aluno"]]["nome"]
        for m in matriculas
        if m["curso"] == nome and m["aluno"] in usuarios
    ]

    return render_template(
        "editar_curso_form.html",
        curso=curso,
        alunos_matriculados=alunos_matriculados
    )


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

    modulo_atual = int(request.args.get("modulo", 0))
    total_modulos = len(curso_obj["modulos"])

    session["start_time"] = datetime.now().isoformat()
    session["curso_visualizado"] = curso

    if aluno not in progresso_por_aluno:
        progresso_por_aluno[aluno] = {}

    progresso_individual = progresso_por_aluno[aluno].get(curso, [0] * total_modulos)
    progresso_individual[modulo_atual] = 100
    progresso_por_aluno[aluno][curso] = progresso_individual

    # ✅ SALVA o progresso no disco
    salvar_dados(CAMINHO_PROGRESSO, progresso_por_aluno)

    progresso_total = int(sum(progresso_individual) / (100 * total_modulos) * 100)

    return render_template("ver_material.html",
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

    return render_template(
        "visualizar_lista_presenca.html",
        curso=curso_obj,
        nrt=curso_obj.get("nrt", "---"),
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
                           nrt=curso_obj.get("nrt",""),
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

    matricula = next((m for m in matriculas if m["aluno"] == aluno_email and m["curso"] == nome), None)
    presenca_assinada = matricula.get("presenca_assinada", False) if matricula else False

    if request.method == "POST":
        acertos = sum(1 for i, p in enumerate(curso["prova"]) if request.form.get(f"pergunta_{i}") == p["correta"])
        total   = len(curso["prova"])
        aprovado = acertos >= 0.7 * total

        curso.setdefault("resultados", {})[aluno_email] = {"acertos": acertos, "total": total}
        salvar_dados(CAMINHO_CURSOS, cursos)  # ⬅️ Salva os resultados da prova

        return render_template(
            "prova.html",
            curso=curso,
            enumerate=enumerate,
            enviado=True,
            acertos=acertos,
            total=total,
            porcentagem=int(acertos / total * 100),
            aprovado=aprovado,
            presenca_assinada=presenca_assinada
        )

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
    professor_assinante = matricula["professor"] if matricula else curso_obj["instrutor"]

    import pytz
    fuso_sp = pytz.timezone("America/Sao_Paulo")
    agora = datetime.now(fuso_sp)

    data_assinatura_instrutor = agora.strftime("%d/%m/%Y")
    hora_assinatura_instrutor = agora.strftime("%H:%M")
    data_assinatura_aluno     = data_assinatura_instrutor
    hora_assinatura_aluno     = hora_assinatura_instrutor

    carga     = curso_obj.get("carga_horaria", "")
    conteudo  = curso_obj.get("conteudo", "")
    aluno_nome = usuarios[aluno]["nome"]

    # (Opcional) Registrar que o certificado foi emitido
    curso_obj.setdefault("certificados_emitidos", {})[aluno] = {
        "data": data_assinatura_instrutor,
        "hora": hora_assinatura_instrutor,
        "ip": gerar_ip()
    }
    salvar_dados(CAMINHO_CURSOS, cursos)

    return render_template("certificado.html",
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


# ======================================================================
#                       RELATÓRIOS / UTIL
# ======================================================================

@app.route("/acompanhamento")
def acompanhamento():
    if session.get("tipo") != "professor":
        return redirect("/login")

    # monta lista de matrículas detalhadas
    enrollments = []
    for m in matriculas:
        curso_nome = m.get("curso")
        if not curso_nome:
            continue
        curso_obj = next((c for c in cursos if c.get("nome") == curso_nome), None)
        if not curso_obj:
            continue

        prog = curso_obj.get("progresso", {}).get(m["aluno"], {"tempo": "---", "concluido": False})
        res  = curso_obj.get("resultados", {}).get(m["aluno"], {"acertos": 0, "total": 0})
        nota = f"{round((res['acertos']/res['total']*100),1)}%" if res["total"] > 0 else "---"

        enrollments.append({
            "curso":     curso_obj,
            "aluno":     usuarios[m["aluno"]]["nome"],
            "email":     m["aluno"],
            "tempo":     prog["tempo"],
            "concluido": prog["concluido"],
            "nota":      nota
        })

    # salva progresso e resultados no disco para não perder dados
    salvar_dados(CAMINHO_CURSOS, cursos)
    salvar_dados(CAMINHO_MATRICULAS, matriculas)

    return render_template("acompanhamento.html", enrollments=enrollments)



@app.route("/fale_tutor")
def fale_tutor():
    if "usuario" in session:
        return render_template("fale_tutor.html", usuario=session["usuario"])
    return redirect("/login")


# ----------------------------- MAIN -----------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
