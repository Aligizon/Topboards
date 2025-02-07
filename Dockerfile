FROM python:3.12.2-slim

WORKDIR /website

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . . 

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "website.main:app", "--bind", "0.0.0.0:8000"]
# CMD [ "python",  "-m", "website.main"]