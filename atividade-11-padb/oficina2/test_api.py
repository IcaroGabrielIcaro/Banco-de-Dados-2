#!/usr/bin/env python3
"""
CLI para testar a API (Cursos / Modulos / Aulas / Matriculas + Auth)
Opção B: menu por seções.
Salve como api_cli.py e rode: python api_cli.py
"""
import json
import os
import requests
from typing import Dict, Optional, List

# ------------------------
# Config
# ------------------------
BASE_URL = "http://localhost:8000/"  # ajuste se necessário
TIMEOUT = 10  # segundos para requisições

# ------------------------
# Cores para terminal
# ------------------------
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ------------------------
# Utilidades
# ------------------------
def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def pretty_print_json(data):
    try:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception:
        print(data)

# ------------------------
# APITester class
# ------------------------
class APITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.test_data = self.load_test_data()
        # cache simples para ids criados durante execução (útil para testes automáticos)
        self.cache: Dict[str, List[int]] = {
            'cursos': [],
            'modulos': [],
            'aulas': [],
            'matriculas': [],
        }

    def load_test_data(self) -> Dict:
        try:
            with open('test_data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"{Colors.WARNING}Aviso: test_data.json não encontrado. Algumas funcionalidades automáticas ficarão indisponíveis.{Colors.ENDC}")
            return {}

    def headers(self, with_auth: bool = True) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if with_auth and self.access_token:
            h["Authorization"] = f"Bearer {self.access_token}"
        return h

    def print_header(self, text: str):
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

    def print_response(self, resp: requests.Response):
        print(f"\n{Colors.OKBLUE}Status Code: {resp.status_code}{Colors.ENDC}")
        try:
            data = resp.json()
            print(f"{Colors.OKCYAN}Response:{Colors.ENDC}")
            pretty_print_json(data)
        except Exception:
            print(f"{Colors.WARNING}Response (text):{Colors.ENDC}")
            print(resp.text)

    # ------------------------
    # AUTH / USUÁRIO
    # ------------------------
    def registrar_usuario(self, index: Optional[int] = None):
        usuarios = self.test_data.get("usuarios_para_registro", [])
        if not usuarios:
            print(f"{Colors.FAIL}Nenhum usuário no test_data.json.{Colors.ENDC}")
            return

        # escolher
        if index is None:
            print(f"\n{Colors.OKGREEN}Usuários disponíveis para registro:{Colors.ENDC}")
            for i, u in enumerate(usuarios, 1):
                print(f"{i}. {u.get('username')} ({u.get('tipo_perfil', '')})")
            try:
                choice = int(input(f"{Colors.OKCYAN}Escolha um usuário (número): {Colors.ENDC}"))
                index = choice - 1
            except Exception:
                print(f"{Colors.FAIL}Entrada inválida.{Colors.ENDC}")
                return

        if not (0 <= index < len(usuarios)):
            print(f"{Colors.FAIL}Índice inválido.{Colors.ENDC}")
            return

        user_data = usuarios[index]
        try:
            resp = requests.post(f"{self.base_url}auth/registro/", json=user_data, headers=self.headers(False), timeout=TIMEOUT)
            self.print_response(resp)
            if resp.status_code in (200, 201):
                data = resp.json()
                # tenta pegar tokens se seu endpoint retornar
                tokens = data.get('tokens') or data.get('tokens') if isinstance(data, dict) else None
                if isinstance(data, dict):
                    if 'access' in data and 'refresh' in data:
                        self.access_token = data.get('access')
                        self.refresh_token = data.get('refresh')
                        print(f"{Colors.OKGREEN}Tokens salvos.{Colors.ENDC}")
                    elif 'tokens' in data and isinstance(data['tokens'], dict):
                        self.access_token = data['tokens'].get('access')
                        self.refresh_token = data['tokens'].get('refresh')
                        print(f"{Colors.OKGREEN}Tokens salvos (campo tokens).{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}Falha ao registrar usuário.{Colors.ENDC}")
        except requests.exceptions.RequestException as e:
            print(f"{Colors.FAIL}Erro na requisição: {e}{Colors.ENDC}")

    def registrar_todos_usuarios(self):
        usuarios = self.test_data.get("usuarios_para_registro", [])
        if not usuarios:
            print(f"{Colors.FAIL}Nenhum usuário no test_data.json.{Colors.ENDC}")
            return
        print(f"{Colors.OKGREEN}Registrando {len(usuarios)} usuários...{Colors.ENDC}")
        for i, u in enumerate(usuarios):
            print(f"{Colors.OKCYAN}[{i+1}/{len(usuarios)}] Registrando: {u.get('username')}{Colors.ENDC}")
            try:
                resp = requests.post(f"{self.base_url}auth/registro/", json=u, headers=self.headers(False), timeout=TIMEOUT)
                if resp.status_code in (200, 201):
                    print(f"{Colors.OKGREEN}✓ Registrado{Colors.ENDC}")
                    # guardar token do primeiro usuário, se retornado
                    if i == 0:
                        data = resp.json()
                        if isinstance(data, dict):
                            if 'access' in data and 'refresh' in data:
                                self.access_token = data.get('access')
                                self.refresh_token = data.get('refresh')
                else:
                    print(f"{Colors.FAIL}✗ Falha ({resp.status_code}){Colors.ENDC}")
            except requests.exceptions.RequestException as e:
                print(f"{Colors.FAIL}Erro: {e}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Processo finalizado.{Colors.ENDC}")

    def fazer_login(self):
        print(f"\n{Colors.OKGREEN}Login{Colors.ENDC}")
        username = input(f"{Colors.OKCYAN}Username: {Colors.ENDC}").strip()
        password = input(f"{Colors.OKCYAN}Password: {Colors.ENDC}").strip()
        if not username or not password:
            print(f"{Colors.FAIL}Username e password obrigatórios.{Colors.ENDC}")
            return
        try:
            resp = requests.post(f"{self.base_url}auth/login/", json={"username": username, "password": password}, headers=self.headers(False), timeout=TIMEOUT)
            self.print_response(resp)
            if resp.status_code == 200:
                data = resp.json()
                # suporte para respostas comuns: {"access": "...", "refresh": "..."} ou {"tokens": {...}}
                if isinstance(data, dict):
                    if 'access' in data and 'refresh' in data:
                        self.access_token = data.get('access')
                        self.refresh_token = data.get('refresh')
                    elif 'tokens' in data and isinstance(data['tokens'], dict):
                        self.access_token = data['tokens'].get('access')
                        self.refresh_token = data['tokens'].get('refresh')
                print(f"{Colors.OKGREEN}Login realizado. Tokens salvos.{Colors.ENDC}")
        except requests.exceptions.RequestException as e:
            print(f"{Colors.FAIL}Erro na requisição: {e}{Colors.ENDC}")

    def renovar_token(self):
        if not self.refresh_token:
            print(f"{Colors.FAIL}Não há refresh token salvo. Faça login primeiro.{Colors.ENDC}")
            return
        try:
            resp = requests.post(f"{self.base_url}auth/token/refresh/", json={"refresh": self.refresh_token}, headers=self.headers(False), timeout=TIMEOUT)
            self.print_response(resp)
            if resp.status_code == 200:
                data = resp.json()
                self.access_token = data.get('access')
                print(f"{Colors.OKGREEN}Access token renovado.{Colors.ENDC}")
        except requests.exceptions.RequestException as e:
            print(f"{Colors.FAIL}Erro: {e}{Colors.ENDC}")

    def obter_usuario_atual(self):
        if not self.access_token:
            print(f"{Colors.FAIL}Faça login primeiro.{Colors.ENDC}")
            return
        try:
            resp = requests.get(f"{self.base_url}auth/usuario/", headers=self.headers(True), timeout=TIMEOUT)
            self.print_response(resp)
        except requests.exceptions.RequestException as e:
            print(f"{Colors.FAIL}Erro: {e}{Colors.ENDC}")

    def visualizar_tokens(self):
        print(f"\n{Colors.OKGREEN}Tokens:{Colors.ENDC}")
        if self.access_token:
            print(f"{Colors.OKCYAN}Access (preview):{Colors.ENDC} {self.access_token[:40]}...{self.access_token[-20:]}")
        else:
            print(f"{Colors.WARNING}Access: não disponível{Colors.ENDC}")
        if self.refresh_token:
            print(f"{Colors.OKCYAN}Refresh (preview):{Colors.ENDC} {self.refresh_token[:40]}...{self.refresh_token[-20:]}")
        else:
            print(f"{Colors.WARNING}Refresh: não disponível{Colors.ENDC}")

    def limpar_tokens(self):
        self.access_token = None
        self.refresh_token = None
        print(f"{Colors.OKGREEN}Tokens limpos.{Colors.ENDC}")

    # ------------------------
    # CURSOS
    # ------------------------
    def listar_cursos(self):
        try:
            resp = requests.get(f"{self.base_url}api/cursos/", headers=self.headers(True), timeout=TIMEOUT)
            self.print_response(resp)
        except requests.exceptions.RequestException as e:
            print(f"{Colors.FAIL}Erro: {e}{Colors.ENDC}")

    def criar_curso(self):
        if not self.access_token:
            print(f"{Colors.FAIL}Faça login como instrutor para criar cursos.{Colors.ENDC}")
            return
        nome = input("Nome do curso: ").strip()
        descricao = input("Descrição: ").strip()
        payload = {"nome": nome, "descricao": descricao}
        try:
            resp = requests.post(f"{self.base_url}api/cursos/", json=payload, headers=self.headers(True), timeout=TIMEOUT)
            self.print_response(resp)
            if resp.status_code in (200, 201):
                data = resp.json()
                cid = data.get('id')
                if cid:
                    self.cache['cursos'].append(cid)
        except requests.exceptions.RequestException as e:
            print(f"{Colors.FAIL}Erro: {e}{Colors.ENDC}")

    def atualizar_curso(self):
        if not self.access_token:
            print(f"{Colors.FAIL}Faça login primeiro.{Colors.ENDC}")
            return
        try:
            pk = int(input("ID do curso a atualizar: ").strip())
        except Exception:
            print(f"{Colors.FAIL}ID inválido.{Colors.ENDC}")
            return
        nome = input("Novo nome (enter para manter): ").strip()
        descricao = input("Nova descrição (enter para manter): ").strip()
        payload = {}
        if nome:
            payload['nome'] = nome
        if descricao:
            payload['descricao'] = descricao
        if not payload:
            print("Nada a atualizar.")
            return
        try:
            resp = requests.put(f"{self.base_url}api/cursos/{pk}/", json=payload, headers=self.headers(True), timeout=TIMEOUT)
            self.print_response(resp)
        except requests.exceptions.RequestException as e:
            print(f"{Colors.FAIL}Erro: {e}{Colors.ENDC}")

    def apagar_curso(self):
        if not self.access_token:
            print(f"{Colors.FAIL}Faça login primeiro.{Colors.ENDC}")
            return
        try:
            pk = int(input("ID do curso a apagar: ").strip())
        except Exception:
            print(f"{Colors.FAIL}ID inválido.{Colors.ENDC}")
            return
        try:
            resp = requests.delete(f"{self.base_url}api/cursos/{pk}/", headers=self.headers(True), timeout=TIMEOUT)
            if resp.status_code in (200, 204):
                print(f"{Colors.OKGREEN}Curso apagado.{Colors.ENDC}")
            else:
                self.print_response(resp)
        except requests.exceptions.RequestException as e:
            print(f"{Colors.FAIL}Erro: {e}{Colors.ENDC}")

    def listar_modulos_de_curso(self):
        try:
            pk = int(input("ID do curso: ").strip())
        except Exception:
            print(f"{Colors.FAIL}ID inválido.{Colors.ENDC}")
            return
        try:
            resp = requests.get(f"{self.base_url}api/cursos/{pk}/modulos/", headers=self.headers(True), timeout=TIMEOUT)
            self.print_response(resp)
        except requests.exceptions.RequestException as e:
            print(f"{Colors.FAIL}Erro: {e}{Colors.ENDC}")

    # ------------------------
    # MODULOS
    # ------------------------
    def listar_modulos(self):
        try:
            resp = requests.get(f"{self.base_url}api/modulos/", headers=self.headers(True), timeout=TIMEOUT)
            self.print_response(resp)
        except requests.exceptions.RequestException as e:
            print(f"{Colors.FAIL}Erro: {e}{Colors.ENDC}")

    def criar_modulo(self):
        if not self.access_token:
            print(f"{Colors.FAIL}Faça login como instrutor para criar módulos.{Colors.ENDC}")
            return
        try:
            curso_id = int(input("ID do curso (onde criar o módulo): ").strip())
        except Exception:
            print(f"{Colors.FAIL}ID inválido.{Colors.ENDC}")
            return
        titulo = input("Título do módulo: ").strip()
        try:
            ordem = int(input("Ordem (número): ").strip())
        except Exception:
            print(f"{Colors.FAIL}Ordem inválida.{Colors.ENDC}")
            return
        payload = {"curso": curso_id, "titulo": titulo, "ordem": ordem}
        try:
            resp = requests.post(f"{self.base_url}api/modulos/", json=payload, headers=self.headers(True), timeout=TIMEOUT)
            self.print_response(resp)
            if resp.status_code in (200, 201):
                data = resp.json(); mid = data.get('id')
                if mid: self.cache['modulos'].append(mid)
        except requests.exceptions.RequestException as e:
            print(f"{Colors.FAIL}Erro: {e}{Colors.ENDC}")

    def atualizar_modulo(self):
        if not self.access_token:
            print(f"{Colors.FAIL}Faça login primeiro.{Colors.ENDC}")
            return
        try:
            pk = int(input("ID do módulo: ").strip())
        except Exception:
            print(f"{Colors.FAIL}ID inválido.{Colors.ENDC}")
            return
        titulo = input("Novo título (enter para manter): ").strip()
        ordem_input = input("Nova ordem (enter para manter): ").strip()
        payload = {}
        if titulo:
            payload["titulo"] = titulo
        if ordem_input:
            try:
                payload["ordem"] = int(ordem_input)
            except Exception:
                print(f"{Colors.FAIL}Ordem inválida.{Colors.ENDC}")
                return
        if not payload:
            print("Nada a atualizar.")
            return
        try:
            resp = requests.put(f"{self.base_url}api/modulos/{pk}/", json=payload, headers=self.headers(True), timeout=TIMEOUT)
            self.print_response(resp)
        except requests.exceptions.RequestException as e:
            print(f"{Colors.FAIL}Erro: {e}{Colors.ENDC}")

    def apagar_modulo(self):
        if not self.access_token:
            print(f"{Colors.FAIL}Faça login primeiro.{Colors.ENDC}")
            return
        try:
            pk = int(input("ID do módulo: ").strip())
        except Exception:
            print(f"{Colors.FAIL}ID inválido.{Colors.ENDC}")
            return
        try:
            resp = requests.delete(f"{self.base_url}api/modulos/{pk}/", headers=self.headers(True), timeout=TIMEOUT)
            if resp.status_code in (200, 204):
                print(f"{Colors.OKGREEN}Módulo apagado.{Colors.ENDC}")
            else:
                self.print_response(resp)
        except requests.exceptions.RequestException as e:
            print(f"{Colors.FAIL}Erro: {e}{Colors.ENDC}")

    def listar_aulas_de_modulo(self):
        try:
            pk = int(input("ID do módulo: ").strip())
        except Exception:
            print(f"{Colors.FAIL}ID inválido.{Colors.ENDC}")
            return
        try:
            resp = requests.get(f"{self.base_url}api/modulos/{pk}/aulas/", headers=self.headers(True), timeout=TIMEOUT)
            self.print_response(resp)
        except requests.exceptions.RequestException as e:
            print(f"{Colors.FAIL}Erro: {e}{Colors.ENDC}")

    # ------------------------
    # AULAS
    # ------------------------
    def listar_aulas(self):
        try:
            resp = requests.get(f"{self.base_url}api/aulas/", headers=self.headers(True), timeout=TIMEOUT)
            self.print_response(resp)
        except requests.exceptions.RequestException as e:
            print(f"{Colors.FAIL}Erro: {e}{Colors.ENDC}")

    def criar_aula(self):
        if not self.access_token:
            print(f"{Colors.FAIL}Faça login como instrutor para criar aulas.{Colors.ENDC}")
            return
        try:
            modulo_id = int(input("ID do módulo: ").strip())
        except Exception:
            print(f"{Colors.FAIL}ID inválido.{Colors.ENDC}")
            return
        titulo = input("Título da aula: ").strip()
        conteudo = input("Conteúdo (texto): ").strip()
        try:
            duracao = int(input("Duração (minutos): ").strip())
        except Exception:
            print(f"{Colors.FAIL}Duração inválida.{Colors.ENDC}")
            return
        ordem = input("Ordem (enter para padrão 1): ").strip()
        ordem_val = 1
        if ordem:
            try:
                ordem_val = int(ordem)
            except Exception:
                print(f"{Colors.WARNING}Ordem inválida, usando 1.{Colors.ENDC}")
        payload = {"modulo": modulo_id, "titulo": titulo, "conteudo": conteudo, "duracao": duracao, "ordem": ordem_val}
        try:
            resp = requests.post(f"{self.base_url}api/aulas/", json=payload, headers=self.headers(True), timeout=TIMEOUT)
            self.print_response(resp)
            if resp.status_code in (200, 201):
                data = resp.json(); aid = data.get('id')
                if aid: self.cache['aulas'].append(aid)
        except requests.exceptions.RequestException as e:
            print(f"{Colors.FAIL}Erro: {e}{Colors.ENDC}")

    def atualizar_aula(self):
        if not self.access_token:
            print(f"{Colors.FAIL}Faça login primeiro.{Colors.ENDC}")
            return
        try:
            pk = int(input("ID da aula: ").strip())
        except Exception:
            print(f"{Colors.FAIL}ID inválido.{Colors.ENDC}")
            return
        titulo = input("Novo título (enter para manter): ").strip()
        conteudo = input("Novo conteúdo (enter para manter): ").strip()
        duracao_input = input("Nova duração (enter para manter): ").strip()
        ordem_input = input("Nova ordem (enter para manter): ").strip()
        payload = {}
        if titulo: payload['titulo'] = titulo
        if conteudo: payload['conteudo'] = conteudo
        if duracao_input:
            try:
                payload['duracao'] = int(duracao_input)
            except Exception:
                print(f"{Colors.FAIL}Duração inválida.{Colors.ENDC}")
                return
        if ordem_input:
            try:
                payload['ordem'] = int(ordem_input)
            except Exception:
                print(f"{Colors.FAIL}Ordem inválida.{Colors.ENDC}")
                return
        if not payload:
            print("Nada a atualizar.")
            return
        try:
            resp = requests.put(f"{self.base_url}api/aulas/{pk}/", json=payload, headers=self.headers(True), timeout=TIMEOUT)
            self.print_response(resp)
        except requests.exceptions.RequestException as e:
            print(f"{Colors.FAIL}Erro: {e}{Colors.ENDC}")

    def apagar_aula(self):
        if not self.access_token:
            print(f"{Colors.FAIL}Faça login primeiro.{Colors.ENDC}")
            return
        try:
            pk = int(input("ID da aula: ").strip())
        except Exception:
            print(f"{Colors.FAIL}ID inválido.{Colors.ENDC}")
            return
        try:
            resp = requests.delete(f"{self.base_url}api/aulas/{pk}/", headers=self.headers(True), timeout=TIMEOUT)
            if resp.status_code in (200, 204):
                print(f"{Colors.OKGREEN}Aula apagada.{Colors.ENDC}")
            else:
                self.print_response(resp)
        except requests.exceptions.RequestException as e:
            print(f"{Colors.FAIL}Erro: {e}{Colors.ENDC}")

    # ------------------------
    # MATRICULAS
    # ------------------------
    def listar_matriculas(self):
        try:
            resp = requests.get(f"{self.base_url}api/matriculas/", headers=self.headers(True), timeout=TIMEOUT)
            self.print_response(resp)
        except requests.exceptions.RequestException as e:
            print(f"{Colors.FAIL}Erro: {e}{Colors.ENDC}")

    def criar_matricula(self):
        if not self.access_token:
            print(f"{Colors.FAIL}Faça login como aluno para se matricular.{Colors.ENDC}")
            return
        try:
            curso_id = int(input("ID do curso para matricular: ").strip())
        except Exception:
            print(f"{Colors.FAIL}ID inválido.{Colors.ENDC}")
            return
        payload = {"curso": curso_id}
        try:
            resp = requests.post(f"{self.base_url}api/matriculas/", json=payload, headers=self.headers(True), timeout=TIMEOUT)
            self.print_response(resp)
            if resp.status_code in (200, 201):
                data = resp.json(); mid = data.get('id')
                if mid: self.cache['matriculas'].append(mid)
        except requests.exceptions.RequestException as e:
            print(f"{Colors.FAIL}Erro: {e}{Colors.ENDC}")

    def atualizar_matricula(self):
        if not self.access_token:
            print(f"{Colors.FAIL}Faça login primeiro.{Colors.ENDC}")
            return
        try:
            pk = int(input("ID da matrícula: ").strip())
        except Exception:
            print(f"{Colors.FAIL}ID inválido.{Colors.ENDC}")
            return
        # permitir atualização mínima (ex: trocar curso)
        try:
            curso_id_input = input("Novo curso ID (enter para manter): ").strip()
            payload = {}
            if curso_id_input:
                payload['curso'] = int(curso_id_input)
            if not payload:
                print("Nada a atualizar.")
                return
            resp = requests.put(f"{self.base_url}api/matriculas/{pk}/", json=payload, headers=self.headers(True), timeout=TIMEOUT)
            self.print_response(resp)
        except Exception as e:
            print(f"{Colors.FAIL}Erro: {e}{Colors.ENDC}")

    def apagar_matricula(self):
        if not self.access_token:
            print(f"{Colors.FAIL}Faça login primeiro.{Colors.ENDC}")
            return
        try:
            pk = int(input("ID da matrícula: ").strip())
        except Exception:
            print(f"{Colors.FAIL}ID inválido.{Colors.ENDC}")
            return
        try:
            resp = requests.delete(f"{self.base_url}api/matriculas/{pk}/", headers=self.headers(True), timeout=TIMEOUT)
            if resp.status_code in (200, 204):
                print(f"{Colors.OKGREEN}Matrícula apagada.{Colors.ENDC}")
            else:
                self.print_response(resp)
        except requests.exceptions.RequestException as e:
            print(f"{Colors.FAIL}Erro: {e}{Colors.ENDC}")

    # ------------------------
    # Criação automática de exemplo (cria um curso->módulo->aula)
    # ------------------------
    def criar_dados_exemplo(self):
        """
        Cria uma sequência básica de dados:
        1) cria curso (se instrutor)
        2) cria módulo
        3) cria aula
        Útil para popular ambiente rapidamente.
        """
        print(f"{Colors.OKGREEN}Criando dados de exemplo...{Colors.ENDC}")
        # 1) criar curso
        if not self.access_token:
            print(f"{Colors.FAIL}Faça login com um instrutor para criar dados automaticamente.{Colors.ENDC}")
            return
        try:
            curso_payload = {
                "nome": "Curso Exemplo CLI",
                "descricao": "Curso criado automaticamente pelo CLI"
            }
            r1 = requests.post(f"{self.base_url}api/cursos/", json=curso_payload, headers=self.headers(True), timeout=TIMEOUT)
            self.print_response(r1)
            if r1.status_code not in (200,201):
                print(f"{Colors.FAIL}Falha ao criar curso exemplo. Abortando.{Colors.ENDC}")
                return
            curso = r1.json()
            curso_id = curso.get('id')
            if not curso_id:
                print(f"{Colors.FAIL}ID do curso não retornado. Abortando.{Colors.ENDC}")
                return
            self.cache['cursos'].append(curso_id)

            # 2) criar módulo
            modulo_payload = {"curso": curso_id, "titulo": "Módulo Exemplo", "ordem": 1}
            r2 = requests.post(f"{self.base_url}api/modulos/", json=modulo_payload, headers=self.headers(True), timeout=TIMEOUT)
            self.print_response(r2)
            if r2.status_code not in (200,201):
                print(f"{Colors.FAIL}Falha ao criar módulo exemplo.{Colors.ENDC}")
                return
            mod = r2.json(); mod_id = mod.get('id')
            if mod_id:
                self.cache['modulos'].append(mod_id)

            # 3) criar aula
            aula_payload = {"modulo": mod_id, "titulo": "Aula Exemplo", "conteudo": "Conteúdo gerado pelo CLI", "duracao": 15, "ordem": 1}
            r3 = requests.post(f"{self.base_url}api/aulas/", json=aula_payload, headers=self.headers(True), timeout=TIMEOUT)
            self.print_response(r3)
            if r3.status_code in (200,201):
                a = r3.json(); aid = a.get('id')
                if aid: self.cache['aulas'].append(aid)

            print(f"{Colors.OKGREEN}Dados de exemplo criados (IDs salvos em cache).{Colors.ENDC}")
        except requests.exceptions.RequestException as e:
            print(f"{Colors.FAIL}Erro: {e}{Colors.ENDC}")

    # ------------------------
    # Menu principal e execução
    # ------------------------
    def mostrar_menu(self):
        self.print_header("API TESTER - Menu por Seções (Opção B)")
        print(f"{Colors.OKGREEN}AUTENTICAÇÃO{Colors.ENDC}")
        print("  1  - Registrar usuário")
        print("  2  - Registrar todos os usuários (do test_data.json)")
        print("  3  - Login")
        print("  4  - Obter usuário atual")
        print("  5  - Renovar token")
        print("  6  - Visualizar tokens")
        print("  7  - Limpar tokens")
        print("")
        print(f"{Colors.OKGREEN}CURSOS{Colors.ENDC}")
        print("  10 - Listar cursos")
        print("  11 - Criar curso")
        print("  12 - Atualizar curso")
        print("  13 - Apagar curso")
        print("  14 - Listar módulos de um curso")
        print("")
        print(f"{Colors.OKGREEN}MÓDULOS{Colors.ENDC}")
        print("  20 - Listar módulos")
        print("  21 - Criar módulo")
        print("  22 - Atualizar módulo")
        print("  23 - Apagar módulo")
        print("  24 - Listar aulas de um módulo")
        print("")
        print(f"{Colors.OKGREEN}AULAS{Colors.ENDC}")
        print("  30 - Listar aulas")
        print("  31 - Criar aula")
        print("  32 - Atualizar aula")
        print("  33 - Apagar aula")
        print("")
        print(f"{Colors.OKGREEN}MATRÍCULAS{Colors.ENDC}")
        print("  40 - Listar minhas matrículas (requer token)")
        print("  41 - Criar matrícula")
        print("  42 - Atualizar matrícula")
        print("  43 - Apagar matrícula")
        print("")
        print(f"{Colors.OKGREEN}UTILS{Colors.ENDC}")
        print("  50 - Criar dados de exemplo (curso->módulo->aula) [requer instrutor autenticado]")
        print("  51 - Exibir cache de IDs criados")
        print("")
        print(f"{Colors.FAIL}0  - Sair{Colors.ENDC}")
        print("")
        if self.access_token:
            print(f"{Colors.OKGREEN}✓ Autenticado{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}⚠ Não autenticado{Colors.ENDC}")

    def executar_acao(self, opcao: str):
        if opcao == '1':
            self.registrar_usuario()
        elif opcao == '2':
            self.registrar_todos_usuarios()
        elif opcao == '3':
            self.fazer_login()
        elif opcao == '4':
            self.obter_usuario_atual()
        elif opcao == '5':
            self.renovar_token()
        elif opcao == '6':
            self.visualizar_tokens()
        elif opcao == '7':
            self.limpar_tokens()
        elif opcao == '10':
            self.listar_cursos()
        elif opcao == '11':
            self.criar_curso()
        elif opcao == '12':
            self.atualizar_curso()
        elif opcao == '13':
            self.apagar_curso()
        elif opcao == '14':
            self.listar_modulos_de_curso()
        elif opcao == '20':
            self.listar_modulos()
        elif opcao == '21':
            self.criar_modulo()
        elif opcao == '22':
            self.atualizar_modulo()
        elif opcao == '23':
            self.apagar_modulo()
        elif opcao == '24':
            self.listar_aulas_de_modulo()
        elif opcao == '30':
            self.listar_aulas()
        elif opcao == '31':
            self.criar_aula()
        elif opcao == '32':
            self.atualizar_aula()
        elif opcao == '33':
            self.apagar_aula()
        elif opcao == '40':
            self.listar_matriculas()
        elif opcao == '41':
            self.criar_matricula()
        elif opcao == '42':
            self.atualizar_matricula()
        elif opcao == '43':
            self.apagar_matricula()
        elif opcao == '50':
            self.criar_dados_exemplo()
        elif opcao == '51':
            print(json.dumps(self.cache, indent=2))
        else:
            print(f"{Colors.FAIL}Opção não reconhecida.{Colors.ENDC}")

    def run(self):
        while True:
            try:
                clear_screen()
                self.mostrar_menu()
                opcao = input(f"\n{Colors.OKCYAN}Escolha uma opção: {Colors.ENDC}").strip()
                if opcao == '0':
                    print(f"\n{Colors.OKGREEN}Até logo!{Colors.ENDC}\n")
                    break
                self.executar_acao(opcao)
                input(f"\n{Colors.WARNING}Pressione ENTER para continuar...{Colors.ENDC}")
            except KeyboardInterrupt:
                print(f"\n\n{Colors.OKGREEN}Até logo!{Colors.ENDC}\n")
                break
            except Exception as e:
                print(f"{Colors.FAIL}Erro inesperado: {e}{Colors.ENDC}")
                input(f"\n{Colors.WARNING}Pressione ENTER para continuar...{Colors.ENDC}")

# ------------------------
# Main
# ------------------------
def main():
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                 API TESTER - CLI (Opção B)                 ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")

    tester = APITester()
    # opção: verificar se servidor responde à raiz da API
    try:
        resp = requests.get(tester.base_url + "/", timeout=2)
    except requests.exceptions.RequestException:
        print(f"{Colors.WARNING}Servidor não respondeu em {tester.base_url}. Verifique se o Django está rodando.{Colors.ENDC}")
        if input("Deseja continuar mesmo assim? (s/N): ").lower() != 's':
            return
    tester.run()

if __name__ == "__main__":
    main()
