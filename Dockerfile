# Use a minimal Python base image
FROM python:3-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Create a non-root user and group
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Set the working directory
WORKDIR /testcases

# Install Python dependencies
COPY requirements.txt .

# Copy the application code
COPY ./nj67-papers/testcases .
COPY ./tester .

# Change ownership of the application files
RUN chown -R appuser:appgroup /testcases

ENV PATH="$PATH:/home/appuser/.local/bin"

# Ensure the test runner script is executable
RUN chmod +x ./tester

# Use a non-root user to run the application
USER appuser

VOLUME ["/testcases/usercode"]

RUN target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Set the entrypoint
ENTRYPOINT ["python", "./tester"]

# for now run with docker run [args] . .

# Note: Resource limits (CPU, memory, pids) should be set at container runtime
# using docker run flags such as --cpus, --memory, --pids-limit, etc.
# Example: docker run --cpus 1 --memory 256m --pids-limit 50 ...