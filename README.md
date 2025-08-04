# Safe Python Script Execution API

A secure, cloud-based API that allows users to execute Python scripts in a sandboxed environment. 
---

## Usage

### 1. Running Locally with Docker

Build the Docker image:

```bash
docker build -t takehome-stacksync .
```

Run the container:

```bash
docker run -p 8080:8080 takehome-stacksync
```
---



#### Example Request

```bash
curl -X POST https://stacksync-python-api-102239670054.us-west1.run.app/execute \
   -H "Content-Type: application/json" \
  -d '{"script": "def main():\n    print(\"hello\")\n    return {\"foo\": \"bar\"}"}'
```

#### Example Response

```json
{
  "result":{
    "foo":"bar"
    },
    "stdout":"hello"
  }
```

---

## Requirements

- Docker
- (For deployment) Google Cloud account with Cloud Run enabled


---

## Development

- Python 3.11
- Flask
- nsjail

---

## Example Scripts

```python
def main():
    import numpy as np
    arr = np.array([1, 2, 3])
    print("Array:", arr)
    return {"sum": int(arr.sum())}
```

---

## Submission

- The GitHub repository URL (public or shared with RubenB1)
- The Google Cloud Run service URL
- 2.5 hours

---

## References

- [nsjail Documentation](https://nsjail.dev/)
- [Google Cloud Run](https://cloud.google.com/run)