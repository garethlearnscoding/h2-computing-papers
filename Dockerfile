# Use a minimal Python base image
FROM python:3-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user and group
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Set the working directory
WORKDIR /testcases

# Copy the application code
COPY ./tester .

# Change ownership of the application files
RUN chown -R appuser:appgroup /testcases

ENV PATH="$PATH:/home/appuser/.local/bin"

# Ensure the test runner script is executable
RUN chmod +x ./tester

# Use a non-root user to run the application
USER appuser

# Set the default command arguments for the tester
CMD ["nj67-papers/testcases", "nj67-papers/testcases"]

# Note: Resource limits (CPU, memory, pids) should be set at container runtime
# using docker run flags such as --cpus, --memory, --pids-limit, etc.
# Example: docker run --cpus 1 --memory 256m --pids-limit 50 ...