# syntax=docker/dockerfile:1
FROM ubuntu:noble AS build

ARG python_version=3.12

SHELL ["/bin/sh", "-exc"]

RUN <<EOF
apt-get update --quiet
apt-get install --quiet --no-install-recommends --assume-yes \
  build-essential \
  libpq-dev \
  "python$python_version-dev"
EOF

COPY --link --from=ghcr.io/astral-sh/uv:0.4 /uv /usr/local/bin/uv

ENV UV_PYTHON="python$python_version" \
  UV_PYTHON_DOWNLOADS=never \
  UV_PROJECT_ENVIRONMENT=/app \
  UV_LINK_MODE=copy \
  UV_COMPILE_BYTECODE=1 \
  PYTHONOPTIMIZE=1

COPY pyproject.toml uv.lock* /_project/

RUN --mount=type=cache,destination=/root/.cache/uv <<EOF
cd /_project
uv sync \
  --no-dev \
  --no-install-project \
  --frozen
EOF

ENV UV_PYTHON=$UV_PROJECT_ENVIRONMENT

COPY src/ /_project/src

RUN --mount=type=cache,destination=/root/.cache/uv <<EOF
cd /_project
uv pip install . --no-deps --no-cache
EOF

FROM ubuntu:noble AS final

ARG user_id=1000
ARG group_id=1000
ARG python_version=3.12

ENTRYPOINT ["/docker-entrypoint.sh"]
STOPSIGNAL SIGINT
EXPOSE 8000/tcp

SHELL ["/bin/sh", "-exc"]

COPY --link --from=ghcr.io/astral-sh/uv:0.4 /uv /usr/local/bin/uv

RUN <<EOF
[ $user_id -gt 0 ] && user="$(id --name --user $user_id 2> /dev/null)" && userdel "$user"

if [ $group_id -gt 0 ]; then
  group="$(id --name --group $group_id 2> /dev/null)" && groupdel "$group"
  groupadd --gid $group_id app
fi

[ $user_id -gt 0 ] && useradd --uid $user_id --gid $group_id --home-dir /app app
EOF

RUN <<EOF
apt-get update --quiet
apt-get install --quiet --no-install-recommends --assume-yes \
  libpq5 \
  "python$python_version"
rm -rf /var/lib/apt/lists/*
EOF

ENV PATH=/app/bin:$PATH \
  PYTHONOPTIMIZE=1 \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1

COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

COPY --link --chown=$user_id:$group_id --from=build /app/ /app

USER $user_id:$group_id
WORKDIR /app

RUN <<EOF
python --version
python -I -m site
echo "Listing site-packages content:"
ls -l /app/lib/python${python_version}/site-packages/
echo "Trying to import url_alias..."
python -I -c 'import url_alias'
EOF