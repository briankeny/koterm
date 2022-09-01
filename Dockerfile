FROM python:3
ADD koterm.py /
RUN pip install argparse colorama requests
ENTRYPOINT ["python", "./koterm.py" ]

