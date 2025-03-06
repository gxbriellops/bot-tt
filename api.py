import tweepy
import os
import pandas as pd
import time
import datetime
import logging
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("twitter_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("twitter_bot")

class TwitterBot:
    def __init__(self, csv_path, test_mode=False):
        """
        Inicializa o bot do Twitter com configurações e autenticação.
        
        Args:
            csv_path (str): Caminho para o arquivo CSV com postagens
            test_mode (bool): Se True, simula postagens sem publicá-las
        """
        self.csv_path = csv_path
        self.test_mode = test_mode
        self.df = None
        
        # Carrega variáveis de ambiente
        load_dotenv()
        
        # Configuração de autenticação
        self.consumer_key = os.getenv('CONSUMER_KEY')
        self.consumer_secret = os.getenv('CONSUMER_SECRET')
        self.access_token = os.getenv('ACCESS_TOKEN')
        self.access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')
        self.bearer_token = os.getenv('BEARER_TOKEN')
        
        # Verifica se todas as credenciais estão presentes
        if not all([self.consumer_key, self.consumer_secret, self.access_token, 
                   self.access_token_secret, self.bearer_token]):
            raise ValueError("Credenciais de autenticação incompletas no arquivo .env")
            
        # Configura a API do Twitter
        self._setup_twitter_api()
        
        # Carrega o DataFrame
        self._load_dataframe()
    
    def _setup_twitter_api(self):
        """Configura a API do Twitter utilizando as credenciais carregadas."""
        auth = tweepy.OAuth1UserHandler(
            self.consumer_key,
            self.consumer_secret,
            self.access_token,
            self.access_token_secret
        )
        
        self.api = tweepy.API(auth)
        
        self.client = tweepy.Client(
            self.bearer_token,
            self.consumer_key,
            self.consumer_secret,
            self.access_token,
            self.access_token_secret
        )
        
        logger.info("Conexão com a API do Twitter estabelecida")
    
    def _load_dataframe(self):
        """Carrega e prepara o DataFrame com postagens do CSV."""
        try:
            self.df = pd.read_csv(self.csv_path)
            
            # Garante a coluna 'posted'
            if 'posted' not in self.df.columns:
                self.df['posted'] = False
                self._save_dataframe()
                
            logger.info(f"DataFrame carregado com {len(self.df)} postagens")
            logger.info(f"Postagens pendentes: {len(self.df[self.df['posted'] == False])}")
        except Exception as e:
            logger.error(f"Erro ao carregar o DataFrame: {e}")
            raise
    
    def _save_dataframe(self):
        """Salva o DataFrame atualizado para o CSV."""
        try:
            self.df.to_csv(self.csv_path, index=False)
            logger.debug("DataFrame salvo com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar o DataFrame: {e}")
    
    def _reset_if_all_posted(self):
        """Reinicia e embaralha se todas as postagens estiverem publicadas."""
        if self.df['posted'].all():
            logger.info("Todas as postagens foram publicadas. Reiniciando e embaralhando.")
            self.df['posted'] = False
            self.df = self.df.sample(frac=1).reset_index(drop=True)
            self._save_dataframe()
    
    def _upload_media(self, media_path):
        """
        Carrega mídia para o Twitter.
        
        Args:
            media_path (str): Caminho para o arquivo de mídia
            
        Returns:
            int: ID da mídia carregada ou None em caso de erro
        """
        try:
            media = self.api.media_upload(media_path)
            logger.info(f"Mídia carregada: {media_path}")
            return media.media_id
        except Exception as e:
            logger.error(f"Erro ao carregar mídia {media_path}: {e}")
            return None
    
    def post_from_dataframe(self):
        """Seleciona e publica uma postagem não publicada do DataFrame."""
        # Verifica se é necessário reiniciar
        self._reset_if_all_posted()
        
        # Seleciona uma postagem não publicada
        unpublished = self.df[self.df['posted'] == False]
        if unpublished.empty:
            logger.warning("Nenhuma postagem restante.")
            return False
        
        postagem = unpublished.sample(n=1)
        index = postagem.index[0]
        row = postagem.iloc[0]
        
        # Prepara a postagem
        media_ids = []
        text_post = ''
        
        # Processa mídia, se houver
        if 'media_path' in row and pd.notna(row['media_path']):
            media_id = self._upload_media(row['media_path'])
            if media_id:
                media_ids.append(media_id)
            else:
                # Se falhar ao carregar mídia, não prossegue com a postagem
                return False
        
        # Processa texto
        if 'tweet_text' in row and pd.notna(row['tweet_text']):
            text_post = row['tweet_text']
        
        # Publica (ou simula)
        if self.test_mode:
            logger.info(f"[MODO TESTE] Tweet: {text_post}")
            logger.info(f"Mídias: {media_ids}")
            success = True
        else:
            success = self._publish_tweet(text_post, media_ids)
        
        # Atualiza e salva o DataFrame se a publicação foi bem-sucedida
        if success:
            self.df.loc[index, 'posted'] = True
            self._save_dataframe()
            return True
        
        return False
    
    def _publish_tweet(self, text, media_ids):
        """
        Publica um tweet com o texto e mídia fornecidos.
        
        Args:
            text (str): Texto do tweet
            media_ids (list): Lista de IDs de mídia
            
        Returns:
            bool: True se publicado com sucesso, False caso contrário
        """
        try:
            response = self.client.create_tweet(text=text, media_ids=media_ids)
            logger.info(f"Tweet publicado: {response.data['id']}")
            return True
        except tweepy.TweepyException as e:
            logger.error(f"Erro ao publicar tweet: {e}")
            return False
    
    def run(self, interval=3600, start_hour=9, end_hour=22):
        """
        Executa o bot em um loop, publicando em intervalos regulares dentro do horário especificado.
        
        Args:
            interval (int): Intervalo entre publicações em segundos
            start_hour (int): Hora de início (formato 24h)
            end_hour (int): Hora de término (formato 24h)
        """
        logger.info(f"Bot iniciado em {'modo de teste' if self.test_mode else 'modo de produção'}")
        logger.info(f"Intervalo: {interval} segundos, Horário: {start_hour}h-{end_hour}h")
        
        while True:
            now = datetime.datetime.now()
            current_hour = now.hour
            
            # Verifica se está dentro do horário de publicação
            if start_hour <= current_hour < end_hour:
                logger.info(f"Horário atual ({current_hour}h) dentro do período de publicação")
                result = self.post_from_dataframe()
                if result:
                    logger.info(f"Próxima publicação em {interval} segundos")
                else:
                    logger.warning("Falha na publicação, tentando novamente em breve")
            else:
                logger.info(f"Fora do horário de publicação. Aguardando... ({current_hour}h)")
            
            # Aguarda até o próximo ciclo
            time.sleep(interval)


if __name__ == "__main__":
    # Configurações
    CSV_PATH = 'produtos - Página1.csv'
    TEST_MODE = False  # Altere para False para publicar de verdade
    INTERVAL = 3600  # Intervalo em segundos (1 hora)
    START_HOUR = 9  # Hora de início (9h)
    END_HOUR = 22  # Hora de término (22h)
    
    try:
        # Inicializa e executa o bot
        bot = TwitterBot(csv_path=CSV_PATH, test_mode=TEST_MODE)
        bot.run(interval=INTERVAL, start_hour=START_HOUR, end_hour=END_HOUR)
    except KeyboardInterrupt:
        logger.info("Bot interrompido pelo usuário")
    except Exception as e:
        logger.critical(f"Erro crítico: {e}")