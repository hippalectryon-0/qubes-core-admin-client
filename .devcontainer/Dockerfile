FROM fedora:38

RUN dnf install -y \
    python3 \
    python3-pip \
    python3-xlib \
    python3-rpm \
    git \
    make \
    which \
    && dnf clean all

RUN useradd -m -u 1000 -G wheel devcontainer

# Install 'uv'
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /workspace
USER devcontainer
ENV PATH="/home/devcontainer/.local/bin:$PATH"