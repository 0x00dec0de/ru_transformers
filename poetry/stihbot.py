from tendo import singleton
me = singleton.SingleInstance()

import logging

logging.basicConfig(filename="stihbot.log", level=logging.INFO)
logger = logging.getLogger(__name__)

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from run_generation import sample_sequence
from sp_encoder import SPEncoder
from transformers import GPT2LMHeadModel
import threading
import regex as re

device="cuda"
path = 'output_poet'

lock = threading.RLock()

def get_sample(prompt, model, tokenizer, device):
    logger.info("*" * 200)
    logger.info(prompt)

    model.to(device)
    model.eval()
    
    filter_n = tokenizer.encode('\n')[-1:]
    context_tokens = tokenizer.encode(prompt)
    out = sample_sequence(
        model=model,
        context=context_tokens,
        length=150,
        temperature=1,
        top_k=0,
        top_p=0.9,
        device=device,
        filter_double=filter_n
    )
    out = out[0, len(context_tokens):].tolist()
    text = tokenizer.decode(out)
    result = re.match(r'[\w\W]*[\.!?]\n', text) 
    if result: text = result[0] 
    logger.info("=" * 200)
    logger.info(text)
    return text

tokenizer = SPEncoder.from_pretrained(path)

model = GPT2LMHeadModel.from_pretrained(path)
model.to(device)
model.eval()

import json
data = json.load(open('config.json'))

from tendo import singleton
me = singleton.SingleInstance()

import os
os.environ["CUDA_VISIBLE_DEVICES"]="0"

import telebot

bot = telebot.TeleBot(data['bot_key'])

from telebot import apihelper

apihelper.proxy = {'https':data['proxy_str']}

def message_handler(message):
    logger.info(message.from_user)
    with lock:
        try:
            bot.reply_to(message, get_sample(message.text, model, tokenizer, device))
        except telebot.apihelper.ApiException as e:
            print(e)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Присылай начало, а я продолжу")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    message_handler(message)

@bot.channel_post_handler(func=lambda m: True)
def echo_all(message):
    message_handler(message)

bot.polling()


