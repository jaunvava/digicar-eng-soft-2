"""Popula uma empresa com dados de demonstração de uma oficina mecânica.

    python manage.py seed_demo                 # empresa de código 1
    python manage.py seed_demo --empresa 1 --limpar

Pessoas e empresas são fictícias. CPF, CNPJ e códigos EAN têm dígitos
verificadores válidos, mas são gerados aleatoriamente. Os dados são
determinísticos (mesma semente gera sempre o mesmo resultado).
"""
import random
import unicodedata
from datetime import date, datetime, time, timedelta
from decimal import ROUND_HALF_UP, Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from clientes.models import Cliente, Veiculo
from core.models import Empresa, PerfilUsuario
from financeiro.facade import FinanceiroFacade
from financeiro.models import ContaPagar, ContaReceber
from fornecedores.models import Fornecedor
from orcamentos.models import ItemOrcamento, Orcamento
from ordens.models import ItemOrdemServico, OrdemServico
from produtos.models import MovimentoEstoque, Produto

CENTAVO = Decimal('0.01')
PREFIXO_TECNICO = 'tecnico.demo.'

NOMES = [
    'Ana', 'Bruno', 'Carla', 'Diego', 'Eduarda', 'Felipe', 'Gabriela', 'Henrique', 'Isabela',
    'João Pedro', 'Juliana', 'Lucas', 'Mariana', 'Mateus', 'Natália', 'Otávio', 'Patrícia',
    'Rafael', 'Renata', 'Rodrigo', 'Sabrina', 'Thiago', 'Vanessa', 'Vinícius', 'Larissa',
    'Gustavo', 'Camila', 'Fernando', 'Letícia', 'André', 'Beatriz', 'Marcelo',
]
SOBRENOMES = [
    'Silva', 'Santos', 'Oliveira', 'Souza', 'Lima', 'Pereira', 'Ferreira', 'Costa', 'Rodrigues',
    'Almeida', 'Nascimento', 'Carvalho', 'Araújo', 'Ribeiro', 'Barbosa', 'Cavalcanti', 'Albuquerque',
    'Monteiro', 'Barros', 'Freitas', 'Moura', 'Teixeira', 'Correia', 'Melo', 'Batista',
]
EMPRESAS_CLIENTES = [
    'Transportadora Rota Nordeste Ltda', 'Locadora Mar Azul Veículos Ltda',
    'Construtora Pedra Forte Ltda', 'Distribuidora Sabor do Agreste Ltda',
    'Clínica Odontológica Sorriso Pleno', 'Padaria Pão Quente do Recife ME',
    'Floricultura Jardim das Graças ME', 'Escritório Contábil Exato S/S',
]
# Bairros reais com CEP de referência (logradouros fictícios em numeração).
ENDERECOS = [
    ('Recife', 'Boa Viagem', 'Av. Conselheiro Aguiar', '51020-020'),
    ('Recife', 'Boa Viagem', 'Rua Ribeiro de Brito', '51021-310'),
    ('Recife', 'Graças', 'Rua das Graças', '52011-200'),
    ('Recife', 'Espinheiro', 'Rua do Espinheiro', '52020-020'),
    ('Recife', 'Casa Forte', 'Av. Dezessete de Agosto', '52060-590'),
    ('Recife', 'Madalena', 'Rua Real da Torre', '50610-000'),
    ('Recife', 'Torre', 'Rua José Bonifácio', '50710-000'),
    ('Recife', 'Pina', 'Av. Herculano Bandeira', '51110-130'),
    ('Recife', 'Imbiribeira', 'Av. Mascarenhas de Morais', '51150-000'),
    ('Recife', 'Várzea', 'Av. Afonso Olindense', '50810-000'),
    ('Olinda', 'Bairro Novo', 'Av. Getúlio Vargas', '53030-010'),
    ('Olinda', 'Casa Caiada', 'Av. Ministro Marcos Freire', '53130-540'),
    ('Jaboatão dos Guararapes', 'Piedade', 'Av. Bernardo Vieira de Melo', '54410-010'),
    ('Jaboatão dos Guararapes', 'Candeias', 'Av. Bernardo Vieira de Melo', '54440-000'),
]
VEICULOS = [
    ('Fiat', 'Argo 1.3 Drive', ['Branco', 'Prata', 'Vermelho']),
    ('Fiat', 'Strada Freedom 1.3', ['Branco', 'Prata']),
    ('Fiat', 'Mobi Like 1.0', ['Branco', 'Vermelho']),
    ('Volkswagen', 'Gol 1.0', ['Prata', 'Branco', 'Preto']),
    ('Volkswagen', 'Polo Highline 1.0 TSI', ['Cinza', 'Branco']),
    ('Volkswagen', 'T-Cross 200 TSI', ['Branco', 'Azul']),
    ('Chevrolet', 'Onix LT 1.0', ['Preto', 'Prata', 'Branco']),
    ('Chevrolet', 'Tracker 1.0 Turbo', ['Branco', 'Cinza']),
    ('Hyundai', 'HB20 Comfort 1.0', ['Prata', 'Branco']),
    ('Hyundai', 'Creta Action 1.6', ['Preto', 'Prata']),
    ('Toyota', 'Corolla XEi 2.0', ['Prata', 'Preto']),
    ('Toyota', 'Hilux SRV 2.8 Diesel', ['Branco', 'Prata']),
    ('Honda', 'Civic EXL 2.0', ['Cinza', 'Preto']),
    ('Honda', 'HR-V EX 1.5', ['Branco', 'Cinza']),
    ('Renault', 'Kwid Zen 1.0', ['Laranja', 'Branco']),
    ('Renault', 'Duster 1.6', ['Marrom', 'Prata']),
    ('Jeep', 'Renegade Longitude 1.3', ['Verde', 'Branco']),
    ('Jeep', 'Compass Limited 1.3', ['Preto', 'Cinza']),
    ('Ford', 'Ka SE 1.0', ['Vermelho', 'Prata']),
    ('Nissan', 'Kicks SV 1.6', ['Laranja', 'Branco']),
]
# (nome, unidade, custo, venda, estoque inicial, mínimo)
PECAS = [
    ('Óleo Motor 5W30 Sintético Mobil Super 1L', 'L', '32.90', '54.90', 60, 24),
    ('Óleo Motor 15W40 Semissintético Lubrax 1L', 'L', '24.50', '39.90', 40, 20),
    ('Filtro de Óleo Tecfil PSL55', 'UN', '18.40', '34.90', 25, 10),
    ('Filtro de Ar Motor Mann C 27 005', 'UN', '29.90', '59.90', 14, 6),
    ('Filtro de Combustível Bosch GB 0450', 'UN', '22.00', '44.90', 12, 6),
    ('Filtro de Cabine (Ar-condicionado) Wega AKX1340', 'UN', '19.90', '42.00', 16, 6),
    ('Pastilha de Freio Dianteira Cobreq N-1171', 'JG', '68.00', '139.90', 10, 4),
    ('Disco de Freio Ventilado Fremax BD5301', 'UN', '112.00', '219.00', 6, 4),
    ('Fluido de Freio DOT 4 Bosch 500ml', 'UN', '21.50', '39.90', 18, 6),
    ('Vela de Ignição NGK BKR6E', 'UN', '17.90', '34.90', 32, 12),
    ('Correia Dentada Gates 5501XS', 'UN', '89.00', '169.90', 5, 3),
    ('Tensor da Correia Dentada SKF VKM 11130', 'UN', '118.00', '229.00', 3, 2),
    ('Amortecedor Dianteiro Monroe SP0301', 'UN', '245.00', '429.00', 4, 4),
    ('Bateria Moura 60Ah M60GD', 'UN', '389.00', '599.00', 5, 3),
    ('Lâmpada Farol H4 Philips 12V 60/55W', 'UN', '18.00', '35.90', 20, 8),
    ('Palheta Limpador Bosch Aerofit 22"', 'UN', '36.00', '69.90', 12, 6),
    ('Aditivo de Radiador Paraflu Orgânico 1L', 'L', '19.90', '36.90', 15, 6),
    ('Kit Embreagem LuK 620 3089 00', 'KIT', '520.00', '899.00', 2, 2),
    ('Pneu Pirelli Cinturato P1 175/70 R14', 'UN', '329.00', '489.00', 8, 4),
    ('Higienizador de Ar-condicionado Wurth 300ml', 'UN', '24.00', '49.90', 10, 4),
]
# (nome, preço de venda)
SERVICOS = [
    ('Troca de óleo e filtro (mão de obra)', '60.00'),
    ('Alinhamento e balanceamento', '120.00'),
    ('Revisão preventiva 10.000 km', '280.00'),
    ('Diagnóstico eletrônico com scanner', '150.00'),
    ('Substituição de pastilhas de freio', '110.00'),
    ('Substituição de discos e pastilhas', '180.00'),
    ('Troca de correia dentada e tensor', '350.00'),
    ('Higienização do ar-condicionado', '130.00'),
    ('Substituição de amortecedores (par)', '260.00'),
    ('Troca de embreagem', '480.00'),
    ('Mão de obra mecânica (hora)', '140.00'),
]
# defeito reclamado, defeito constatado, solução, serviços, peças (nome: quantidade)
ATENDIMENTOS = [
    ('Revisão dos 10 mil km.', 'Veículo dentro do plano de manutenção.',
     'Realizada revisão preventiva com troca de óleo e filtros.',
     ['Revisão preventiva 10.000 km'],
     {'Óleo Motor 5W30 Sintético Mobil Super 1L': 4, 'Filtro de Óleo Tecfil PSL55': 1, 'Filtro de Ar Motor Mann C 27 005': 1}),
    ('Barulho ao frear.', 'Pastilhas dianteiras no limite de desgaste.',
     'Substituídas as pastilhas dianteiras e completado o fluido de freio.',
     ['Substituição de pastilhas de freio'],
     {'Pastilha de Freio Dianteira Cobreq N-1171': 1, 'Fluido de Freio DOT 4 Bosch 500ml': 1}),
    ('Volante trepidando ao frear em velocidade.', 'Discos de freio empenados.',
     'Substituídos discos e pastilhas dianteiros.',
     ['Substituição de discos e pastilhas'],
     {'Disco de Freio Ventilado Fremax BD5301': 2, 'Pastilha de Freio Dianteira Cobreq N-1171': 1}),
    ('Carro puxando para a direita.', 'Geometria fora do padrão.',
     'Realizado alinhamento e balanceamento das quatro rodas.',
     ['Alinhamento e balanceamento'], {}),
    ('Luz da injeção acesa no painel.', 'Falha de ignição no cilindro 3 (velas desgastadas).',
     'Substituído o jogo de velas e apagados os códigos de falha.',
     ['Diagnóstico eletrônico com scanner'],
     {'Vela de Ignição NGK BKR6E': 4}),
    ('Ar-condicionado com mau cheiro.', 'Filtro de cabine saturado.',
     'Higienizado o sistema e substituído o filtro de cabine.',
     ['Higienização do ar-condicionado'],
     {'Filtro de Cabine (Ar-condicionado) Wega AKX1340': 1, 'Higienizador de Ar-condicionado Wurth 300ml': 1}),
    ('Troca preventiva da correia dentada (60 mil km).', 'Correia com trincas laterais.',
     'Substituídos correia dentada e tensor.',
     ['Troca de correia dentada e tensor'],
     {'Correia Dentada Gates 5501XS': 1, 'Tensor da Correia Dentada SKF VKM 11130': 1}),
    ('Carro não pega pela manhã.', 'Bateria com carga abaixo de 30% e sem retenção.',
     'Substituída a bateria e testado o sistema de carga.',
     ['Mão de obra mecânica (hora)'],
     {'Bateria Moura 60Ah M60GD': 1}),
    ('Barulho na suspensão em lombadas.', 'Amortecedores dianteiros com vazamento.',
     'Substituído o par de amortecedores dianteiros.',
     ['Substituição de amortecedores (par)', 'Alinhamento e balanceamento'],
     {'Amortecedor Dianteiro Monroe SP0301': 2}),
    ('Pedal da embreagem alto e patinando.', 'Disco de embreagem gasto.',
     'Substituído o kit de embreagem.',
     ['Troca de embreagem'],
     {'Kit Embreagem LuK 620 3089 00': 1}),
    ('Troca de óleo.', 'Óleo vencido.', 'Trocados óleo e filtro.',
     ['Troca de óleo e filtro (mão de obra)'],
     {'Óleo Motor 15W40 Semissintético Lubrax 1L': 4, 'Filtro de Óleo Tecfil PSL55': 1}),
    ('Farol baixo queimado e palhetas ruins.', 'Lâmpada H4 queimada e palhetas ressecadas.',
     'Substituídas lâmpadas e palhetas.',
     ['Mão de obra mecânica (hora)'],
     {'Lâmpada Farol H4 Philips 12V 60/55W': 2, 'Palheta Limpador Bosch Aerofit 22"': 2}),
]
FORNECEDORES = [
    ('Auto Peças Boa Viagem Comércio Ltda', 'Recife', 'Imbiribeira', 'vendas@autopecasboaviagem.com.br'),
    ('Distribuidora Nordeste Autopeças Ltda', 'Jaboatão dos Guararapes', 'Prazeres', 'pedidos@nordesteautopecas.com.br'),
    ('Lubrificantes Capibaribe Ltda', 'Recife', 'Afogados', 'comercial@lubcapibaribe.com.br'),
    ('Pneus & Rodas Guararapes Ltda', 'Jaboatão dos Guararapes', 'Cavaleiro', 'contato@pneusguararapes.com.br'),
    ('Baterias Olinda Distribuição Ltda', 'Olinda', 'Peixinhos', 'vendas@bateriasolinda.com.br'),
    ('Ferramentas Pernambuco Ltda', 'Recife', 'São José', 'atendimento@ferramentaspe.com.br'),
]
TECNICOS = [('carlos', 'Carlos', 'Menezes'), ('jose', 'José', 'Bezerra'), ('roberta', 'Roberta', 'Lins')]
FORMAS_RECEBIMENTO = ['pix', 'pix', 'pix', 'cartao_credito', 'cartao_debito', 'dinheiro', 'transferencia', 'boleto']


def _dv_cpf(digitos):
    for tamanho in (9, 10):
        soma = sum(int(d) * (tamanho + 1 - i) for i, d in enumerate(digitos[:tamanho]))
        resto = (soma * 10) % 11
        digitos.append(0 if resto == 10 else resto)
    return digitos


def gerar_cpf(rnd):
    d = _dv_cpf([rnd.randint(0, 9) for _ in range(9)])
    s = ''.join(map(str, d))
    return f'{s[:3]}.{s[3:6]}.{s[6:9]}-{s[9:]}'


def gerar_cnpj(rnd):
    d = [rnd.randint(0, 9) for _ in range(8)] + [0, 0, 0, 1]
    for pesos in ([5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2], [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]):
        resto = sum(a * b for a, b in zip(d, pesos)) % 11
        d.append(0 if resto < 2 else 11 - resto)
    s = ''.join(map(str, d))
    return f'{s[:2]}.{s[2:5]}.{s[5:8]}/{s[8:12]}-{s[12:]}'


def gerar_ean13(rnd):
    d = [7, 8, 9] + [rnd.randint(0, 9) for _ in range(9)]
    soma = sum(n * (3 if i % 2 else 1) for i, n in enumerate(d))
    d.append((10 - soma % 10) % 10)
    return ''.join(map(str, d))


def gerar_placa(rnd):
    letras = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return (''.join(rnd.choice(letras) for _ in range(3)) + str(rnd.randint(0, 9))
            + rnd.choice(letras) + f'{rnd.randint(0, 99):02d}')


def gerar_chassi(rnd):
    # VIN tem 17 caracteres e não usa I, O e Q.
    caracteres = 'ABCDEFGHJKLMNPRSTUVWXYZ0123456789'
    return '9' + ''.join(rnd.choice(caracteres) for _ in range(16))


def celular(rnd):
    return f'(81) 9{rnd.randint(8100, 9999)}-{rnd.randint(1000, 9999)}'


def fixo(rnd):
    return f'(81) 3{rnd.randint(100, 799)}-{rnd.randint(1000, 9999)}'


def sem_acento(texto):
    return unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode()


def em_datetime(dia, hora=9):
    return timezone.make_aware(datetime.combine(dia, time(hora, 0)))


def dinheiro(valor):
    return Decimal(valor).quantize(CENTAVO, rounding=ROUND_HALF_UP)


class Command(BaseCommand):
    help = 'Popula uma empresa com dados de demonstração (oficina mecânica em Recife/PE).'

    def add_arguments(self, parser):
        parser.add_argument('--empresa', default='1', help='Código da empresa (padrão: 1).')
        parser.add_argument('--limpar', action='store_true',
                            help='Apaga os dados operacionais da empresa antes de popular.')
        parser.add_argument('--semente', type=int, default=2026, help='Semente aleatória.')

    def handle(self, *args, **opcoes):
        try:
            empresa = Empresa.objects.get(codigo=opcoes['empresa'])
        except Empresa.DoesNotExist as exc:
            raise CommandError(f"Empresa com código {opcoes['empresa']!r} não existe.") from exc

        tem_dados = Cliente.objects.filter(empresa=empresa).exists() or Produto.objects.filter(empresa=empresa).exists()
        if tem_dados and not opcoes['limpar']:
            raise CommandError('A empresa já tem dados. Use --limpar para apagar e popular de novo.')

        self.rnd = random.Random(opcoes['semente'])
        self.hoje = date.today()
        self.empresa = empresa

        with transaction.atomic():
            if opcoes['limpar']:
                self.limpar()
            self.atualizar_empresa()
            tecnicos = self.criar_tecnicos()
            fornecedores = self.criar_fornecedores()
            pecas, servicos = self.criar_produtos()
            clientes = self.criar_clientes()
            ordens = self.criar_ordens(clientes, tecnicos, pecas, servicos)
            orcamentos = self.criar_orcamentos(clientes, pecas, servicos)
            receber = self.criar_contas_receber(ordens)
            pagar = self.criar_contas_pagar(fornecedores)

        self.stdout.write(self.style.SUCCESS(
            f'Empresa {empresa.codigo} ({empresa.nome}) populada: '
            f'{len(clientes)} clientes, {Veiculo.objects.filter(cliente__empresa=empresa).count()} veículos, '
            f'{len(pecas)} peças, {len(servicos)} serviços, {len(fornecedores)} fornecedores, '
            f'{len(tecnicos)} técnicos, {len(ordens)} OS, {len(orcamentos)} orçamentos, '
            f'{receber} contas a receber, {pagar} contas a pagar.'
        ))

    # ── Limpeza ─────────────────────────────────────────────────────────
    def limpar(self):
        e = self.empresa
        ContaPagar.objects.filter(empresa=e).delete()
        ContaReceber.objects.filter(empresa=e).delete()
        OrdemServico.objects.filter(empresa=e).delete()
        Orcamento.objects.filter(empresa=e).delete()
        Cliente.objects.filter(empresa=e).delete()
        Produto.objects.filter(empresa=e).delete()
        Fornecedor.objects.filter(empresa=e).delete()
        User.objects.filter(username__startswith=PREFIXO_TECNICO, perfil__empresa=e).delete()

    # ── Cadastros ───────────────────────────────────────────────────────
    def atualizar_empresa(self):
        e = self.empresa
        if e.nome in ('', 'teste'):
            e.nome = 'DigiCAR Oficina Mecânica'
        e.cnpj = e.cnpj or gerar_cnpj(self.rnd)
        e.telefone = e.telefone or '(81) 3345-2210'
        e.email = e.email or 'contato@digicaroficina.com.br'
        e.endereco = e.endereco or 'Av. Mascarenhas de Morais, 2150 - Imbiribeira, Recife/PE'
        e.save()

    def criar_tecnicos(self):
        tecnicos = []
        for login, nome, sobrenome in TECNICOS:
            usuario = User.objects.create_user(
                username=PREFIXO_TECNICO + login, first_name=nome, last_name=sobrenome,
                email=f'{login}@digicaroficina.com.br',
            )
            usuario.set_unusable_password()  # técnicos de exemplo não fazem login
            usuario.save()
            PerfilUsuario.objects.create(user=usuario, empresa=self.empresa, perfil='operador',
                                         cargo='Mecânico', ativo=True)
            tecnicos.append(usuario)
        return tecnicos

    def criar_fornecedores(self):
        fornecedores = []
        for nome, cidade, bairro, email in FORNECEDORES:
            fornecedores.append(Fornecedor.objects.create(
                empresa=self.empresa, tipo='PJ', nome=nome, cpf_cnpj=gerar_cnpj(self.rnd),
                telefone1=fixo(self.rnd), telefone2=celular(self.rnd), email=email,
                site='https://www.' + email.split('@')[1],
                cep=f'5{self.rnd.randint(0, 4)}{self.rnd.randint(100, 999)}-{self.rnd.randint(0, 999):03d}',
                endereco='Rua Comercial', numero=str(self.rnd.randint(10, 2500)),
                bairro=bairro, cidade=cidade, estado='PE',
            ))
        return fornecedores

    def criar_produtos(self):
        pecas, servicos = {}, {}
        inicio = self.hoje - timedelta(days=200)
        for nome, unidade, custo, venda, estoque, minimo in PECAS:
            produto = Produto.objects.create(
                empresa=self.empresa, tipo='produto', codigo=gerar_ean13(self.rnd), nome=nome,
                unidade=unidade, preco_custo=Decimal(custo), preco_venda=Decimal(venda),
                estoque_atual=Decimal(0), estoque_minimo=Decimal(minimo),
            )
            self.movimentar(produto, 'entrada', Decimal(estoque), 'Estoque inicial (compra de abertura)', inicio)
            pecas[nome] = produto
        for nome, venda in SERVICOS:
            servicos[nome] = Produto.objects.create(
                empresa=self.empresa, tipo='servico', nome=nome, unidade='SV',
                preco_venda=Decimal(venda),
            )
        return pecas, servicos

    def movimentar(self, produto, tipo, quantidade, motivo, dia):
        anterior = produto.estoque_atual
        produto.estoque_atual = anterior + quantidade if tipo == 'entrada' else anterior - quantidade
        produto.save(update_fields=['estoque_atual', 'atualizado_em'])
        movimento = MovimentoEstoque.objects.create(
            produto=produto, tipo=tipo, quantidade=quantidade, estoque_anterior=anterior,
            estoque_posterior=produto.estoque_atual, motivo=motivo,
        )
        MovimentoEstoque.objects.filter(pk=movimento.pk).update(criado_em=em_datetime(dia, 10))

    def criar_clientes(self):
        rnd = self.rnd
        clientes = []
        usados = set()
        for i in range(32):
            cidade, bairro, rua, cep = rnd.choice(ENDERECOS)
            if i < len(EMPRESAS_CLIENTES):
                nome = EMPRESAS_CLIENTES[i]
                dominio = sem_acento(nome.split()[1].lower())
                dados = dict(tipo='PJ', nome=nome, cpf_cnpj=gerar_cnpj(rnd),
                             rg_ie=f'{rnd.randint(1000000, 9999999)}-{rnd.randint(10, 99)}',
                             email=f'financeiro@{dominio}.com.br', telefone=fixo(rnd))
            else:
                while True:
                    nome = f'{rnd.choice(NOMES)} {rnd.choice(SOBRENOMES)} {rnd.choice(SOBRENOMES)}'
                    if nome not in usados and nome.split()[-1] != nome.split()[-2]:
                        break
                partes = sem_acento(nome.lower()).split()
                dados = dict(tipo='PF', nome=nome, cpf_cnpj=gerar_cpf(rnd),
                             rg_ie=f'{rnd.randint(1000000, 9999999)} SDS/PE',
                             email=f'{partes[0]}.{partes[-1]}{rnd.randint(1, 99)}@email.com')
            usados.add(nome)
            cliente = Cliente.objects.create(
                empresa=self.empresa, celular=celular(rnd), cep=cep, endereco=rua,
                numero=str(rnd.randint(12, 3200)),
                complemento=rnd.choice(['', '', f'Apto {rnd.randint(101, 1804)}', 'Casa', f'Sala {rnd.randint(101, 912)}']),
                bairro=bairro, cidade=cidade, estado='PE', ativo=(i != 31), **dados,
            )
            # Cadastros espalhados nos últimos meses (alguns neste mês).
            criado = self.hoje - timedelta(days=rnd.randint(0, 200) if i % 5 else rnd.randint(0, 8))
            Cliente.objects.filter(pk=cliente.pk).update(criado_em=em_datetime(criado))

            for _ in range(2 if dados['tipo'] == 'PJ' else rnd.choice([1, 1, 1, 2])):
                marca, modelo, cores = rnd.choice(VEICULOS)
                Veiculo.objects.create(
                    cliente=cliente, placa=gerar_placa(rnd), marca=marca, modelo=modelo,
                    ano=rnd.randint(2014, 2025), cor=rnd.choice(cores), chassi=gerar_chassi(rnd),
                )
            clientes.append(cliente)
        return clientes

    # ── Movimento ───────────────────────────────────────────────────────
    def criar_ordens(self, clientes, tecnicos, pecas, servicos):
        rnd = self.rnd
        ordens = []
        # 36 OS nos últimos 6 meses + 14 recentes (as que ainda estão na oficina).
        dias = [rnd.randint(13, 180) for _ in range(36)] + [rnd.randint(0, 12) for _ in range(14)]
        dias.sort(reverse=True)  # da mais antiga para a mais recente: numeração em ordem
        for dias_atras in dias:
            cliente = rnd.choice(clientes[:-1])  # o cliente inativo não tem OS
            veiculo = rnd.choice(list(cliente.veiculos.all()))
            entrada = self.hoje - timedelta(days=dias_atras)
            reclamado, constatado, solucao, nomes_servicos, nomes_pecas = rnd.choice(ATENDIMENTOS)

            if dias_atras > 12:
                status = rnd.choices(['entregue', 'cancelada'], [12, 1])[0]
            elif dias_atras > 5:
                status = rnd.choice(['entregue', 'pronta', 'aguardando_peca'])
            else:
                status = rnd.choice(['aberta', 'em_andamento', 'em_andamento', 'aguardando_peca', 'pronta'])
            em_aberto = status in ('aberta', 'em_andamento', 'aguardando_peca')

            ordem = OrdemServico.objects.create(
                empresa=self.empresa, cliente=cliente, veiculo=veiculo, tecnico=rnd.choice(tecnicos),
                status=status, prioridade=rnd.choices(['baixa', 'normal', 'alta', 'urgente'], [2, 10, 3, 1])[0],
                equipamento=f'{veiculo.marca} {veiculo.modelo}', marca=veiculo.marca, modelo=veiculo.modelo,
                numero_serie=veiculo.placa, defeito_reclamado=reclamado,
                defeito_constatado='' if status == 'aberta' else constatado,
                solucao=solucao if status in ('pronta', 'entregue') else '',
                data_prevista=entrada + timedelta(days=rnd.randint(1, 4)),
                garantia_dias=90,
                observacoes=rnd.choice(['', '', 'Cliente aguarda na loja.', 'Cliente pediu orçamento por WhatsApp antes de executar.']),
            )
            v_servicos = v_pecas = Decimal(0)
            for nome in nomes_servicos:
                servico = servicos[nome]
                item = ItemOrdemServico.objects.create(
                    ordem=ordem, tipo='servico', produto=servico, descricao=servico.nome,
                    quantidade=Decimal(1), preco_unitario=servico.preco_venda,
                )
                v_servicos += item.subtotal
            for nome, quantidade in nomes_pecas.items():
                peca = pecas[nome]
                quantidade = Decimal(quantidade)
                if peca.estoque_atual < quantidade:
                    # Reposição: compra do fornecedor antes de usar a peça.
                    self.movimentar(peca, 'entrada', peca.estoque_minimo * 2 + quantidade,
                                    'Reposição de estoque (pedido ao fornecedor)', entrada - timedelta(days=1))
                item = ItemOrdemServico.objects.create(
                    ordem=ordem, tipo='peca', produto=peca, descricao=peca.nome,
                    quantidade=quantidade, preco_unitario=peca.preco_venda,
                )
                v_pecas += item.subtotal
                if status != 'cancelada':
                    self.movimentar(peca, 'saida', quantidade, f'Utilização na OS #{ordem.numero}', entrada)

            ordem.valor_servicos = v_servicos
            ordem.valor_pecas = v_pecas
            if cliente.tipo == 'PJ' or rnd.random() < 0.15:
                ordem.desconto = dinheiro((v_servicos + v_pecas) * Decimal('0.05'))
            if not em_aberto and status != 'cancelada':
                ordem.data_conclusao = em_datetime(entrada + timedelta(days=rnd.randint(0, 3)), 17)
            ordem.save()
            OrdemServico.objects.filter(pk=ordem.pk).update(data_entrada=em_datetime(entrada, rnd.randint(8, 11)))
            ordem.data_entrada = em_datetime(entrada)
            ordens.append(ordem)
        return ordens

    def criar_orcamentos(self, clientes, pecas, servicos):
        rnd = self.rnd
        orcamentos = []
        for _ in range(16):
            dias_atras = rnd.randint(0, 120)
            criado = self.hoje - timedelta(days=dias_atras)
            validade = criado + timedelta(days=15)
            if validade < self.hoje:
                status = rnd.choice(['aprovado', 'aprovado', 'reprovado', 'expirado'])
            else:
                status = rnd.choice(['rascunho', 'enviado', 'enviado', 'aprovado'])
            orcamento = Orcamento.objects.create(
                empresa=self.empresa, cliente=rnd.choice(clientes[:-1]), status=status, validade=validade,
                observacoes='Valores válidos por 15 dias. Garantia de 90 dias em peças e serviços.',
            )
            _, _, _, nomes_servicos, nomes_pecas = rnd.choice(ATENDIMENTOS)
            subtotal = Decimal(0)
            itens = [(servicos[n], Decimal(1)) for n in nomes_servicos]
            itens += [(pecas[n], Decimal(q)) for n, q in nomes_pecas.items()]
            for produto, quantidade in itens:
                item = ItemOrcamento.objects.create(
                    orcamento=orcamento, produto=produto, quantidade=quantidade,
                    preco_unitario=produto.preco_venda,
                )
                subtotal += item.subtotal
            orcamento.subtotal = subtotal
            orcamento.desconto = dinheiro(subtotal * Decimal('0.05')) if rnd.random() < 0.3 else Decimal(0)
            orcamento.total = subtotal - orcamento.desconto
            orcamento.save()
            Orcamento.objects.filter(pk=orcamento.pk).update(criado_em=em_datetime(criado, 14))
            orcamentos.append(orcamento)
        return orcamentos

    # ── Financeiro ──────────────────────────────────────────────────────
    def baixar(self, conta, valor, dia, forma, metodo, **extra):
        dados = {'valor': str(valor), 'data_pagamento': dia.isoformat(), 'forma_pagamento': forma}
        if forma == 'cartao_credito':
            dados['parcelas'] = str(self.rnd.choice([1, 1, 2, 3]))
        if forma == 'cheque':
            dados['numero_cheque'] = str(self.rnd.randint(100000, 999999))
        dados.update(extra)
        getattr(FinanceiroFacade(), metodo)(conta, dados)

    def criar_contas_receber(self, ordens):
        rnd = self.rnd
        total = 0
        for ordem in ordens:
            if ordem.status not in ('pronta', 'entregue') or ordem.total <= 0:
                continue
            entrada = ordem.data_entrada.date()
            parcelas = 3 if ordem.total > 1200 else (2 if ordem.total > 600 and rnd.random() < 0.5 else 1)
            valor_parcela = dinheiro(ordem.total / parcelas)
            for n in range(1, parcelas + 1):
                valor = valor_parcela if n < parcelas else ordem.total - valor_parcela * (parcelas - 1)
                vencimento = entrada + timedelta(days=30 * (n - 1) + (0 if parcelas == 1 else 5))
                conta = ContaReceber.objects.create(
                    empresa=self.empresa, cliente=ordem.cliente, numero_titulo=f'OS{ordem.numero:04d}',
                    descricao=f'OS #{ordem.numero} - {ordem.equipamento}', parcela=f'{n}/{parcelas}',
                    valor=valor, emissao=entrada, vencimento=vencimento,
                )
                total += 1
                if vencimento > self.hoje:
                    continue  # a vencer: fica pendente
                destino = rnd.choices(['pago', 'parcial', 'atrasado'], [80, 6, 14])[0]
                forma = rnd.choice(FORMAS_RECEBIMENTO)
                if destino == 'pago':
                    dia = min(self.hoje, vencimento + timedelta(days=rnd.choice([0, 0, 0, 1, 3])))
                    self.baixar(conta, valor, dia, forma, 'registrar_baixa_receber')
                elif destino == 'parcial':
                    self.baixar(conta, dinheiro(valor * Decimal('0.4')), vencimento, forma,
                                'registrar_baixa_receber', observacoes='Cliente pagou entrada; restante combinado.')
                    if vencimento < self.hoje:
                        ContaReceber.objects.filter(pk=conta.pk).update(status='atrasado')
                else:
                    ContaReceber.objects.filter(pk=conta.pk).update(status='atrasado')
        return total

    def criar_contas_pagar(self, fornecedores):
        rnd = self.rnd
        total = 0
        despesas_fixas = [
            ('Imobiliária Recife Centro', 'Aluguel do galpão', 'Aluguel', Decimal('4800.00'), 5),
            ('Concessionária de Energia', 'Energia elétrica', 'Utilidades', None, 12),
            ('Companhia de Saneamento', 'Água e esgoto', 'Utilidades', None, 15),
            ('Provedor Fibra Net', 'Internet fibra 500 Mb', 'Utilidades', Decimal('149.90'), 10),
            ('Contabilidade Exato', 'Honorários contábeis', 'Serviços', Decimal('950.00'), 20),
        ]
        inicio = self.hoje.replace(day=1)
        for meses_atras in range(6, -2, -1):  # 6 meses atrás até o mês que vem
            ano, mes = inicio.year, inicio.month - meses_atras
            while mes < 1:
                ano, mes = ano - 1, mes + 12
            while mes > 12:
                ano, mes = ano + 1, mes - 12
            for fornecedor, descricao, categoria, valor, dia in despesas_fixas:
                if valor is None:
                    valor = dinheiro(rnd.uniform(380, 920) if 'Energia' in descricao else rnd.uniform(90, 210))
                total += self.conta_pagar(fornecedor, f'{descricao} {mes:02d}/{ano}', categoria,
                                          valor, date(ano, mes, dia))
            for _ in range(rnd.randint(2, 3)):
                fornecedor = rnd.choice(fornecedores)
                valor = dinheiro(rnd.uniform(650, 4200))
                nota = rnd.randint(10000, 99999)
                total += self.conta_pagar(fornecedor.nome, f'Compra de peças - NF {nota}', 'Peças',
                                          valor, date(ano, mes, rnd.randint(1, 28)), titulo=f'NF{nota}')
        return total

    def conta_pagar(self, fornecedor, descricao, categoria, valor, vencimento, titulo=''):
        conta = ContaPagar.objects.create(
            empresa=self.empresa, fornecedor=fornecedor, descricao=descricao, categoria=categoria,
            valor=valor, vencimento=vencimento, numero_titulo=titulo,
        )
        if vencimento <= self.hoje:
            if self.rnd.random() < 0.9:
                dia = min(self.hoje, vencimento)
                forma = 'boleto' if categoria in ('Peças', 'Utilidades') else 'transferencia'
                self.baixar(conta, valor, dia, forma, 'registrar_baixa_pagar')
            else:
                ContaPagar.objects.filter(pk=conta.pk).update(status='atrasado')
        return 1
