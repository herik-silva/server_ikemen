# Como Rodar
Instale as dependências do projeto utilizando o comando abaixo 
```
pip install --no-cache-dir -r requirements.txt
``` 
Em seguida, execute as migrations com o comando
```
python manage.py migrate
```
Ao finalizar as migrations, execute o comando para execução do servidor
```
python manage.py runserver
```
#### Observação: É necessário configurar algumas variáveis de ambiente, solicitar arquivo com as ENVS.
O Servidor já se encontra online em [IkemenServer](https://serverikemenstore.onrender.com/).