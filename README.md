# backend_desafio_headers
Desafio da Empresa Headers - 21/02/2025

Para as rotas, vamos assumir que algumas estão disponiveis mesmo sem o usuário estar logado.
Para edição e exclusão de usuários e posts, é checado o JWT do solicitante, e depois se seu tipo (uma abstração, pode ser interpretada também como Role) tem aquela permissão.

A aplicação usou como banco de dados o PostgreSQL no host local. A documentação foi feita com Flasgger.

Para executar: python app/run.py