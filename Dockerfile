FROM python:3.12-slim-bookworm

ENV URL=""
ENV ENCRYPT_KEY="fiBL_VPMpCfGmpcjYZKqcwGzvyXFcWXccFRI4nKErHw="
ENV LOCAL_SERVER=""

WORKDIR /app

COPY ./app /app

RUN pip install --no-cache-dir --upgrade -r /app/r.txt

EXPOSE 8000

CMD ["fastapi", "run", "main.py", "--port", "8000", "--no-reload", "--proxy-headers" ]