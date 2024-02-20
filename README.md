# News Handler

## Sobre este aplicativo
<p>Este projeto é uma Api de um projeto que complementa outro projeto do meu Github, este aplicativo coletava informações do site https://investing.com , e filtrava o mesmo separando pares de moedas e horas, e posteriormente envia-os para outra api que fazia o cadastro e controle das mesmas. </p>

## Requisitos
### Python 3.11

## Instalação e configuração
Para instalar as dependências do projeto, execute o seguinte comando:

    pip install -r requirements.txt

Antes de executar a aplicação, é necessário criar as seguintes variáveis de ambiente:

<ul>
<li> DB_HOST: endereço do banco de dados </li>
<li> DB_NAME: nome do banco de dados </li>
<li> DB_PORT: porta do banco de dados </li>
<li> DB_USER: usuário do banco de dados </li>
<li> DB_PASSWORD: senha do usuário do banco de dados </li>
<li>API_USER: Usuário para rotas sem JWT</li>
<li>API_PASS:Senha para rotas sem JWT</li>
</ul>

Essas variáveis podem ser definidas no arquivo .env, seguindo o exemplo do arquivo .env.example.

## Utilização

### rodar o programa :

uvicorn main:app --reload

---

## About this app
<p>This project is an API that complements another project on my Github. This application collects information from the website https://investing.com, filters it by separating currency pairs and times, and subsequently sends them to another API that handles the registration and control of the data.</p>

## Requirements
### Python 3.11

## Installation and Configuration
To install the project dependencies, execute the following command:

    pip install -r requirements.txt

Before running the application, it is necessary to create the following environment variables:

<ul>
<li>DB_HOST: database address</li>
<li>DB_NAME: database name</li>
<li>DB_PORT: database port</li>
<li>DB_USER: database user</li>
<li>DB_PASSWORD: database user's password</li>
<li>API_USER: User for non JWT routes</li>
<li>API_PASS: Password for non JWT routes</li>
</ul>

These variables can be defined in the .env file, following the example from the .env.example file.

## Usage

### Run the program:

uvicorn main:app --reload
