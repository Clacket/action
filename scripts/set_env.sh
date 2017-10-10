#! /bin/sh

cat > $1 << EOF
DATABASE_URL="$DATABASE_URL"
FLASK_APP="$FLASK_APP"
SECRET_KEY="$SECRET_KEY"
EOF

echo "Saved env vars in $1"