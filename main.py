from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama
from qdrant_client import QdrantClient
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain.schema.runnable import RunnablePassthrough 
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.chains import LLMChain
from prompt import chain_type_kwargs

import asyncio 
import logging 
import sys 

from aiogram import Bot, Dispatcher, types 
from aiogram.enums import ParseMode 
from aiogram.filters import CommandStart 
from aiogram.types import Message 
from aiogram.utils.markdown import hbold

# Bot token can be obtained via https://t.me/BotFather, nom = @Camer_bot
TOKEN = "6831145979:AAGcy6NzHxV_2TLbN2dtLhAGIeCaeeWHR9w"
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

class Chat:
    def __init__(self):
        self.model = Ollama(base_url = 'http://192.168.71.5:11434',model="mistral:instruct")
        self.engine = None
        self.collection = None
        self.client = None

    def ask(self, query: str):
        self.client = QdrantClient(host="localhost", port=6333)
        search_result = self.client.query(
            collection_name="demo_collection",
            query_text=query
        )

        def concate_(n):
            search_result_conca = ''
            for x in range(n):
                txt = search_result[x].metadata['document'][search_result[x].metadata['document'].find('reponse'):search_result[x].metadata['document'].find('date')]
                search_result_conca += txt + " "
            return search_result_conca

        search_result_concat = concate_(3)
        prompts = f"""
            **Instructions:**
            Question: {query}
            Reponses: {search_result_concat.replace("https://", "")}
        """
        return self.model.invoke(prompts)

    def clear(self):
        if self.client:
            del self.client
            self.client = None
        if self.collection:
            del self.collection
            self.collection = None

chat = Chat()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")

@dp.message()
async def echo_handler(message: types.Message) -> None:
    message_wait = await bot.send_message(chat_id=message.chat.id, text="Traitement en cours...")

    # Variable pour le prompt
    message_prompt = message.text

    response = None
    attempts = 0
    max_attempts = 5
    delay = 1

    while attempts < max_attempts:
        try:
            response = chat.ask(message_prompt)
            break
        except Exception as e:
            logging.warning(f"Attempt {attempts+1} failed: {e}")
            attempts += 1
            await asyncio.sleep(delay)
            delay *= 2  # Double the delay each retry

    # Effacer "traitement en cours"
    await bot.delete_message(chat_id=message.chat.id, message_id=message_wait.message_id)

    # Afficher la réponse dans Telegram
    if response:
        await message.answer(response)
    else:
        await message.answer("Désolé, je n'ai pas pu traiter votre demande. Veuillez réessayer plus tard.")

async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
