FROM python:3.9

RUN mkdir -p /usr/app/learn_tg_bot/
WORKDIR /usr/app/learn_tg_bot/

COPY . /usr/app/learn_tg_bot/
RUN ls \
&& pip install --no-cache-dir -r requirements.txt

CMD ["python3", "bot_project_new/bot.py"]