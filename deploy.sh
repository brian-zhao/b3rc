#!/bin/bash
# Deploy to GAE, merging secrets from app.secrets.yaml into app.yaml
set -e

if [ ! -f app.secrets.yaml ]; then
    echo "ERROR: app.secrets.yaml not found. Create it with your secrets."
    exit 1
fi

# Build merged app.yaml with secrets
python3 -c "
import yaml, sys

with open('app.yaml') as f:
    app = yaml.safe_load(f)
with open('app.secrets.yaml') as f:
    secrets = yaml.safe_load(f)

app['env_variables'].update(secrets.get('env_variables', {}))

with open('/tmp/app-deploy.yaml', 'w') as f:
    yaml.dump(app, f, default_flow_style=False, sort_keys=False)
"

echo "Deploying with merged secrets..."
gcloud app deploy /tmp/app-deploy.yaml --project=b3rc-467810 --quiet
rm /tmp/app-deploy.yaml
echo "Done!"
