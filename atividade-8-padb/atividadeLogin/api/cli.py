import argparse
import requests
import os
from rich.console import Console
from rich.table import Table

console = Console()

API_BASE_URL = "http://127.0.0.1:8000/api"
TOKEN_FILE = ".token"


def save_token(token):
    with open(TOKEN_FILE, "w") as f:
        f.write(token)


def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    return None


def delete_token():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)


def auth_headers():
    token = load_token()
    if not token:
        console.print("[red]Erro: você precisa estar autenticado. Faça login primeiro.[/red]")
        exit(1)
    return {"Authorization": f"Bearer {token}"}


def handle_response(response):
    """
    Trata respostas HTTP de forma segura e amigável.
    """
    try:
        # Tenta converter resposta para JSON
        data = response.json() if response.content else {}
    except ValueError:
        data = {"detail": response.text.strip()}

    if response.status_code in (200, 201, 204):
        return data or {}

    msg = data.get("detail") or data.get("message") or str(data)

    if response.status_code == 400:
        console.print(f"[red]❌ Erro 400 - Requisição inválida:[/red] {msg}")
    elif response.status_code == 401:
        console.print(f"[red]🔒 Erro 401 - Não autorizado. Faça login novamente.[/red]")
        delete_token()
    elif response.status_code == 403:
        console.print(f"[red]🚫 Erro 403 - Acesso negado: {msg}[/red]")
    elif response.status_code == 404:
        console.print(f"[red]🔎 Erro 404 - Recurso não encontrado.[/red]")
    elif response.status_code >= 500:
        console.print(f"[red]💥 Erro {response.status_code} - Problema no servidor.[/red]")
    else:
        console.print(f"[red]⚠️ Erro inesperado ({response.status_code}):[/red] {msg}")

    exit(1)


def safe_request(method, url, **kwargs):
    """
    Envolve as chamadas HTTP e trata erros de rede e servidor.
    """
    try:
        response = requests.request(method, url, timeout=10, **kwargs)
        return handle_response(response)
    except requests.exceptions.ConnectionError:
        console.print("[red]❌ Não foi possível conectar ao servidor. Verifique se o Django está rodando.[/red]")
        exit(1)
    except requests.exceptions.Timeout:
        console.print("[red]⏱️ Tempo de resposta excedido. Tente novamente.[/red]")
        exit(1)
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Erro inesperado na requisição:[/red] {str(e)}")
        exit(1)



def registrar(args):
    data = {
        "username": args.username,
        "password": args.password,
        "password2": args.password,
        "email": args.email,
    }
    safe_request("POST", f"{API_BASE_URL}/cadastro/", json=data)
    console.print("[green]✅ Usuário registrado com sucesso![/green]")


def login(args):
    data = {"username": args.username, "password": args.password}
    json_data = safe_request("POST", f"{API_BASE_URL}/login/", json=data)
    token = json_data.get("access")

    if token:
        save_token(token)
        console.print("[green]🔓 Login realizado com sucesso![/green]")
    else:
        console.print("[red]Falha ao obter token de acesso.[/red]")


def logout(args):
    delete_token()
    console.print("[green]🚪 Logout realizado com sucesso.[/green]")



def projetos_listar(args):
    projetos = safe_request("GET", f"{API_BASE_URL}/projetos/", headers=auth_headers())

    if not projetos:
        console.print("[yellow]Nenhum projeto encontrado.[/yellow]")
        return

    table = Table(title="📁 Seus Projetos")
    table.add_column("ID", justify="right")
    table.add_column("Nome")
    table.add_column("Status")
    table.add_column("Criado em")

    for p in projetos:
        table.add_row(str(p["id"]), p["nome"], p["status"], p["data_criacao"])
    console.print(table)


def projetos_criar(args):
    data = {"nome": args.nome, "descricao": args.descricao, "status": args.status}
    projeto = safe_request("POST", f"{API_BASE_URL}/projetos/", json=data, headers=auth_headers())
    console.print(f"[green]✅ Projeto criado com sucesso! ID: {projeto['id']}[/green]")


def projetos_ver(args):
    projeto = safe_request("GET", f"{API_BASE_URL}/projetos/{args.id}/", headers=auth_headers())
    console.print(projeto)


def projetos_atualizar(args):
    data = {k: v for k, v in vars(args).items() if k in ["nome", "descricao", "status"] and v}
    safe_request("PUT", f"{API_BASE_URL}/projetos/{args.id}/", json=data, headers=auth_headers())
    console.print(f"[green]✏️ Projeto {args.id} atualizado com sucesso![/green]")


def projetos_deletar(args):
    safe_request("DELETE", f"{API_BASE_URL}/projetos/{args.id}/", headers=auth_headers())
    console.print(f"[green]🗑️ Projeto {args.id} deletado com sucesso![/green]")



def tarefas_listar(args):
    tarefas = safe_request("GET", f"{API_BASE_URL}/projetos/{args.projeto_id}/tarefas/", headers=auth_headers())

    if not tarefas:
        console.print("[yellow]Nenhuma tarefa encontrada para este projeto.[/yellow]")
        return

    table = Table(title=f"📝 Tarefas do Projeto {args.projeto_id}")
    table.add_column("ID", justify="right")
    table.add_column("Título")
    table.add_column("Prioridade")
    table.add_column("Concluída")
    table.add_column("Data Criação")

    for t in tarefas:
        table.add_row(str(t["id"]), t["titulo"], t["prioridade"], str(t["concluida"]), t["data_criacao"])
    console.print(table)


def tarefas_criar(args):
    data = {
        "titulo": args.titulo,
        "descricao": args.descricao,
        "prioridade": args.prioridade,
        "projeto": args.projeto_id,  # ✅ Adicionado
    }
    tarefa = safe_request(
        "POST",
        f"{API_BASE_URL}/projetos/{args.projeto_id}/tarefas/",
        json=data,
        headers=auth_headers()
    )
    console.print(f"[green]✅ Tarefa criada com sucesso! ID: {tarefa['id']}[/green]")


def tarefas_ver(args):
    tarefa = safe_request("GET", f"{API_BASE_URL}/tarefas/{args.id}/", headers=auth_headers())
    console.print(tarefa)


def tarefas_atualizar(args):
    data = {k: v for k, v in vars(args).items() if k in ["titulo", "descricao", "prioridade"] and v}
    safe_request("PUT", f"{API_BASE_URL}/tarefas/{args.id}/", json=data, headers=auth_headers())
    console.print(f"[green]✏️ Tarefa {args.id} atualizada com sucesso![/green]")


def tarefas_concluir(args):
    safe_request("PATCH", f"{API_BASE_URL}/tarefas/{args.id}/concluir/", headers=auth_headers())
    console.print(f"[green]✅ Tarefa {args.id} marcada como concluída![/green]")


def tarefas_deletar(args):
    safe_request("DELETE", f"{API_BASE_URL}/tarefas/{args.id}/", headers=auth_headers())
    console.print(f"[green]🗑️ Tarefa {args.id} deletada com sucesso![/green]")


def main():
    parser = argparse.ArgumentParser(description="Cliente CLI para o sistema de Projetos e Tarefas")
    subparsers = parser.add_subparsers(dest="comando")

    # --- Autenticação ---
    parser_registrar = subparsers.add_parser("registrar")
    parser_registrar.add_argument("--username", required=True)
    parser_registrar.add_argument("--password", required=True)
    parser_registrar.add_argument("--email", required=True)
    parser_registrar.set_defaults(func=registrar)

    parser_login = subparsers.add_parser("login")
    parser_login.add_argument("--username", required=True)
    parser_login.add_argument("--password", required=True)
    parser_login.set_defaults(func=login)

    parser_logout = subparsers.add_parser("logout")
    parser_logout.set_defaults(func=logout)

    # --- Projetos ---
    parser_proj = subparsers.add_parser("projetos")
    proj_sub = parser_proj.add_subparsers(dest="acao")

    p_listar = proj_sub.add_parser("listar")
    p_listar.set_defaults(func=projetos_listar)

    p_criar = proj_sub.add_parser("criar")
    p_criar.add_argument("--nome", required=True)
    p_criar.add_argument("--descricao", required=True)
    p_criar.add_argument("--status", required=True)
    p_criar.set_defaults(func=projetos_criar)

    p_ver = proj_sub.add_parser("ver")
    p_ver.add_argument("--id", required=True, type=int)
    p_ver.set_defaults(func=projetos_ver)

    p_atualizar = proj_sub.add_parser("atualizar")
    p_atualizar.add_argument("--id", required=True, type=int)
    p_atualizar.add_argument("--nome")
    p_atualizar.add_argument("--descricao")
    p_atualizar.add_argument("--status")
    p_atualizar.set_defaults(func=projetos_atualizar)

    p_deletar = proj_sub.add_parser("deletar")
    p_deletar.add_argument("--id", required=True, type=int)
    p_deletar.set_defaults(func=projetos_deletar)

    # --- Tarefas ---
    parser_tarefa = subparsers.add_parser("tarefas")
    tarefa_sub = parser_tarefa.add_subparsers(dest="acao")

    t_listar = tarefa_sub.add_parser("listar")
    t_listar.add_argument("--projeto_id", required=True, type=int)
    t_listar.set_defaults(func=tarefas_listar)

    t_criar = tarefa_sub.add_parser("criar")
    t_criar.add_argument("--projeto_id", required=True, type=int)
    t_criar.add_argument("--titulo", required=True)
    t_criar.add_argument("--descricao", required=True)
    t_criar.add_argument("--prioridade", required=True)
    t_criar.set_defaults(func=tarefas_criar)

    t_ver = tarefa_sub.add_parser("ver")
    t_ver.add_argument("--id", required=True, type=int)
    t_ver.set_defaults(func=tarefas_ver)

    t_atualizar = tarefa_sub.add_parser("atualizar")
    t_atualizar.add_argument("--id", required=True, type=int)
    t_atualizar.add_argument("--titulo")
    t_atualizar.add_argument("--descricao")
    t_atualizar.add_argument("--prioridade")
    t_atualizar.set_defaults(func=tarefas_atualizar)

    t_concluir = tarefa_sub.add_parser("concluir")
    t_concluir.add_argument("--id", required=True, type=int)
    t_concluir.set_defaults(func=tarefas_concluir)

    t_deletar = tarefa_sub.add_parser("deletar")
    t_deletar.add_argument("--id", required=True, type=int)
    t_deletar.set_defaults(func=tarefas_deletar)

    # --- Executar comando ---
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
