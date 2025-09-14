import os
import sys
from typing import Optional
import psycopg2
from psycopg2 import sql
from tabulate import tabulate

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'postgres',
    'password': 'postgres',
    'database': 'postgres'
}

class SistemaVendasCLI:
    def __init__(self):
        self.conexao = None
        print("Sistema de Vendas - CLI Inicializado")
        print("=" * 50)
    
    def conectar_banco(self):
        try:
            self.conexao = psycopg2.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database']
            )
            
            print("Conectando ao banco PostgreSQL...")
            #self.conexao = psycopg2.connect(**pg_config)
            self.conexao.autocommit = True
            print("Conexão estabelecida com sucesso!")
            return True
        except psycopg2.Error as e:
            print(f"Erro ao conectar ao PostgreSQL: {e}")
            return False
        except Exception as e:
            print(f"Erro inesperado: {e}")
            return False
        return True
    
    def desconectar_banco(self):
        if self.conexao:
            self.conexao.close()
            print("Conexão com o banco de dados encerrada.")

    def executar_query(self, sql: str) -> tuple[list[str], list[tuple]]:
        with self.conexao.cursor() as cursor:
            cursor.execute(sql)
            if cursor.description:
                colunas = [desc[0] for desc in cursor.description]
                linhas = cursor.fetchall()
                return colunas, linhas
            return [], []
        
    def exibir_resultado(self, colunas: list[str], linhas: list[tuple], descricao: str = "") -> None:
        if linhas:
            tabela = tabulate(linhas, headers=colunas, tablefmt="fancy_grid", showindex=False)
            largura_tabela = len(tabela.splitlines()[0])
            print(descricao.center(largura_tabela))
            print(tabela)
        else:
            print(descricao.center(50))
            print("consulta realizada com sucesso, mas sem retorno")
                        
    def executar_consulta(self, sql: str, descricao: str) -> None:
        coluna, linha = self.executar_query(sql)
        self.exibir_resultado(coluna, linha, descricao)
    
    # ========================================
    # FUNCOES COM CONSULTAS SQL
    # ========================================
    
    def consulta_01_usuarios_ativos(self):
        """1. Listagem de Usuários Ativos"""
        sql = """
        SELECT id_usuario, nome, email, telefone
        FROM usuario
        WHERE ativo = TRUE;
        """
        self.executar_consulta(sql, "1. Listagem de Usuários Ativos")
    
    def consulta_02_produtos_categoria(self):
        """2. Listagem de Produtos da Categoria Informática"""
        sql = """
        SELECT nome, preco, quantidade_estoque
        FROM produto
        WHERE categoria = 'Informática'
        ORDER BY preco ASC;
        """
        self.executar_consulta(sql, "2. Listagem de Produtos da Categoria Informática")
    
    def consulta_03_pedidos_status(self):
        """3. Quantidade de Pedidos para cada Status Diferente"""
        sql = """
        SELECT status_pedido, COUNT(*) AS quantidade_pedidos
        FROM pedido
        GROUP BY status_pedido;
        """
        self.executar_consulta(sql, "3. Quantidade de Pedidos para cada Status Diferente")
    
    def consulta_04_estoque_baixo(self):
        """4. Listagem de Produtos com Quantidade em Estoque Menor que 30 Unidades"""
        sql = """
        SELECT nome, quantidade_estoque, categoria
        FROM produto
        WHERE quantidade_estoque < 30;
        """
        self.executar_consulta(sql, "4. Listagem de Produtos com Quantidade em Estoque Menor que 30 Unidades")
    
    def consulta_05_pedidos_recentes(self):    
        """5. Listagem de Pedidos Realizados nos Últimos 60 Dias"""
        sql = """
        SELECT id_pedido, TO_CHAR(data_pedido, 'DD-MM-YYYY') AS data_pedido, valor_total, status_pedido
        FROM pedido
        WHERE data_pedido >= CURRENT_DATE - INTERVAL '60 day';
        """
        self.executar_consulta(sql, "5. Listagem de Pedidos Realizados nos Últimos 60 Dias")
    
    def consulta_06_produtos_caros_categoria(self):
        """6. Listagem de Produto Mais Caro da Categoria"""

        """
        O PARTITION BY vai criar novas tabelinhas com base na categoria
        cada uma dessas tabelinhas vai ser ordenada (ORDER BY) pelo preco, deixando o mais caro no topo
        o ROW_NUMBER() OVER vai colocar especies de ranks, que vão ser chamados de posicao
        com o WHERE posicao = 1, a gente pega os primeiros ranks
        
        como so tem 1 primeiro rank por categoria, e os primeiros ranks sao os mais caros
        ele seleciona o mais caro de cada categoria"""

        sql = """
        SELECT nome, preco
        FROM (
            SELECT *,
                ROW_NUMBER() OVER (PARTITION BY categoria ORDER BY preco DESC) AS posicao
            FROM produto
        ) sub
        WHERE posicao = 1;
        """
        self.executar_consulta(sql, "6. Listagem de Produto Mais Caro da Categoria")
    
    def consulta_07_contatos_incompletos(self):
        """7. Listagem de Usuários Ativos que não Possuem Telefone Cadastrado"""
        sql = """
        SELECT *
        FROM usuario
        WHERE telefone IS NULL;
        """
        self.executar_consulta(sql, "7. Listagem de Usuários Ativos que não Possuem Telefone Cadastrado")
    
    def consulta_08_pedidos_enviados(self):
        """8. Listagem de Pedidos com Status 'Enviado'"""
        sql = """
        SELECT 
            u.nome AS nome_usuario,
            u.email AS email_usuario,
            u.telefone AS telefone_usuario,
            p.endereco_entrega
        FROM pedido p
        JOIN usuario u ON p.id_usuario = u.id_usuario
        WHERE p.status_pedido = 'enviado';
        """
        self.executar_consulta(sql, "8. Listagem de Pedidos com Status 'Enviado'")
    
    def consulta_09_detalhamento_pedido(self):
        """9. Listagem de Todas as Informações de um Pedido"""
        sql = """
        SELECT
            u.nome AS nome_cliente,
            u.email AS email_cliente,
            u.telefone AS telefone_cliente,
            pr.nome AS produto_comprado,
            ip.quantidade,
            ip.preco_unitario,
            ip.subtotal
        FROM pedido p
        JOIN usuario u ON p.id_usuario = u.id_usuario
        JOIN itens_pedido ip ON ip.id_pedido = p.id_pedido
        JOIN produto pr ON ip.id_produto = pr.id_produto;
        """
        self.executar_consulta(sql, "9. Listagem de Todas as Informações de um Pedido")
    
    def consulta_10_ranking_produtos(self):
        """10. Listagem de Produtos Ordenado pela Quantidade Total Vendida"""
        sql = """
        SELECT p.nome, p.categoria, SUM(ip.quantidade) AS total_vendido
        FROM produto p
        JOIN itens_pedido ip ON ip.id_produto = p.id_produto
        GROUP BY p.nome, p.categoria
        ORDER BY total_vendido DESC;
        """
        self.executar_consulta(sql, "10. Listagem de Produtos Ordenado pela Quantidade Total Vendida")
    
    def consulta_11_clientes_sem_compras(self):
        """11. Listagem de Usuários Ativos que Nunca Fizeram um Pedido no Sistema"""
        sql = """
        SELECT u.id_usuario, u.nome, u.email, u.telefone
        FROM usuario u
        JOIN pedido p ON p.id_usuario = u.id_usuario
        WHERE u.ativo = TRUE
        GROUP BY u.id_usuario, u.nome, u.email, u.telefone
        HAVING COUNT(p.id_pedido) = 0;
        """
        self.executar_consulta(sql, "11. Listagem de Usuários Ativos que Nunca Fizeram um Pedido no Sistema")
    
    def consulta_12_estatisticas_cliente(self):
        """12. Listagem de Número Total de Pedidos, Valor Médio por Pedido e Valor Total Gasto"""
        sql = """
        SELECT u.nome, 
            COUNT(p.id_pedido) AS quantidade_pedidos, 
            AVG(p.valor_total) AS valor_medio_por_pedido,
            SUM(p.valor_total) AS valor_total_gasto
        FROM usuario u
        JOIN pedido p ON p.id_usuario = u.id_usuario
        GROUP BY u.nome
        ORDER BY valor_total_gasto DESC;
        """
        self.executar_consulta(sql, "12. Listagem de Número Total de Pedidos, Valor Médio por Pedido e Valor Total Gasto")
    
    def consulta_13_relatorio_mensal(self):
        """13. Listagem de Vendas por Mês/Ano"""
        sql = """
        SELECT TO_CHAR(p.data_pedido, 'YYYY-MM') AS periodo,
            COUNT(DISTINCT p.id_pedido) AS total_pedidos,
            COUNT(DISTINCT ip.id_produto) AS produtos_diferentes_vendidos,
            SUM(ip.subtotal) AS faturamento_total
        FROM pedido p
        JOIN itens_pedido ip ON ip.id_pedido = p.id_pedido
        GROUP BY TO_CHAR(p.data_pedido, 'YYYY-MM')
        ORDER BY periodo;
        """
        self.executar_consulta(sql, "13. Listagem de Vendas por Mês/Ano")
    
    def consulta_14_produtos_nao_vendidos(self):
        """14. Listagem de Produtos Ativos que Nunca Foram Incluídos em Nenhum Pedido"""
        sql = """
        SELECT p.id_produto, p.nome
        FROM produto p
        JOIN itens_pedido ip ON ip.id_produto = p.id_produto
        WHERE p.ativo = TRUE
        GROUP BY p.id_produto, p.nome
        HAVING COUNT(ip.id_item) = 0;
        """
        self.executar_consulta(sql, "14. Listagem de Produtos Ativos que Nunca Foram Incluídos em Nenhum Pedido")
    
    def consulta_15_ticket_medio_categoria(self):
        """15. Listagem de Ticket Médio para Cada Categoria de Produto"""
        sql = """
        SELECT p.categoria, AVG(ip.subtotal) AS ticket_medio
        FROM produto p
        JOIN itens_pedido ip ON ip.id_produto = p.id_produto
        JOIN pedido pe ON pe.id_pedido = ip.id_pedido
        WHERE pe.status_pedido != 'cancelado'
        GROUP BY p.categoria;
        """
        self.executar_consulta(sql, "15. Listagem de Ticket Médio para Cada Categoria de Produto")
    
    # ========================================
    # MENUS 
    # ======================================== 
    def menu_exercicios(self):
        """MENU"""
        while True:            
            print("=" * 40)
            print("1. Listagem de Usuários Ativos")
            print("2. Catálogo de Produtos por Categoria")
            print("3. Contagem de Pedidos por Status")
            print("4. Alerta de Estoque Baixo")
            print("5. Histórico de Pedidos Recentes")
            print("6. Produtos Mais Caros por Categoria")
            print("7. Clientes com Dados Incompletos")
            print("8. Pedidos Pendentes de Entrega")
            print("9. Detalhamento Completo de Pedidos")
            print("10. Ranking dos Produtos Mais Vendidos")
            print("11. Análise de Clientes Sem Compras")
            print("12. Estatísticas de Compras por Cliente")
            print("13. Relatório Mensal de Vendas")
            print("14. Produtos que Nunca Foram Vendidos")
            print("15. Análise de Ticket Médio por Categoria")            
            print("0. Voltar ao Menu Principal")
            print("=" * 40)
            
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == "1":
                self.consulta_01_usuarios_ativos()
            elif opcao == "2":
                self.consulta_02_produtos_categoria()
            elif opcao == "3":
                self.consulta_03_pedidos_status()
            elif opcao == "4":
                self.consulta_04_estoque_baixo()
            elif opcao == "5":
                self.consulta_05_pedidos_recentes()
            elif opcao == "6":
                self.consulta_06_produtos_caros_categoria()
            elif opcao == "7":
                self.consulta_07_contatos_incompletos()
            elif opcao == "8":
                self.consulta_08_pedidos_enviados()
            elif opcao == "9":
                self.consulta_09_detalhamento_pedido()
            elif opcao == "10":
                self.consulta_10_ranking_produtos()
            elif opcao == "11":
                self.consulta_11_clientes_sem_compras()
            elif opcao == "12":
                self.consulta_12_estatisticas_cliente()
            elif opcao == "13":
                self.consulta_13_relatorio_mensal()
            elif opcao == "14":
                self.consulta_14_produtos_nao_vendidos()
            elif opcao == "15":
                self.consulta_15_ticket_medio_categoria()                
            elif opcao == "0":
                break
            else:
                print("Opção inválida!")
            
            input("\nPressione ENTER para continuar...")

def main():
    cli = SistemaVendasCLI()
    if cli.conectar_banco():
        try:
            cli.menu_exercicios()
        finally:
            cli.desconectar_banco()
    else:
        print("Falha ao conectar ao banco de dados.")
        sys.exit(1)

if __name__ == "__main__":
    main()