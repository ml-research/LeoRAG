FROM nvcr.io/nvidia/pytorch:23.10-py3
RUN apt-get update
RUN apt-get install -y zsh
RUN wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true
WORKDIR /workspace/Verba
ENV PYTHONPATH "${PYTHONPATH}:./"
RUN DEBIAN_FRONTEND=noninteractive pip uninstall torchtext torchdata transformer-engine -y
RUN DEBIAN_FRONTEND=noninteractive pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu118
RUN DEBIAN_FRONTEND=noninteractive pip uninstall flash-attn -y
RUN DEBIAN_FRONTEND=noninteractive pip install flash-attn