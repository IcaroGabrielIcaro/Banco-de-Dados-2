import requests
import sys

BASE_URL = 'http://localhost:8000/api/'
TOKEN = None


def signup(username, email, password):
    data = {
        'username': username,
        'email': email,
        'password': password,
        'password2': password
    }

    r = requests.post(BASE_URL + 'cadastro/', json=data)
    if r.status_code == 201:
        print("✅ Usuário cadastrado com sucesso!")
        print("Agora faça login para obter o token.")
    else:
        print("❌ Erro ao cadastrar usuário:")
        print(r.status_code, r.text)


def login(username, password):
    global TOKEN
    data = {
        'username': username,
        'password': password
    }

    r = requests.post(BASE_URL + 'login/', json=data)
    if r.status_code == 200:
        TOKEN = r.json().get('access')
        print("✅ Login bem-sucedido!")
        print("🔑 Token salvo:", TOKEN[:30] + "...")
    else:
        print("❌ Erro ao logar:")
        print(r.status_code, r.text)


def get_headers():
    global TOKEN
    if not TOKEN:
        print("⚠️  Você precisa estar logado para essa operação.")
        sys.exit(1)
    return {'Authorization': f'Bearer {TOKEN}'}


def listar_projetos():
    r = requests.get(BASE_URL + 'projetos/', headers=get_headers())
    if r.status_code == 200:
        projetos = r.json()
        if not projetos:
            print("📭 Nenhum projeto encontrado.")
        else:
            print("\n📂 Seus Projetos:")
            for p in projetos:
                print(f"  [{p['id']}] {p['nome']} - {p.get('descricao', '')}")
    else:
        print("❌ Erro:", r.status_code, r.text)


def criar_projeto(nome, descricao):
    data = {'nome': nome, 'descricao': descricao}
    r = requests.post(BASE_URL + 'projetos/', json=data, headers=get_headers())

    if r.status_code == 201:
        print("✅ Projeto criado com sucesso!")
    else:
        print("❌ Erro ao criar projeto:")
        print(r.status_code, r.text)


def listar_tarefas(projeto_id):
    r = requests.get(BASE_URL + f'tarefas/?projeto_id={projeto_id}', headers=get_headers())
    if r.status_code == 200:
        tarefas = r.json()
        if not tarefas:
            print("📭 Nenhuma tarefa encontrada para este projeto.")
        else:
            print(f"\n📋 Tarefas do projeto {projeto_id}:")
            for t in tarefas:
                status = "✅" if t['concluida'] else "❌"
                print(f"  [{t['id']}] {t['titulo']} - {status}")
    else:
        print("❌ Erro ao listar tarefas:", r.status_code, r.text)


def criar_tarefa(projeto_id, titulo, descricao):
    data = {'titulo': titulo, 'descricao': descricao, 'projeto': projeto_id}
    r = requests.post(BASE_URL + 'tarefas/', json=data, headers=get_headers())
    if r.status_code == 201:
        print("✅ Tarefa criada com sucesso!")
    else:
        print("❌ Erro ao criar tarefa:")
        print(r.status_code, r.text)


def menu():
    print("\n=== CLI Django API ===")
    print("1 - Cadastrar usuário")
    print("2 - Login")
    print("3 - Listar projetos")
    print("4 - Criar projeto")
    print("5 - Listar tarefas")
    print("6 - Criar tarefa")
    print("0 - Sair")

    opcao = input("Escolha: ")

    if opcao == '1':
        signup(input("Username: "), input("Email: "), input("Senha: "))
    elif opcao == '2':
        login(input("Username: "), input("Senha: "))
    elif opcao == '3':
        listar_projetos()
    elif opcao == '4':
        criar_projeto(input("Nome: "), input("Descrição: "))
    elif opcao == '5':
        listar_tarefas(input("ID do projeto: "))
    elif opcao == '6':
        criar_tarefa(input("Projeto ID: "), input("Título: "), input("Descrição: "))
    elif opcao == '0':
        print("Saindo...")
        sys.exit(0)
    else:
        print("Opção inválida!")

    menu()


if __name__ == '__main__':
    menu()
