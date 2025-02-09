import tweepy
from dotenv import load_dotenv
import os
import pandas as pd
import time
import datetime

hora = datetime.datetime.now().time()

load_dotenv()

# Configurações de autenticação (mantidas como no original)
consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')
access_token = os.getenv('ACCESS_TOKEN')
access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')
bearer_token = os.getenv('BEARER_TOKEN')

auth = tweepy.OAuth1UserHandler(
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)

api = tweepy.API(auth)

client = tweepy.Client(
    bearer_token,
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)

MODO_TESTE = False  # Altere para False para publicar

def post_from_dataframe(df, path_csv):
    # Garante a coluna 'posted'
    if 'posted' not in df:
        df['posted'] = False
    
    # Reinicia e embaralha se todas estiverem publicadas
    if df['posted'].all():
        df['posted'] = False
        df = df.sample(frac=1).reset_index(drop=True)
        df.to_csv(path_csv, index=False)  # Salva o novo estado
    
    # Seleciona uma postagem não publicada
    postagem = df[df['posted'] == False].sample(n=1)
    
    if postagem.empty:
        print("Nenhuma postagem restante.")
        return
    
    index = postagem.index[0]
    row = postagem.iloc[0]
    
    midia_ids = []
    textpost = ''
    
    # Processa mídia
    if 'media_path' in row and pd.notna(row['media_path']):
        try:
            midia = api.media_upload(row['media_path'])
            midia_ids.append(midia.media_id)
        except Exception as e:
            print(f"Erro ao carregar mídia: {e}")
            return
    
    # Processa texto
    if 'tweet_text' in row and pd.notna(row['tweet_text']):
        textpost = row['tweet_text']
    
    # Publica (ou simula)
    if MODO_TESTE:
        print(f"[MODO TESTE] Tweet: {textpost}")
        print(f"Mídias: {midia_ids}")
    else:
        try:
            response = client.create_tweet(text=textpost, media_ids=midia_ids)
            print(f"Tweet publicado: {response.data['id']}")
        except tweepy.TweepyException as e:
            print(f"Erro ao publicar: {e}")
            return
    
    # Atualiza e salva o DataFrame
    df.loc[index, 'posted'] = True
    df.to_csv(path_csv, index=False)

df = pd.read_csv('produtos - Página1.csv')

# Loop principal
while True:
    if hora > datetime.time(9) and hora < datetime.time(22):
        post_from_dataframe(df=df, path_csv='produtos - Página1.csv')
        time.sleep(10)  # Verifica a cada X segundo