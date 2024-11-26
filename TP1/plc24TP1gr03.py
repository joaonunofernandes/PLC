from re import *
import json

original = open("processos.txt", "rt")   # Abrir ficheiro disponibilizado para leitura e em modo de texto.
novo = open("resultado.txt", "at")       # Criar e abrir novo ficheiro para escrita e em modo de texto.

escritas = []                            # Iterar sobre as linhas do ficheiro original e escrevê-las, sem repetições, no ficheiro novo.
for l in original:
    if l not in escritas:
        novo.write(l)
        escritas.append(l)

original.close()
novo.close()

def alineaA(ficheiro):
    primeira = ficheiro.readline()
    d = {}
    for linha in ficheiro:
        if linha == primeira:
            continue                       # Ignorar a primeira linha do ficheiro.
        lista = split(r':{2,}', linha)     # Separar os itens por cada conjunto de dois ou mais símbolos ":".
        lista = split(r'-', lista[1])      # Separar o elemento da lista correspondente à data em 3 partes por cada símbolo "-".
        ano = lista[0]                     # Guardar somente o ano.
        d[ano] = d.setdefault(ano, 0) + 1  # Criar entrada no dicionário para o ano em questão e inicializar o nº de processos a 0 + 1 ou apenas incrementar esse mesmo nº.
    return d

def alineaB(ficheiro):
    primeira = ficheiro.readline()
    d = {}
    for linha in ficheiro:
        if linha == primeira:
            continue                       # Ignorar a primeira linha do ficheiro.
        lista = split(r':{2,}', linha)     # Separar os itens por cada conjunto de dois ou mais símbolos ":".
        data = split(r'-', lista[1])       # Separar o elemento da lista correspondente à data em 3 partes por cada símbolo "-".
        data = data[0]                     # Data passa a ser apenas o ano.
        data = str(int(data[:2]) + 1)      # O nosso grupo decidiu considerar os anos terminados com 00 (i.e., 1900, 2000, etc.) como pertencendo ao novo século.
        if search(r'\.', lista[-2]):       # Encontrar a primeira ocorrência do símbolo "." no penúltimo elemento de lista (o último elemento é sempre "").
            lista.pop(-2)
        lista = lista[2:-1]                # Lista passa a conter apenas os nomes do confessado, do pai e da mãe.
        palavras = []
        for elemento in lista:
            if nome := match(r'[a-zA-Z]+', elemento):         # Procurar e guarda o primeiro nome do confessado.
                    palavras.append(nome.group(0))            # Adicionar ao final da lista palavras o primeiro nome.
            if search(r',|\(| ou ', elemento):                # Procurar a 1ª ocorrência de um dos seguintes símbolos/expressões: "," "(" " ou ".
                partes = split(r',|\(| ou ', elemento)        # Se encontrar, separa a string numa lista.
                if apelido := search(r'(?<= )[a-zA-Z]+(?=[$ ])', partes[0]): # Capturar a 1ª palavra que ocorre após um espaço e antes do fim da string. Não captura o espaço no fim da string, caso exista.
                        palavras.append(apelido.group(0))                    # Adicionar ao final da lista palavras o apelido.
            else:
                if apelido := search(r'(?<= )[a-zA-Z]+(?=$)', elemento):     # Capturar a 1ª palavra que ocorre após um espaço e antes do fim da string.
                        palavras.append(apelido.group(0))                    # Adicionar ao final da lista palavras o apelido.
        if data not in d:
            d.update({data: {}})                                             # Criar nova entrada no dicionário com a data respetiva, caso ainda não exista, associando-lhe um dicionário vazio.
        freqs = d[data]
        for palavra in palavras:
            freqs[palavra] = freqs.setdefault(palavra, 0) + 1                # Criar entrada no dicionário para o nome/apelido em questão e inicializar o nº de ocorrências a 0 + 1 ou apenas incrementar esse mesmo nº.
    return d

def alineaC(ficheiro):
    primeira = ficheiro.readline()
    n = 0
    for linha in ficheiro:
        if linha == primeira:
            continue
        lista = split(r':{2,}', linha)                          # Separar os itens por cada conjunto de dois ou mais símbolos ":".
        s = lista[-2]                                           # Guardar em s o campo Observações.
        if search(r'(?<=,)(?i:Ti[oa])(?i:s?)(?=[ ]+|\.)', s):   # Capturar a primeira ocorrência da palavra Tio(a)/Tios(as), em case insensitive, que sejam precedidos pelo símbolo "," e sucedidos por 1 ou mais espaços ou por um símbolo ".".
            n += 1
    return n

def alineaD(ficheiro):
    primeira = ficheiro.readline()
    d = {}
    res = []
    for linha in ficheiro:
        if linha == primeira:
            continue
        lista = split(r':{2,}', linha)                   # Separar os itens por cada conjunto de dois ou mais símbolos ":".
        lista = lista[2:-1]                              # Lista passa a conter apenas os nomes do confessado, do pai e da mãe.
        cmp = len(lista)
        if cmp == 2:                                                                    # Lista tem 2 nomes.
            if not search(r'\.', lista[-1]):                                            # Verificar se o último elemento não é o campo observações.
                parente = search(r'[a-zA-Z ]+(?=,| \(| ou |$)', lista[1]).group(0)      # Procurar o nome do único parente.
                d[(parente, '')] = d.setdefault((parente, ''), 0) + 1                   # Atualizar dicionário.
        elif cmp == 3:                                                                  # Lista tem 3 nomes.
            if not search(r'\.', lista[-1]):                                            # Verificar se o último elemento não é o campo observações.
                pai = search(r'[a-zA-Z ]+(?=,| \(| ou |$)', lista[1]).group(0)          # Procurar o nome do pai.
                mae = search(r'[a-zA-Z ]+(?=,| \(| ou |$)', lista[2]).group(0)          # Procurar o nome da mãe.
                d[(pai,mae)] = d.setdefault((pai,mae), 0) + 1                           # Atualizar dicionário.
        elif cmp == 4:                                                                  # Lista tem 3 nomes e observações.
            pai = search(r'[a-zA-Z ]+(?=,| \(| ou |$)', lista[1]).group(0)              # Procurar o nome do pai.
            mae = search(r'[a-zA-Z ]+(?=,| \(| ou |$)', lista[2]).group(0)              # Procurar o nome da mãe.
            d[(pai,mae)] = d.setdefault((pai,mae), 0) + 1                               # Atualizar dicionário.
            if search(r'(?<=,)(?i:Irma)(?i:o?s?)(?=[ ]+|\.)', lista[-1]):               # Procurar nomes de irmãos(ãs).
                d[(pai,mae)] += 1                                                       # Atualizar dicionário.
    for pais in d:
        if d[pais] > 1:                                                                 # Verificar quais os pais com mais do que um(a) filho(a).
            res.append(pais[0])
            res.append(pais[1])
    return res                                                                          # Note-se que o nosso grupo decidiu considerar, nos casos em que uma pessoa era conhecida de duas ou mais formas, somente a primeira forma referida, já que se presume ser a principal e que, na nossa opinião, faz mais sentido contar cada ser humano apenas uma vez.

def alineaE(ficheiro):
    ficheiro.seek(0)                                                       # Voltar ao início do ficheiro.
    ficheiro.readline()                                                    # Ignorar a primeira linha (cabeçalho).
    primeiro_registo = ficheiro.readline().strip()                         # Ler a segunda linha (primeiro registo de dados). O método strip() serve para remover os espaços.
    campos = split(r':{2,}', primeiro_registo)                             # Separar os itens por cada conjunto de dois ou mais símbolos ":".
    dicionario_registo = {
        "NumProc": campos[0],
        "Data": campos[1],
        "Confessado": campos[2],
        "Pai": campos[3] if len(campos) > 3 else "",                       # Verificar se a lista campos tem mais de 3 elementos. Se tiver Atribui o valor do quarto elemento (índice 3) da lista campos à chave "pai", senão Atribui uma string vazia ("") à chave "pai".
        "Mae": campos[4] if len(campos) > 4 else "",
        "Observacoes": campos[-2] if len(campos) > 5 else ""
    }
    # Esta abordagem é usada para lidar com casos em que o campo "pai" pode não estar presente no registo original. 
    # Se o registo tiver informações suficientes (mais de 3 campos), assume-se que o quarto campo é o nome do pai. 
    # Caso contrário, usa-se uma string vazia para indicar que essa informação não está disponível.
    return json.dumps(dicionario_registo, ensure_ascii=False, indent=2)   #Converter o dicionário para uma string JSON formatada,ensure_ascii=False permite caracteres não-ASCII,indent=2 formata o JSON com indentação para melhor legibilidade.

resultado = open("resultado.txt", "rt")

print(alineaA(resultado), "\n\n")                    #Imprimir o resultado da alínea a).

resultado.close()

resultado = open("resultado.txt", "rt")

print(alineaB(resultado), "\n\n")                    #Imprimir o resultado da alínea b).

resultado.close()

resultado = open("resultado.txt", "rt")

print(alineaC(resultado), "\n\n")                    #Imprimir o resultado da alínea c).

resultado.close()

resultado = open("resultado.txt", "rt")

print(alineaD(resultado))                            #Imprimir o resultado da alínea d).

resultado.close()

resultado = open("resultado.txt", "rt")

print(alineaE(resultado))  # Imprimir o resultado da alínea e).

resultado.close()

# Opcionalmente, guardar num ficheiro.
with open("resultado.json", "w", encoding="utf-8") as ficheiro_json:
    resultado = open("resultado.txt", "rt")
    ficheiro_json.write(alineaE(resultado))
    resultado.close()

# O UTF-8 permite armazenar corretamente caracteres que não fazem parte do alfabeto inglês, como letras acentuadas (é, ã, ç), ou caracteres de outros idiomas (por exemplo, ñ do espanhol ou caracteres asiáticos como 漢字).
# Sem especificar a codificação correta, há o risco de problemas de codificação/descodificação, o que pode resultar em erros ou na corrupção de dados, especialmente se o texto contiver caracteres especiais.
# O UTF-8 é o padrão mais comum para codificação de texto na web e em sistemas modernos, tornando o ficheiro mais facilmente compatível com outras ferramentas e plataformas.

def processar_e_gerar_html():
    with open("resultado.txt", "rt", encoding="utf-8") as ficheiro:
        # Alínea A
        ficheiro.seek(0)  # Reposicionar o cursor no início do ficheiro.
        resultados_a = alineaA(ficheiro)
        
        # Alínea B
        ficheiro.seek(0)  # Reposicionar o cursor no início do ficheiro.
        resultados_b = alineaB(ficheiro)
        
        # Alínea C
        ficheiro.seek(0)  # Reposicionar o cursor no início do ficheiro.
        resultados_c = alineaC(ficheiro)
        
        # Alínea D
        ficheiro.seek(0)  # Reposicionar o cursor no início do ficheiro.
        resultados_d = alineaD(ficheiro)
        
        # Alínea E
        ficheiro.seek(0)  # Reposicionar o cursor no início do ficheiro.
        resultados_e = json.loads(alineaE(ficheiro))
        
        # Nota:
        # - Temos de usar o seek(0), porque senão corre apenas o ficheiro uma vez e depois o resto das funções vão sempre procurar as respetivas funções no fim do ficheiro.

    # Gerar o HTML.
    html = f""" 
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Processador de Pessoas listadas nos Róis de Confessados</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }}
            h1 {{ color: #333; }}
            h2 {{ color: #666; }}
            pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>Processador de Pessoas listadas nos Róis de Confessados</h1>
        
        <h2>A) Frequência de Processos por Ano</h2>
        <pre>{json.dumps(resultados_a, indent=2, ensure_ascii=False)}</pre>
        
        <h2>B) Frequência de Nomes Próprios e Apelidos por Séculos</h2>
        <pre>{json.dumps(resultados_b, indent=2, ensure_ascii=False)}</pre>
        
        <h2>C) Frequência de processos que são Recomendados por, pelo menos, um Tio</h2>
        <p>{resultados_c}</p>
        
        <h2>D) Pais que têm mais do que 1 Filho Confessado</h2>
        <pre>{json.dumps(resultados_d, indent=2, ensure_ascii=False)}</pre>
        
        <h2>E) Primeiro Registo em Formato JSON</h2>
        <pre>{json.dumps(resultados_e, indent=2, ensure_ascii=False)}</pre>
    </body>
    </html>
    """

    with open("index.html", "wt", encoding="utf-8") as f:
        f.write(html)

processar_e_gerar_html()
print("Página HTML gerada com sucesso!")

# Explicação do código HTML
#   - Definimos a variável html como uma f-string, para permitir que inclua variáveis python dentro da string usando {}.
#   - A parte inicial <!DOCTYPE html> indica que o documento é um HTML5.
#   - Define a linguagem do documento como português, o que pode ajudar os navegadores e motores de busca a entender melhor o conteúdo.
#   - A tag <head> contém metadados e informações que não são exibidas diretamente no corpo da página.
#   - <meta charset="UTF-8"> define a codificação de caracteres como UTF-8, garantindo que caracteres especiais, como acentos, sejam exibidos corretamente.
#   - <meta name="viewport" content="width=device-width, initial-scale=1.0"> assegura que a página seja responsiva, ou seja, que ela seja visualizada corretamente em diferentes aparelhos, ajustando a largura do layout para o tamanho do ecrã.
#   - <title> define o título da página que aparece na tab do navegador.
#   - Dentro da tag <style>, temos as regras CSS que definem o estilo da página:
#       - body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }: define a fonte do corpo do texto como "Arial" (ou uma fonte padrão sem serifa), aumenta o espaçamento entre linhas (line-height: 1.6) para melhor legibilidade e aplica um preenchimento de 20 pixels ao redor do conteúdo.
#       - h1 { color: #333; }: define a cor do título de nível 1 (H1) com um tom escuro de cinza (#333).
#       - h2 { color: #666; }: define a cor dos títulos de nível 2 (H2) com um tom mais claro de cinza (#666).
#       - pre { background-color: #f4f4f4; padding: 10px; border-radius: 5px; }: formata as tags <pre> (que exibem código ou texto pré-formatado) com um fundo claro, preenchimento interno de 10 pixels e cantos arredondados.
#   - A tag <body> define o conteúdo visível da página.
#   - <h1> insere o título principal da página.
#   - O subtítulo <h2> indica que esta é a primeira seção do relatório ("A) Frequência de Processos por Ano").
#   - A tag <pre> exibe o conteúdo pré-formatado, mantendo os espaços e quebras de linha. Dentro dessa tag, o conteúdo da variável resultados_a (um dicionário Python) é convertido para JSON utilizando a função json.dumps(), que formata o dicionário em um formato legível.
#   - etc.
#   - As tags </body> e </html> fecham o documento HTML.