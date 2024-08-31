.PHONY: stop

# Default target
all:
	@echo "Please choose your target!"
	exit 1

# Run the auth.py script
run:
	@echo "PUBLIC_IP_PORT is $$PUBLIC_IP_PORT"
	# Check if the PUBLIC_IP_PORT environment variables are set
	@if [ -z "$${PUBLIC_IP_PORT}" ]; then \
		echo "Error: PUBLIC_IP_PORT environment variable is not set."; \
		exit 1; \
	fi
	# Check if the JACCOUNT_CLIENT_ID environment variables are set
	@if [ -z "$${JACCOUNT_CLIENT_ID}" ]; then \
		echo "Error: JACCOUNT_CLIENT_ID environment variable is not set."; \
		exit 1; \
	fi
	# Check if the JACCOUNT_CLIENT_SECRET environment variables are set
	@if [ -z "$${JACCOUNT_CLIENT_SECRET}" ]; then \
		echo "Error: JACCOUNT_CLIENT_SECRET environment variable is not set."; \
		exit 1; \
	fi
	nohup python3 -u auth.py 2>&1 -d &

# Stop the auth.py script
stop:
	@echo "Stopping auth.py..."
	@-pkill -f 'python3 auth.py'
	@echo "Process stopped."
