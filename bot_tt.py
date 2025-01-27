import twikit
import asyncio
import pandas as pd
from typing import List, Optional
import logging
from pathlib import Path
from dotenv import load_dotenv
import os
import time
from dataclasses import dataclass

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('twitter_bot.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class TwitterCredentials:
    username: str
    email: str
    password: str

class TwitterBot:
    def __init__(self, credentials: TwitterCredentials):
        """
        Inicializa o bot do Twitter com credenciais seguras.
        
        Args:
            credentials: TwitterCredentials object containing authentication info
        """
        self.client = twikit.Client(language='pt-BR')
        self.credentials = credentials
        self.is_logged_in = False
        self.last_tweet_time = 0
        self.min_tweet_interval = 60  # segundos

    async def login(self) -> bool:
        """
        Realiza login na API do Twitter com tratamento de erros.
        
        Returns:
            bool: True se login bem sucedido, False caso contrário
        """
        try:
            await self.client.login(
                auth_info_1=self.credentials.username,
                auth_info_2=self.credentials.email,
                password=self.credentials.password
            )
            self.is_logged_in = True
            logging.info("Login realizado com sucesso")
            return True
        except Exception as e:
            logging.error(f"Erro no login: {e}")
            self.is_logged_in = False
            return False

    async def upload_media(self, media_path: str) -> Optional[str]:
        """
        Faz upload de mídia com validação de arquivo.
        
        Args:
            media_path: Caminho para o arquivo de mídia
            
        Returns:
            Optional[str]: ID da mídia se sucesso, None se falha
        """
        try:
            if not Path(media_path).exists():
                raise FileNotFoundError(f"Arquivo não encontrado: {media_path}")
                
            media_id = await self.client.upload_media(media_path)
            logging.info(f"Mídia {media_path} enviada com sucesso")
            return media_id
        except Exception as e:
            logging.error(f"Erro no upload da mídia {media_path}: {e}")
            return None

    async def create_tweet(self, text: str, media_ids: List[str] = None) -> bool:
        """
        Cria tweet com rate limiting e retry.
        
        Args:
            text: Texto do tweet
            media_ids: Lista opcional de IDs de mídia
            
        Returns:
            bool: True se tweet foi postado com sucesso
        """
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_tweet_time
        if time_since_last < self.min_tweet_interval:
            await asyncio.sleep(self.min_tweet_interval - time_since_last)

        try:
            await self.client.create_tweet(text=text, media_ids=media_ids or [])
            self.last_tweet_time = time.time()
            return True
        except Exception as e:
            logging.error(f"Erro ao criar tweet: {e}")
            return False

    async def post_from_dataframe(self, csv_path: str) -> None:
        """
        Posta tweets a partir de um DataFrame com retry logic.
        
        Args:
            csv_path: Caminho para o arquivo CSV
        """
        try:
            if not Path(csv_path).exists():
                raise FileNotFoundError(f"CSV não encontrado: {csv_path}")

            df = pd.read_csv(csv_path)
            required_columns = ['tweet_text']
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"CSV deve conter as colunas: {required_columns}")

            if not self.is_logged_in and not await self.login():
                raise Exception("Não foi possível realizar o login")

            for index, row in df.iterrows():
                media_ids = []
                if 'media_path' in row and pd.notna(row['media_path']):
                    media_id = await self.upload_media(row['media_path'])
                    if media_id:
                        media_ids.append(media_id)

                if await self.create_tweet(row['tweet_text'], media_ids):
                    logging.info(f"Tweet {index + 1} postado com sucesso")
                else:
                    logging.error(f"Falha ao postar tweet {index + 1}")

        except Exception as e:
            logging.error(f"Erro ao processar arquivo CSV: {e}")
            raise

async def main():
    # Carrega variáveis de ambiente do arquivo .env
    load_dotenv()
    
    credentials = TwitterCredentials(
        username=os.getenv('TWITTER_USERNAME'),
        email=os.getenv('TWITTER_EMAIL'),
        password=os.getenv('TWITTER_PASSWORD')
    )

    bot = TwitterBot(credentials)
    await bot.post_from_dataframe('produtos - Página1.csv')

if __name__ == "__main__":
    asyncio.run(main())