import twikit
import asyncio
import pandas as pd

class TwitterBot:
    def __init__(self, username, email, password):
        self.client = twikit.Client(language='pt-BR')
        self.username = username
        self.email = email
        self.password = password

    async def login(self):
        await self.client.login(
            auth_info_1=self.username,
            auth_info_2=self.email,
            password=self.password
        )

    async def post_from_dataframe(self, csv_path):
        # Lê o CSV com conteúdo para postagens
        df = pd.read_csv(csv_path)
        
        # Login
        await self.login()
        
        # Itera sobre as linhas do DataFrame
        for index, row in df.iterrows():
            try:
                # Verifica se há mídia para upload
                media_ids = []
                if 'media_path' in row and pd.notna(row['media_path']):
                    media_ids = [await self.client.upload_media(row['media_path'])]
                
                # Cria o tweet
                await self.client.create_tweet(
                    text=row['tweet_text'],
                    media_ids=media_ids
                )
                print(f"Tweet {index + 1} postado com sucesso!")
                
                # Opcional: adicionar delay entre posts para evitar rate limiting
                await asyncio.sleep(60)  # 1 minuto entre posts
                
            except Exception as e:
                print(f"Erro ao postar tweet {index + 1}: {e}")

# Exemplo de uso
async def main():
    bot = TwitterBot(
        username='CapocciLea77927', 
        email='capoccileandro@gmail.com', 
        password='Aeiou8734%'
    )
    await bot.post_from_dataframe('produtos - Página1.csv')

asyncio.run(main())