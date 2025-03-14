import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

TOKEN = "7885984369:AAE_P3HvYvbL-_QQxdwCI6c7UDCFnTBX__E"
DESTINO_CHAT_ID = 2006153630

# verificação do formato correto
async def verificar_formato_imagem(update: Update, context: CallbackContext):
    mensagem = update.message
    if not mensagem.photo:
        return

    foto = mensagem.photo[-1]
    
    largura = foto.width
    altura = foto.height
    proporcao = largura / altura
    
    tolerancia_3_4 = (0.74, 0.76)  # 3:4
    tolerancia_16_9 = (1.76, 1.78)  # 16:9
    
    if tolerancia_3_4[0] <= proporcao <= tolerancia_3_4[1]:
        return "3:4"

    elif tolerancia_16_9[0] <= proporcao <= tolerancia_16_9[1]:
        return "16:9"
    else:
        return "formato não suportado"

def verificar_formato(legenda, formato_imagem):
    if formato_imagem == "3:4":
        padrao = r"^[A-Za-z0-9À-ÿ\s]+,\s[A-Za-z0-9À-ÿ\s]+,\s[A-Za-z0-9À-ÿ\s]+,\s[A-Za-z0-9À-ÿ\s]+,\s[A-Za-z0-9À-ÿ\s]+$"
    elif formato_imagem == "16:9":
        padrao = r"^Banner,\s[A-Za-z0-9À-ÿ\s]+$"
    else:
        return False
    
    return bool(re.match(padrao, legenda))

# comandos e envio de imagens
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("🍥 Este é o Nekorin add, o bot responsável pelas adições do Nekorin! Para fazer seu pedido me envie as imagens seguindo as descrições previstas pelo comando */info*", parse_mode="Markdown")

async def info(update: Update, context: CallbackContext):
    mensagem = "📌 Opa! Precisa de ajuda? Aqui está um modelo de como enviar seu pedido:\n" +\
    "*Categoria, Tag, Nome, Raridade, Coleção*" +\
    "\n\nLembrando que se o pedido for enviado no formato incorreto ele não será processado pelo bot" +\
    "\n\n📍Imagens de integrante: *3:4*\n📍Imagens para banner de grupo ou tag: *16:9*" +\
    "\n\n*O pedido deve ser feito com as imagens em si, pedidos feitos em arquivo não serão processados pelo bot.*"
    await update.message.reply_photo(
        photo="https://i.ibb.co/bgmSHbv4/example.jpg", 
        caption=f"{mensagem}",
        parse_mode="Markdown"
    )

async def receber_imagem(update: Update, context: CallbackContext):
    mensagem = update.message
    if not mensagem.photo:
        return

    foto = mensagem.photo[-1]
    
    formato_imagem = await verificar_formato_imagem(update, context)
    
    if formato_imagem == "formato não suportado":
        await update.message.reply_text(
            "❗️ Ops! A imagem não está nos formatos 3:4 ou 16:9. Por favor, envie uma imagem nos formatos suportados."
        )
        return

    legenda = mensagem.caption if mensagem.caption else "(Sem legenda)"

    if not verificar_formato(legenda, formato_imagem):
        if formato_imagem == "3:4":
            mensagem_erro = "❗️ Ops! Parece que a legenda está no formato incorreto... Verifique o formato da legenda para Integrante em */info*"
        else:  
            mensagem_erro = "❗️ Ops! Parece que a legenda está no formato incorreto... Verifique o formato da legenda para Banner em */info*"

        await update.message.reply_text(mensagem_erro, parse_mode="Markdown")
        return

    # encaminha para o mod
    await context.bot.send_photo(chat_id=DESTINO_CHAT_ID, photo=foto.file_id, caption=f"{legenda}")

async def error_handler(update: object, context: CallbackContext):
    print(f"Ocorreu um erro: {context.error}")
    await update.message.reply_text("❗️ Parece que ocorreu um erro! Tente novamente.")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex(r"^\.start\b"), start))  

    app.add_handler(CommandHandler("info", info))
    app.add_handler(MessageHandler(filters.Regex(r"^\.info\b"), info))  

    app.add_handler(MessageHandler(filters.PHOTO, receber_imagem))

    app.add_error_handler(error_handler)

    print("🤖 NekoaddBot rodando...")
    app.run_polling()

if __name__ == "__main__":
    main()
