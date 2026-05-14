# How to Test Models

If you encounter issues such as model inaccessibility or access errors, you can follow the steps below to troubleshoot:

## First, Test if the Model is Working

Use the command below to test whether your model API is functioning properly. (Note: this test targets the model service itself and is unrelated to CoStrict. Please use the correct model address.)

In the following command, replace `http://ip:port/v1/chat/completions` with the actual model address, replace `Bearer ***` with the actual authentication header, and replace `GLM-4.5-FP8` with the actual model name. Run the test and verify the model produces a normal output to ensure it is working correctly.

```bash
curl -X POST "http://ip:port/v1/chat/completions" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer ***" \
--data-binary '{
  "model": "GLM-4.5-FP8",
  "messages": [
    {"role": "user", "content": "Hello, how are you?"}
  ],
  "max_tokens": 50,
  "temperature": 0.7
}'
```

## Client Test

This test only checks the model list and targets the CoStrict service interface. It is related to the CoStrict service and requires the CoStrict service to be deployed and configured with models before testing.

Open a browser and navigate to `${BASE_URL}/ai-gateway/api/v1/models`. Replace `${BASE_URL}` with the CoStrict service address (BaseUrl from the output) and verify that the model list loads correctly.

## Service Test

Used to test whether the CoStrict service can access the model service.

Navigate to the deployment directory and run the following commands:

```bash
# Enter the model-proxy container
docker compose exec -it model-proxy sh

# Use the wget command. Replace Kimi-K2-Moonshot with the model ID, which is the ID configured in Nacos.
wget http://127.0.0.1:8080/model-test/Kimi-K2-Moonshot?stream=false -O test.txt
cat test.txt
```
