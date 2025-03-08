# Bot de Promoções da Amazon - Readme

## Descrição do Projeto

Este projeto consiste em um bot automatizado para Twitter que publica promoções de produtos da Amazon Brasil. O sistema é composto por duas partes principais:

1. **Webscraping de Produtos**: Um script que coleta automaticamente produtos populares da Amazon, incluindo informações como nome, preço, avaliações e imagens.

2. **Bot do Twitter**: Um sistema automatizado que publica tweets sobre os produtos coletados, em intervalos regulares, incluindo imagens e links para os produtos.

## Estrutura do Projeto

- **webscrapping.ipynb**: Notebook Jupyter para coletar produtos da Amazon
- **api.py**: Módulo principal que gerencia a publicação de tweets
- **.env**: Arquivo com as credenciais de autenticação da API do Twitter
- **produtos - Página1.csv**: Banco de dados de produtos coletados
- **media/**: Diretório que armazena as imagens dos produtos

## Funcionalidades

- Scraping automatizado dos produtos mais vendidos da Amazon Brasil
- Geração de mensagens personalizadas para cada produto
- Sistema de postagem com intervalo configurável
- Postagem apenas em horários específicos
- Controle de produtos já publicados
- Rotação automática e reembaralhamento da lista quando todos os produtos forem publicados
- Sistema completo de logging

## Requisitos

- Python 3.x
- Bibliotecas Python:
  - tweepy
  - pandas
  - python-dotenv
  - selenium (para webscraping)
  - requests

## Configuração

1. Clone o repositório
2. Instale as dependências:
   ```
   pip install tweepy pandas python-dotenv selenium requests
   ```
3. Configure suas credenciais do Twitter no arquivo `.env`:
   ```
   CONSUMER_KEY = 'sua consumer key'
   CONSUMER_SECRET = 'sua consumer secret'
   ACCESS_TOKEN = 'seu token de acesso'
   ACCESS_TOKEN_SECRET = 'seu token de acesso secreto'
   BEARER_TOKEN = 'seu bearer token'
   ```
4. Execute o notebook `webscrapping.ipynb` para coletar produtos (ou utilize o arquivo CSV já existente)
5. Execute o bot com:
   ```
   python api.py
   ```

## Uso do Bot

- O bot é configurado para operar entre 9h e 22h (configurável)
- Por padrão, publica um tweet a cada hora
- Para usar em modo de teste (sem publicar tweets reais), defina `TEST_MODE = True` no código

## Personalização

- **Intervalo de Postagem**: Modifique a variável `INTERVAL` (em segundos)
- **Horário de Funcionamento**: Ajuste `START_HOUR` e `END_HOUR`
- **Formato das Mensagens**: O script de webscraping gera mensagens variadas para cada produto

## Logs

O sistema registra todas as operações no arquivo `twitter_bot.log` e também exibe logs no console durante a execução. Isto facilita o monitoramento do funcionamento do bot e a identificação de possíveis problemas.

## Notas de Segurança

- Nunca compartilhe suas credenciais de API do Twitter
- O arquivo `.env` já está incluído no `.gitignore` para evitar exposição acidental
- Certifique-se de seguir as políticas do Twitter para bots automatizados

## Exemplo de Uso

```python
# Inicialização básica do bot
bot = TwitterBot(csv_path='produtos - Página1.csv', test_mode=False)
bot.run(interval=3600, start_hour=9, end_hour=22)
```

## Futuras Atualizações

- Implementação de análise de sentimento para filtrar produtos com avaliações negativas
- Sistema de detecção de preços com desconto real
- Integração com outras plataformas além do Twitter
- Interface web para monitoramento e controle do bot

---

Desenvolvido com ❤️ para compartilhar as melhores ofertas da Amazon Brasil
