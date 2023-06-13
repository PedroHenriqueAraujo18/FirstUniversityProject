from flask import Flask, request, render_template, url_for, redirect
import oracledb
import numpy as np
app = Flask(__name__)

#pega a quantidade de amostra
def obter_quantidade_amostras():
    
    try:
        connection = obter_conexao()
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM QUALIDADE_DO_AR")
        quantidade_amostras = cursor.fetchone()
        cursor.close()
        return quantidade_amostras
    except:
        return 'Sem amostras no banco'
        
#mostra as amostras no html
def mostrar_amostras():
    try:
        connection = obter_conexao()
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT * FROM QUALIDADE_DO_AR")
        amostras = cursor.fetchall()
        cursor.close()
        return amostras
    except:
        return 'Nenhuma amostra foi encontrada'

def generate_key_matrix():
    key_matrix = np.random.randint(0, 26, (2, 2))
    return key_matrix

def hill_cipher_2x2(matrix, text):
    if matrix.shape != (2, 2):
        raise ValueError("A matriz deve ser 2x2.")

    text = text.upper().replace(" ", "")
    if len(text) % 2 != 0:
        text += "X"

    letter_to_number = {chr(i + 65): i for i in range(26)}
    number_to_letter = {i: chr(i + 65) for i in range(26)}

    encrypted_text = ""

    for i in range(0, len(text), 2):
        pair = text[i:i+2]
        pair_numbers = [letter_to_number.get(char, 0) for char in pair]  # Usa o valor 0 para caracteres não encontrados
        result = np.matmul(matrix, pair_numbers) % 26
        encrypted_pair = "".join([number_to_letter[num] for num in result])
        encrypted_text += encrypted_pair

    return encrypted_text

@app.route('/criptografia',methods=['GET'])
def criptografia():
    connection = obter_conexao()
    cursor = connection.cursor()
    
    if request.method =='GET':
        cursor.execute('SELECT * FROM QUALIDADE_DO_AR')
        data = cursor.fetchone()

        key_matrix = generate_key_matrix()

        dados_criptografados = [hill_cipher_2x2(key_matrix, str(x)) for x in data]
        return render_template('criptografia.html', dadosCriptografados=dados_criptografados)
    return'erro'
      
def obter_conexao():
    connection = oracledb.connect(
        user="SYSTEM",
        password="pedro",
        dsn="localhost/xe"
    )
    return connection

@app.route('/')
def index():
    connection = obter_conexao()
    cursor = connection.cursor()
   
    return render_template('index.html')

@app.route('/Sair')
def sair():
    return render_template('sair.html')
    
        
@app.route('/Sobre')
def sobre():
    return render_template('Sobre.html')

@app.route('/Cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        try:
            connection = obter_conexao()
            cursor = connection.cursor()

            mp10 = request.form['mp10']
            mp25 = request.form['mp25']
            o3 = request.form['o3']
            co = request.form['co']
            no2 = request.form['no2']
            so2 = request.form['so2']

            cursor.execute("INSERT INTO QUALIDADE_DO_AR (MP10, MP2_5, O3, CO, NO2, SO2) VALUES (:mp10, :mp25, :o3, :co, :no2, :so2)",
                           (mp10, mp25, o3, co, no2, so2))
            
            connection.commit()
            cursor.close()

            #return f"MP10: {mp10}<br>MP2.5: {mp25}<br>O3: {o3}<br>CO: {co}<br>NO2: {no2}<br>SO2: {so2}"
            return render_template('Cadastrar.html')
        except oracledb.Error as error:
            return "Erro ao cadastrar"
    return render_template('Cadastrar.html')


@app.route('/alterar', methods=['GET', 'POST'])
def alterar():
    if request.method == 'GET':
        try:
            connection = obter_conexao()
            cursor = connection.cursor()

            # Obtém o ID do item a ser alterado
            id_item = request.args.get('id')
            if id_item:
                # Executa o comando SELECT para recuperar os dados do item
                cursor.execute("SELECT * FROM QUALIDADE_DO_AR WHERE ID = :id", {'id': id_item})
                item = cursor.fetchone()
                cursor.close()

                # Renderiza o template para atualizar os dados do item
                return render_template('formAlterar.html', item=item)
            else:
                # Executa o comando SELECT para recuperar os dados de todos os itens
                cursor.execute("SELECT * FROM QUALIDADE_DO_AR")
                items = cursor.fetchall()
                cursor.close()

                # Renderiza o template para exibir todos os itens
                return render_template('alterar.html', items=items)

        except oracledb.Error as error:
            return "Erro ao exibir o alteração."
        
    elif request.method == 'POST':
        try:
            connection = obter_conexao()
            cursor = connection.cursor()

            # Obtém os valores atualizados do formulário
            id = request.form.get('id')
            mp10 = request.form.get('mp10')
            mp25 = request.form.get('mp25')
            o3 = request.form.get('o3')
            co = request.form.get('co')
            no2 = request.form.get('no2')
            so2 = request.form.get('so2')

            # Executa o comando UPDATE para atualizar os dados do item
            cursor.execute("UPDATE QUALIDADE_DO_AR SET MP10=:mp10, MP2_5=:mp2_5, O3=:o3, CO=:co, NO2=:no2, SO2=:so2 WHERE ID=:id",
                           {'mp10': mp10, 'mp2_5': mp25, 'o3': o3, 'co': co, 'no2': no2, 'so2': so2, 'id': id})
            connection.commit()
            cursor.close()

            # Renderiza o template para confirmar que os dados foram atualizados
            return render_template('formAlterar.html', item=(id, mp10, mp25, o3, co, no2, so2))

        except oracledb.Error as error:
            return "Erro ao atualizar a amostra."

    # Return a default response if no other response has been returned
    return "Invalid request method"

@app.route('/classificacao', methods=['GET'])
def classificacao():
    quantidade_amostras = obter_quantidade_amostras()
    tabelas = mostrar_amostras()
    classificacao={}
    if request.method == 'GET':
        try:
            connection = obter_conexao()
            cursor = connection.cursor()
            resultados=request.form.get('id')
            cursor.execute('SELECT ID FROM  QUALIDADE_DO_AR')
            resultados=cursor.fetchall()
            for resultado in resultados:
                # Get the sample ID from the result
                sample_id = resultado[0]
                
                # Use the sample ID as needed
            data = list(zip(resultados, tabelas))   
                
            cursor.execute('SELECT AVG(MP10), AVG(MP2_5), AVG(O3), AVG(NO2), AVG(CO), AVG(SO2) FROM QUALIDADE_DO_AR')
            resultado = cursor.fetchone()
            classificacao ={}
            if resultado is not None:
                MP10, MP25, O3, SO2, CO, NO2 = resultado

            if (MP10 > 250) or (MP25 > 125) or (O3 > 200) or (SO2 > 800) or (NO2 > 1130) or (CO > 15):
                classificacao = {
                "qualidade_ar": "Péssima",
                "efeitos_saude": "Toda a população pode apresentar sérios riscos de manifestações de doenças respiratórias e cardiovasculares. Aumento de mortes prematuras em pessoas de grupos sensíveis."
                    }
            elif (MP10 > 150 and MP10 <= 250) or (MP25 > 75 and MP25 <= 125) or (O3 > 160 and O3 <= 200) or (SO2 > 365 and SO2 <= 800) or (NO2 > 320 and NO2 <= 1130) or (CO > 13 and CO <= 15) or (SO2 > 40 and SO2 <= 365):
                classificacao = {
                    "qualidade_ar": "Muito Ruim",
                    "efeitos_saude": "Toda a população pode apresentar agravamento dos sintomas como tosse seca, cansaço, ardor nos olhos, nariz e garganta, e ainda falta de ar e respiração ofegante. Efeitos ainda mais graves na saúde de grupos sensíveis (crianças, idosos e pessoas com doenças respiratórias)."
                    }
            elif (MP10 > 100 and MP10 <= 150) or (MP25 > 50 and MP25 <= 75) or (O3 > 130 and O3 <= 160) or (NO2 > 240 and NO2 <= 320) or (CO > 11 and CO <= 13) or (SO2 > 20 and SO2 <= 40):
                classificacao = {
                    "qualidade_ar": "Ruim",
                    "efeitos_saude": "Toda a população pode apresentar sintomas como tosse seca, cansaço, ardor nos olhos, nariz e garganta. Pessoas de grupos sensíveis (crianças, idosos e pessoas com doenças respiratórias e cardíacas) podem apresentar efeitos mais sérios na saúde."
                     }
            elif (MP10 > 50 and MP10 <= 100) or (MP25 > 25 and MP25 <= 50) or (O3 > 100 and O3 <= 130) or (NO2 > 200 and NO2 <= 240) or (CO > 9 and CO <= 11) or (SO2 >= 0 and SO2 <= 20):
                classificacao = {
                "qualidade_ar": "Moderada",
                "efeitos_saude": "Pessoas de grupos sensíveis (crianças, idosos e pessoas com doenças respiratórias e cardíacas) podem apresentar sintomas como tosse seca e cansaço. A população, em geral, não é afetada."
                }
            else:
                classificacao = {
                "qualidade_ar": "Boa"
                }   
        except:
            return "ERROR"    
        
    #Não retorna o valor classificacao.qualidade_ar 
    return render_template('Classificacao.html',classificacao=classificacao,quantidade_amostras=quantidade_amostras, tabelas=tabelas,resultado=resultado,sample_ids=resultados,data=data)

@app.route('/excluir', methods=['GET', 'POST'])
def excluir(): #Erro de int, verificar conversão de valores
    if request.method == 'POST':
        try:
            # Conexão com o banco de dados e cursor
            connection = obter_conexao()
            cursor = connection.cursor()

            # Obtém o ID do item a ser excluído
            id_item = request.form.get('id')

            # Executa o comando DELETE
            cursor.execute("DELETE FROM QUALIDADE_DO_AR WHERE id = :id", {'id': id_item})
            connection.commit()
            cursor.close()

            # Redireciona para a página de excluir após a exclusão bem-sucedida
            return redirect(url_for('excluir'))

        except oracledb.Error as error:
            return "Erro ao excluir o item."

    # Buscar os dados das amostras do banco de dados
    try:
        connection = obter_conexao()
        cursor = connection.cursor()

        # Executar a consulta para obter as amostras
        cursor.execute("SELECT ID, MP10, MP2_5, O3, CO, NO2, SO2 FROM QUALIDADE_DO_AR")

        # Obter todas as linhas de resultados
        amostras = cursor.fetchall()

        cursor.close()

    except oracledb.Error as error:
        return "Erro ao buscar as amostras."

    return render_template('Excluir.html', amostras=amostras)
  
if __name__ == '__main__':
    app.run(debug=True)
    


