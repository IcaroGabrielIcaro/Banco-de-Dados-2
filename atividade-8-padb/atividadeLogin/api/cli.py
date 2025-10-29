import requests
import sys

BASE_URL = 'http://localhost:8000/api/'
TOKEN = None


def signup(username, email, password):
    data = {'username': username, 'email': email, 'password': password}
    r = requests.post(BASE_URL + 'signup/', json=data)
    if r.status_code == 201:
        print("Usuário cadastrado com sucesso!")
        print("Access Token:", r.json().get('access'))
        return r.json()
    else:
        print("Erro ao cadastrar:", r.text)


def login(username, password):
    global TOKEN
    data = {'username': username, 'password': password}
    r = requests.post(BASE_URL + 'login/', json=data)
    if r.status_code == 200:
        TOKEN = r.json().get('access')
        print("Login bem-sucedido!")
        print("Token salvo na sessão.")
    else:
        print("Erro ao logar:", r.text)


def get_headers():
    global TOKEN
    if not TOKEN:
        print("Você precisa estar logado.")
        sys.exit(1)
    return {'Authorization': f'Bearer {TOKEN}'}


def listar_projetos():
    r = requests.get(BASE_URL + 'projetos/', headers=get_headers())
    if r.status_code == 200:
        projetos = r.json()
        for p in projetos:
            print(f"[{p['id']}] {p['nome']} - {p['descricao']}")
    else:
        print("Erro:", r.text)


def criar_projeto(nome, descricao):
    data = {'nome': nome, 'descricao': descricao}
    r = requests.post(BASE_URL + 'projetos/', json=data, headers=get_headers())
    if r.status_code == 201:
        print("Projeto criado com sucesso!")
    else:
        print("Erro:", r.text)


def atualizar_projeto(id, nome=None, descricao=None):
    data = {}
    if nome:
        data['nome'] = nome
    if descricao:
        data['descricao'] = descricao

    r = requests.put(BASE_URL + f'projetos/{id}/', json=data, headers=get_headers())
    if r.status_code in (200, 202):
        print("Projeto atualizado!")
    else:
        print("Erro:", r.text)


def deletar_projeto(id):
    r = requests.delete(BASE_URL + f'projetos/{id}/', headers=get_headers())
    if r.status_code == 204:
        print("Projeto deletado com sucesso!")
    else:
        print("Erro:", r.text)


def listar_tarefas(projeto_id):
    r = requests.get(BASE_URL + f'projetos/{projeto_id}/tarefas/', headers=get_headers())
    if r.status_code == 200:
        tarefas = r.json()
        for t in tarefas:
            print(f"[{t['id']}] {t['titulo']} - {'✅' if t['concluida'] else '❌'}")
    else:
        print("Erro:", r.text)


def criar_tarefa(projeto_id, titulo, descricao):
    data = {'titulo': titulo, 'descricao': descricao, 'projeto': projeto_id}
    r = requests.post(BASE_URL + 'tarefas/', json=data, headers=get_headers())
    if r.status_code == 201:
        print("Tarefa criada com sucesso!")
    else:
        print("Erro:", r.text)


def atualizar_tarefa(id, titulo=None, descricao=None, concluida=None):
    data = {}
    if titulo:
        data['titulo'] = titulo
    if descricao:
        data['descricao'] = descricao
    if concluida is not None:
        data['concluida'] = concluida

    r = requests.put(BASE_URL + f'tarefas/{id}/', json=data, headers=get_headers())
    if r.status_code in (200, 202):
        print("Tarefa atualizada!")
    else:
        print("Erro:", r.text)


def deletar_tarefa(id):
    r = requests.delete(BASE_URL + f'tarefas/{id}/', headers=get_headers())
    if r.status_code == 204:
        print("Tarefa deletada!")
    else:
        print("Erro:", r.text)


def menu():
    print("\n=== CLI Django API ===")
    print("1 - Cadastrar usuário")
    print("2 - Login")
    print("3 - Listar projetos")
    print("4 - Criar projeto")
    print("5 - Atualizar projeto")
    print("6 - Deletar projeto")
    print("7 - Listar tarefas")
    print("8 - Criar tarefa")
    print("9 - Atualizar tarefa")
    print("10 - Deletar tarefa")
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
        atualizar_projeto(input("ID: "), input("Novo nome: "), input("Nova descrição: "))
    elif opcao == '6':
        deletar_projeto(input("ID: "))
    elif opcao == '7':
        listar_tarefas(input("ID do projeto: "))
    elif opcao == '8':
        criar_tarefa(input("Projeto ID: "), input("Título: "), input("Descrição: "))
    elif opcao == '9':
        atualizar_tarefa(input("ID: "), input("Novo título: "), input("Nova descrição: "), input("Concluída? (True/False): ") == "True")
    elif opcao == '10':
        deletar_tarefa(input("ID: "))
    elif opcao == '0':
        print("Saindo...")
        sys.exit(0)
    else:
        print("Opção inválida!")

    menu()


if __name__ == '__main__':
    menu()
