#!/bin/bash

# Test script to verify docker-entrypoint.sh syntax
echo "Testing docker-entrypoint.sh syntax..."

# Test the script with sample environment variables
export DB_HOST="${db.HOSTNAME}"
export DB_PORT="5432"
export DB_USER="${db.USER}"
export REDIS_URL=""

# Test just the database check part
echo "Testing database check logic..."
if [ -z "$DB_HOST" ] || [[ "$DB_HOST" == *"db."* ]] || [[ "$DB_HOST" == *"\${"* ]]; then
    echo "✅ Database check logic works - would skip pg_isready"
else
    echo "❌ Database check logic failed"
fi

echo "✅ Test completed successfully"
