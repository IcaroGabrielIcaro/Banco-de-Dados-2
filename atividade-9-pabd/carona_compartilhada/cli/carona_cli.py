import requests
import json
from datetime import datetime
from typing import Optional, Dict, List
import os

TOKEN_FILE = ".token"

class CaronaCLI:
    """CLI para interagir com a API de Carona Compartilhada"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api"):
        self.base_url = base_url
        self.session = requests.Session()

    def save_token(self, token: str):
        with open(TOKEN_FILE, "w") as f:
            f.write(token)

    def load_token(self):
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "r") as f:
                return f.read().strip()
        return None

    def delete_token(self):
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)

    def auth_headers(self):
        token = self.load_token()
        if not token:
            print("❌ Você precisa estar autenticado. Faça login primeiro.")
            exit(1)
        return {"Authorization": f"Bearer {token}"}
    
    def handle_response(self, response):
        try:
            data = response.json() if response.content else {}
        except ValueError:
            data = {"detail": response.text.strip()}

        if response.status_code in (200, 201, 204):
            return data or {}

        msg = data.get("detail") or data.get("message") or str(data)

        if response.status_code == 400:
            print(f"❌ Erro 400 - Requisição inválida: {msg}")
        elif response.status_code == 401:
            print("🔒 Erro 401 - Não autorizado. Faça login novamente.")
            self.delete_token()
        elif response.status_code == 403:
            print(f"🚫 Erro 403 - Acesso negado: {msg}")
        elif response.status_code == 404:
            print("🔎 Erro 404 - Recurso não encontrado.")
        elif response.status_code >= 500:
            print(f"💥 Erro {response.status_code} - Problema no servidor.")
        else:
            print(f"⚠️ Erro inesperado ({response.status_code}): {msg}")

        exit(1)

    def safe_request(self, method, url, **kwargs):
        try:
            response = self.session.request(method, url, timeout=10, **kwargs)
            return self.handle_response(response)
        except requests.exceptions.ConnectionError:
            print("❌ Não foi possível conectar ao servidor Django.")
            exit(1)
        except requests.exceptions.Timeout:
            print("⏱️ Tempo de resposta excedido. Tente novamente.")
            exit(1)
        except requests.exceptions.RequestException as e:
            print(f"Erro inesperado na requisição: {str(e)}")
            exit(1)

    def registrar(self, username, email, password):
        data = {
            "username": username,
            "email": email,
            "password": password,
            "password2": password,
        }
        self.safe_request("POST", f"{self.base_url}/cadastro/", json=data)
        print("✅ Usuário registrado com sucesso! Faça login para continuar.")

    def login(self, username, password):
        data = {"username": username, "password": password}
        json_data = self.safe_request("POST", f"{self.base_url}/login/", json=data)
        token = json_data.get("access")

        if token:
            self.save_token(token)
            print("🔓 Login realizado com sucesso!")
        else:
            print("❌ Falha ao obter token de acesso.")

    def logout(self):
        self.delete_token()
        print("🚪 Logout realizado com sucesso.")
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Faz requisição HTTP para a API"""
        url = f"{self.base_url}/{endpoint}"
        try:
            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, json=data)
            elif method == "PUT":
                response = self.session.put(url, json=data)
            elif method == "DELETE":
                response = self.session.delete(url)
            
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {e}")
            return {}
    
    def listar_caronas(self):
        """Lista todas as caronas disponíveis"""
        print("\nCARONAS DISPONÍVEIS")
        print("=" * 80)
        
        caronas = self._make_request("GET", "caronas/disponiveis/")
        
        if not caronas:
            print("Nenhuma carona disponível no momento.")
            return
        
        for carona in caronas:
            print(f"\nID: {carona['id']}")
            print(f"   Origem: {carona['origem']} → Destino: {carona['destino']}")
            print(f"   Motorista: {carona['motorista_nome']}")
            print(f"   Data/Hora: {carona['data_hora_saida']}")
            print(f"   Vagas: {carona['vagas_disponiveis']}")
            print(f"   Preço: R$ {carona['preco_por_pessoa']}")
            if carona['observacoes']:
                print(f"   Obs: {carona['observacoes']}")
    
    def criar_carona(self):
        """Cria uma nova carona"""
        print("\nCRIAR NOVA CARONA")
        print("=" * 80)
        
        try:
            motorista_id = int(input("ID do motorista: "))
            veiculo_id = int(input("ID do veículo: "))
            origem = input("Origem: ")
            destino = input("Destino: ")
            data_hora = input("Data/Hora de saída (YYYY-MM-DD HH:MM): ")
            vagas = int(input("Vagas disponíveis: "))
            preco = float(input("Preço por pessoa: "))
            observacoes = input("Observações (opcional): ")
            
            data = {
                "motorista": motorista_id,
                "veiculo": veiculo_id,
                "origem": origem,
                "destino": destino,
                "data_hora_saida": data_hora,
                "vagas_disponiveis": vagas,
                "preco_por_pessoa": preco,
                "observacoes": observacoes,
                "status": "DISPONIVEL"
            }
            
            resultado = self._make_request("POST", "caronas/", data)
            
            if resultado:
                print(f"\nCarona criada com sucesso! ID: {resultado.get('id')}")
            else:
                print("\nErro ao criar carona.")
                
        except ValueError:
            print("Erro: Valores inválidos inseridos.")
    
    def solicitar_carona(self):
        """Solicita participação em uma carona"""
        print("\nSOLICITAR CARONA")
        print("=" * 80)
        
        try:
            carona_id = int(input("ID da carona: "))
            passageiro_id = int(input("ID do passageiro: "))
            num_lugares = int(input("Número de lugares solicitados: "))
            
            data = {
                "carona": carona_id,
                "passageiro": passageiro_id,
                "num_lugares": num_lugares,
                "status": "PENDENTE"
            }
            
            resultado = self._make_request("POST", "solicitacoes/", data)
            
            if resultado:
                print(f"\nSolicitação enviada com sucesso! ID: {resultado.get('id')}")
            else:
                print("\nErro ao solicitar carona.")
                
        except ValueError:
            print("Erro: Valores inválidos inseridos.")
    
    def listar_solicitacoes(self):
        """Lista todas as solicitações"""
        print("\nSOLICITAÇÕES")
        print("=" * 80)
        
        solicitacoes = self._make_request("GET", "solicitacoes/")
        
        if not solicitacoes.get('results'):
            print("Nenhuma solicitação encontrada.")
            return
        
        for sol in solicitacoes['results']:
            print(f"\n🎫 ID: {sol['id']}")
            print(f"   Carona: {sol['carona_info']}")
            print(f"   Passageiro: {sol['passageiro_nome']}")
            print(f"   Lugares: {sol['num_lugares']}")
            print(f"   Status: {sol['status']}")
            print(f"   Data: {sol['data_solicitacao']}")
    
    def gerenciar_solicitacao(self):
        """Aceitar ou recusar solicitação"""
        print("\nGERENCIAR SOLICITAÇÃO")
        print("=" * 80)
        
        try:
            sol_id = int(input("ID da solicitação: "))
            acao = input("Ação (aceitar/recusar): ").lower()
            
            if acao not in ['aceitar', 'recusar']:
                print("Ação inválida!")
                return
            
            resultado = self._make_request("POST", f"solicitacoes/{sol_id}/{acao}/")
            
            if resultado:
                print(f"\nSolicitação {acao}a com sucesso!")
            else:
                print(f"\n Erro ao {acao} solicitação.")
                
        except ValueError:
            print("Erro: Valores inválidos inseridos.")
    
    def criar_veiculo(self):
        """Cadastra um novo veículo"""
        print("\nCADASTRAR VEÍCULO")
        print("=" * 80)
        
        try:
            motorista_id = int(input("ID do motorista: "))
            modelo = input("Modelo: ")
            marca = input("Marca: ")
            cor = input("Cor: ")
            ano = int(input("Ano: "))
            placa = input("Placa: ")
            num_lugares = int(input("Número de lugares: "))
            
            data = {
                "motorista": motorista_id,
                "modelo": modelo,
                "marca": marca,
                "cor": cor,
                "ano": ano,
                "placa": placa,
                "num_lugares": num_lugares,
                "ativo": True
            }
            
            resultado = self._make_request("POST", "veiculos/", data)
            
            if resultado:
                print(f"\nVeículo cadastrado com sucesso! ID: {resultado.get('id')}")
            else:
                print("\n Erro ao cadastrar veículo.")
                
        except ValueError:
            print(" Erro: Valores inválidos inseridos.")
    
    def menu_principal(self):
        """Menu principal do CLI"""
        while True:
            print("\n" + "=" * 80)
            print("SISTEMA DE CARONA COMPARTILHADA - CLI")
            print("=" * 80)
            print("1. Registrar-se")
            print("2. Entrar no sistema")
            print("3. Sair do sistema")
            print("4. Listar caronas disponíveis")
            print("5. Criar nova carona")
            print("6. Solicitar carona")
            print("7. Listar solicitações")
            print("8. Gerenciar solicitação (aceitar/recusar)")
            print("9. Cadastrar veículo")
            print("0. Sair")
            print("=" * 80)
            
            opcao = input("\nEscolha uma opção: ")
            
            if opcao == "1":
                self.registrar(input("Username: "), input("Email: "), input("Senha: "))
            elif opcao == "2":
                self.login(input("Username: "), input("Senha: "))
            elif opcao == "3":
                self.logout()
            elif opcao == "4":
                self.listar_caronas()
            elif opcao == "5":
                self.criar_carona()
            elif opcao == "6":
                self.solicitar_carona()
            elif opcao == "7":
                self.listar_solicitacoes()
            elif opcao == "8":
                self.gerenciar_solicitacao()
            elif opcao == "9":
                self.criar_veiculo()
            elif opcao == "0":
                print("\n FIM!")
                break
            else:
                print("\n Opção inválida!")
            
            input("\nPressione ENTER para continuar...")


def main():
    """Função principal"""
    cli = CaronaCLI()
    cli.menu_principal()


if __name__ == "__main__":
    main()