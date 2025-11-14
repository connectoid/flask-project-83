curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

make install && make update-requirements && psql -a -d $DATABASE_URL -f database.sql