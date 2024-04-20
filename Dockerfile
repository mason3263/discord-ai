FROM python

COPY . /app

WORKDIR /app

RUN mkdir data
RUN touch data/guild_list.yaml

RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python3", "src/main.py" ]