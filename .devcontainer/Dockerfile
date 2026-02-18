# FROM fedora:38  # will switch when tests pass for 3.12
#FROM fedora:40
FROM registry.gitlab.com/qubesos/docker-images/qubesos-ci:latest

RUN sudo dnf install -y \
    openssl \
    python3-rpm \
    sequoia-sqv \
    python3-xlib \
    libnotify \
    zstd \
    xorg-x11-server-Xvfb \
    && sudo dnf clean all

USER root

# uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

#user config (rootnopwd)
RUN useradd -m -u 1000 -G wheel devcontainer
RUN echo '%devcontainer ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/devcontainer-nopasswd && \
    chmod 0440 /etc/sudoers.d/devcontainer-nopasswd

WORKDIR /workspace
USER devcontainer
ENV PATH=$HOME/.local/bin:$PATH
ENV ENABLE_SLOW_TESTS=1
#COPY --chown=devcontainer:devcontainer . /workspace