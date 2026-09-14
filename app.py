import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 1. Inicialização da Aplicação Flask
app = Flask(__name__)

# 2. Configuração do Banco de Dados MySQL
# Formato da URL: mysql+pymysql://USUARIO:SENHA@HOST:PORTA/NOME_DO_BANCO
# Usamos 'os.environ.get' para pegar a credencial da nuvem no deploy, usando local como fallback.
DB_URL = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:suasenha@localhost/consultorio')
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 3. Inicialização do SQLAlchemy
db = SQLAlchemy(app)

# 4. Definição das Tabelas (Modelos ORM)
class Paciente(db.Model):
    __tablename__ = 'pacientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    nascimento = db.Column(db.Date, nullable=False)
    telefone = db.Column(db.String(20))
    convenio = db.Column(db.String(50))
    observacoes = db.Column(db.Text)
    
    # Relacionamento: Permite acessar paciente.consultas facilmente
    consultas = db.relationship('Consulta', backref='paciente', lazy=True)

class Consulta(db.Model):
    __tablename__ = 'consultas'
    
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    motivo = db.Column(db.String(200))
    status = db.Column(db.String(20), default='Pendente')

# 5. Rotas do Sistema

@app.route('/')
def index():
    # Busca todas as linhas das tabelas no MySQL
    pacientes = Paciente.query.all()
    consultas = Consulta.query.all()
    # Injeta os dados buscados dentro do arquivo HTML
    return render_template('index.html', pacientes=pacientes, consultas=consultas)

@app.route('/pacientes/novo', methods=['POST'])
def novo_paciente():
    # Captura os dados enviados pelo <form> HTML através do atributo "name" de cada input
    nome = request.form['nome']
    nascimento = request.form['nascimento']
    telefone = request.form['telefone']
    convenio = request.form['convenio']
    observacoes = request.form['observacoes']

    # Converte a String de data "YYYY-MM-DD" enviada pelo HTML em um objeto Date do Python
    data_convertida = datetime.strptime(nascimento, '%Y-%m-%d').date()

    # Instancia o novo registro
    novo = Paciente(
        nome=nome,
        nascimento=data_convertida,
        telefone=telefone,
        convenio=convenio,
        observacoes=observacoes
    )
    
    # Grava no Banco de Dados
    db.session.add(novo)
    db.session.commit()
    
    # Redireciona de volta para a página principal para atualizar a listagem
    return redirect(url_for('index'))

@app.route('/consultas/novo', methods=['POST'])
def nova_consulta():
    paciente_id = request.form['paciente_id']
    data = request.form['data']
    hora = request.form['hora']
    motivo = request.form['motivo']

    data_convertida = datetime.strptime(data, '%Y-%m-%d').date()
    hora_convertida = datetime.strptime(hora, '%H:%M').time()

    nova = Consulta(
        paciente_id=paciente_id,
        data=data_convertida,
        hora=hora_convertida,
        motivo=motivo
    )
    
    db.session.add(nova)
    db.session.commit()
    
    return redirect(url_for('index'))

# 6. Criação automática das tabelas e execução em modo de desenvolvimento
if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Lê as classes Paciente e Consulta e cria as tabelas no MySQL se não existirem
    app.run(debug=True)